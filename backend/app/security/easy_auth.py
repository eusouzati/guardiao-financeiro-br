"""Identidade vinda do Easy Auth (autenticação integrada do Azure Container Apps).

O sidecar de autenticação faz o login no Microsoft Entra ID e injeta o cabeçalho
``X-MS-CLIENT-PRINCIPAL`` (JSON em base64 com as claims). O sidecar remove cabeçalhos
``X-MS-*`` enviados pelo cliente, e a API não tem endereço público: só recebe tráfego do
frontend, que passa pelo sidecar. Ainda assim, este módulo valida estrutura, tamanho e
tenant (defesa em profundidade). Ver ADR-006.

Perfis vêm das **App Roles** do registro da aplicação no Entra (ADMIN, ANALYST, APPROVER,
AUDITOR). Valores desconhecidos são ignorados; usuário sem perfil fica sem permissões.
"""

from __future__ import annotations

import base64
import binascii
import json
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from app.domain.errors import NotAuthenticatedError
from app.domain.identity import Role

PRINCIPAL_HEADER = "x-ms-client-principal"
IDP_HEADER = "x-ms-client-principal-idp"
MAX_HEADER_BYTES = 16 * 1024

_OID_CLAIMS = ("http://schemas.microsoft.com/identity/claims/objectidentifier", "oid")
_TENANT_CLAIMS = ("http://schemas.microsoft.com/identity/claims/tenantid", "tid")
_NAME_CLAIMS = ("name", "preferred_username")
_ROLE_CLAIMS = ("roles", "http://schemas.microsoft.com/ws/2008/06/identity/claims/role")


@dataclass(frozen=True, slots=True)
class EasyAuthIdentity:
    object_id: str
    tenant_id: str
    display_name: str
    roles: frozenset[Role]


def _claims(payload: Mapping[str, object]) -> list[tuple[str, str]]:
    raw = payload.get("claims")
    if not isinstance(raw, list):
        raise NotAuthenticatedError("Identidade inválida.")
    result: list[tuple[str, str]] = []
    for item in raw:
        if isinstance(item, dict):
            typ, val = item.get("typ"), item.get("val")
            if isinstance(typ, str) and isinstance(val, str):
                result.append((typ, val))
    return result


def _first(claims: Iterable[tuple[str, str]], names: tuple[str, ...]) -> str | None:
    for typ, val in claims:
        if typ in names and val:
            return val
    return None


def parse_client_principal(
    header_value: str | None, *, idp: str | None, expected_tenant_id: str
) -> EasyAuthIdentity:
    """Converte o cabeçalho do Easy Auth em identidade. Qualquer problema resulta em 401."""
    if not header_value:
        raise NotAuthenticatedError()
    if len(header_value) > MAX_HEADER_BYTES:
        raise NotAuthenticatedError("Identidade inválida.")
    if idp is not None and idp.lower() != "aad":
        raise NotAuthenticatedError("Provedor de identidade não suportado.")
    try:
        payload = json.loads(base64.b64decode(header_value, validate=True))
    except (binascii.Error, ValueError) as exc:
        raise NotAuthenticatedError("Identidade inválida.") from exc
    if not isinstance(payload, dict):
        raise NotAuthenticatedError("Identidade inválida.")

    claims = _claims(payload)
    object_id = _first(claims, _OID_CLAIMS)
    tenant_id = _first(claims, _TENANT_CLAIMS)
    if not object_id or not tenant_id:
        raise NotAuthenticatedError("Identidade incompleta.")
    if tenant_id.lower() != expected_tenant_id.lower():
        raise NotAuthenticatedError("Tenant não autorizado.")

    role_type = payload.get("role_typ")
    role_claims = (*_ROLE_CLAIMS, role_type) if isinstance(role_type, str) else _ROLE_CLAIMS
    valid = {r.value for r in Role}
    roles = frozenset(
        Role(val.upper()) for typ, val in claims if typ in role_claims and val.upper() in valid
    )
    return EasyAuthIdentity(
        object_id=object_id,
        tenant_id=tenant_id,
        display_name=_first(claims, _NAME_CLAIMS) or "Usuário",
        roles=roles,
    )
