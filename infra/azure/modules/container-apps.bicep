// Aplicações de bootstrap do MVP no Azure Container Apps (fase 2 do deploy, Sprint 0).
//
// - api:     backend FastAPI; ingress INTERNO (sem endereço público); sondas /health e /ready.
// - web:     Nginx + SPA; ingress externo HTTPS; página pública /status.
// - migrate: job manual que aplica as migrations (Alembic) com a imagem do backend.
//
// Sem regras de negócio nesta sprint. Sem autenticação configurada no ambiente, a API
// responde 401 para tudo que não é health check (a autenticação DEV é proibida fora de
// APP_ENV=local). O login Entra (Easy Auth + App Roles) é ligado na Sprint 1 (ADR-006).
param resourcePrefix string
param environment string
param location string
param tags object
param environmentId string
param apiIdentityId string
param apiIdentityClientId string
param webIdentityId string
param registryLoginServer string
param keyVaultUri string
param postgresFqdn string
param postgresAdminLogin string
param postgresDatabase string
param storageBlobEndpoint string
param appInsightsConnectionString string
@minLength(1)
param imageTag string

var apiName = 'ca-${resourcePrefix}-api-${environment}'
var webName = 'ca-${resourcePrefix}-web-${environment}'
var jobName = 'caj-${resourcePrefix}-migrate-${environment}'
var backendImage = '${registryLoginServer}/guardiao-backend:${imageTag}'
var frontendImage = '${registryLoginServer}/guardiao-frontend:${imageTag}'
var workloadProfileName = 'Consumption'

var dbSecrets = [
  {
    name: 'postgres-password'
    keyVaultUrl: '${keyVaultUri}secrets/postgres-admin-password'
    identity: apiIdentityId
  }
]

var backendEnv = [
  { name: 'APP_ENV', value: environment }
  { name: 'LOG_FORMAT', value: 'json' }
  { name: 'POSTGRES_HOST', value: postgresFqdn }
  { name: 'POSTGRES_PORT', value: '5432' }
  { name: 'POSTGRES_DB', value: postgresDatabase }
  { name: 'POSTGRES_USER', value: postgresAdminLogin }
  { name: 'POSTGRES_PASSWORD', secretRef: 'postgres-password' }
  { name: 'POSTGRES_SSLMODE', value: 'require' }
  { name: 'AZURE_CLIENT_ID', value: apiIdentityClientId }
  { name: 'AZURE_STORAGE_BLOB_ENDPOINT', value: storageBlobEndpoint }
  { name: 'APPLICATIONINSIGHTS_CONNECTION_STRING', value: appInsightsConnectionString }
]

resource api 'Microsoft.App/containerApps@2026-01-01' = {
  name: apiName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${apiIdentityId}': {} }
  }
  properties: {
    environmentId: environmentId
    workloadProfileName: workloadProfileName
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: false // acessível apenas dentro do ambiente (pelo web)
        targetPort: 8000
        transport: 'http'
        allowInsecure: true // HTTP interno web → api; o ambiente criptografa o tráfego entre apps
      }
      registries: [{ server: registryLoginServer, identity: apiIdentityId }]
      secrets: dbSecrets
    }
    template: {
      containers: [
        {
          name: 'api'
          image: backendImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: backendEnv
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/health', port: 8000 }
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: { path: '/ready', port: 8000 }
              periodSeconds: 15
              failureThreshold: 3
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          { name: 'http', http: { metadata: { concurrentRequests: '20' } } }
        ]
      }
    }
  }
}

resource web 'Microsoft.App/containerApps@2026-01-01' = {
  name: webName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${webIdentityId}': {} }
  }
  properties: {
    environmentId: environmentId
    workloadProfileName: workloadProfileName
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: 8080
        transport: 'auto'
        allowInsecure: false // HTTP é redirecionado para HTTPS
      }
      registries: [{ server: registryLoginServer, identity: webIdentityId }]
    }
    template: {
      containers: [
        {
          name: 'web'
          image: frontendImage
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: [
            // FQDN interno completo: o resolver do Nginx não aplica os domínios de busca
            // do /etc/resolv.conf, então o nome curto da aplicação não resolveria.
            { name: 'BACKEND_UPSTREAM', value: 'http://${api.properties.configuration.ingress.fqdn}' }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: { path: '/healthz', port: 8080 }
              periodSeconds: 30
            }
          ]
        }
      ]
      scale: {
        minReplicas: 0
        maxReplicas: 1
        rules: [
          { name: 'http', http: { metadata: { concurrentRequests: '50' } } }
        ]
      }
    }
  }
  dependsOn: [api]
}

resource migrate 'Microsoft.App/jobs@2026-01-01' = {
  name: jobName
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: { '${apiIdentityId}': {} }
  }
  properties: {
    environmentId: environmentId
    workloadProfileName: workloadProfileName
    configuration: {
      triggerType: 'Manual'
      replicaTimeout: 900
      replicaRetryLimit: 0
      manualTriggerConfig: { parallelism: 1, replicaCompletionCount: 1 }
      registries: [{ server: registryLoginServer, identity: apiIdentityId }]
      secrets: dbSecrets
    }
    template: {
      containers: [
        {
          name: 'migrate'
          image: backendImage
          command: ['alembic', 'upgrade', 'head']
          resources: { cpu: json('0.25'), memory: '0.5Gi' }
          env: backendEnv
        }
      ]
    }
  }
}

output webFqdn string = web.properties.configuration.ingress.fqdn
output apiName string = api.name
output migrateJobName string = migrate.name
