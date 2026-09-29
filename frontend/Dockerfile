# SPA estática servida por Nginx sem privilégios; /api/ é encaminhado ao backend.

FROM node:24.21.0-alpine3.24 AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN --mount=type=cache,target=/root/.npm npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.30.5-alpine3.24 AS runtime
RUN rm -f /etc/nginx/conf.d/default.conf
COPY nginx/nginx.conf /etc/nginx/nginx.conf
COPY nginx/security-headers.conf /etc/nginx/security-headers.conf
COPY nginx/templates/ /etc/nginx/templates/
COPY --chmod=0755 nginx/docker-entrypoint.d/15-resolver.sh /docker-entrypoint.d/15-resolver.sh
COPY --from=build /app/dist /usr/share/nginx/html
# Destino da API e saída dos templates (gravável mesmo com sistema de arquivos read-only + tmpfs).
ENV BACKEND_UPSTREAM=http://backend:8000 \
    NGINX_ENVSUBST_OUTPUT_DIR=/tmp/nginx
USER nginx
EXPOSE 8080
HEALTHCHECK --interval=15s --timeout=3s --start-period=10s --retries=3 \
    CMD ["wget", "-qO-", "http://127.0.0.1:8080/healthz"]
CMD ["nginx", "-g", "daemon off;"]
