/** Tipos das respostas da API /api/v1 (espelham os schemas Pydantic do backend). */

export interface ApiErrorBody {
  code: string;
  message: string;
  request_id: string | null;
  details: { field: string | null; message: string }[];
}

export interface Organization {
  id: string;
  legal_name: string;
  tax_id: string | null;
}

export interface Me {
  user_id: string;
  display_name: string;
  auth_method: 'DEV' | 'EASY_AUTH' | 'ENTRA_ID';
  roles: string[];
  permissions: string[];
  organization: Organization;
}

export type PolicyType = 'BOOLEAN' | 'INTEGER' | 'DECIMAL' | 'SEVERITY';

export interface Policy {
  key: string;
  label: string;
  description: string;
  type: PolicyType;
  unit: string | null;
  /** Decimais chegam como string (ADR-009). */
  value: boolean | number | string;
  default_value: boolean | number | string;
  allowed_values: string[];
  minimum: string | null;
  maximum: string | null;
  source: 'DEFAULT' | 'ORGANIZATION';
  version: number | null;
  changed_by: string | null;
  changed_at: string | null;
}

export interface ConfigurationResponse {
  items: Policy[];
}

export interface Readiness {
  status: 'ok' | 'unavailable';
  version: string;
  environment: string;
  database: 'ok' | 'unavailable';
  schema_revision: string | null;
}
