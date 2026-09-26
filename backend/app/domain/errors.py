"""Erros de aplicação com códigos estáveis e mensagens em pt-BR.

O catálogo de códigos está documentado em ``docs/error-codes.md``. Mensagens nunca contêm
detalhes técnicos internos (SQL, caminhos, stack trace, segredos).
"""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    VALIDATION_ERROR = "GFB-0422"
    NOT_AUTHENTICATED = "GFB-0401"
    PERMISSION_DENIED = "GFB-0403"
    NOT_FOUND = "GFB-0404"
    CONFLICT = "GFB-0409"
    INTERNAL_ERROR = "GFB-0500"
    SERVICE_UNAVAILABLE = "GFB-0503"
    ORGANIZATION_NOT_INITIALIZED = "GFB-1001"
    INVALID_CONFIGURATION_VALUE = "GFB-1101"
    INVALID_MONETARY_VALUE = "GFB-1201"


class AppError(Exception):
    """Erro esperado da aplicação, seguro para exibir ao usuário."""

    code: ErrorCode = ErrorCode.INTERNAL_ERROR
    default_message: str = "Não foi possível concluir a operação."

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.default_message
        super().__init__(self.message)


class NotAuthenticatedError(AppError):
    code = ErrorCode.NOT_AUTHENTICATED
    default_message = "Autenticação necessária."


class PermissionDeniedError(AppError):
    code = ErrorCode.PERMISSION_DENIED
    default_message = "Você não tem permissão para executar esta operação."


class NotFoundError(AppError):
    code = ErrorCode.NOT_FOUND
    default_message = "Recurso não encontrado."


class ServiceUnavailableError(AppError):
    code = ErrorCode.SERVICE_UNAVAILABLE
    default_message = "Serviço temporariamente indisponível. Tente novamente em instantes."


class OrganizationNotInitializedError(AppError):
    code = ErrorCode.ORGANIZATION_NOT_INITIALIZED
    default_message = (
        "Nenhuma organização configurada. Execute a inicialização do ambiente "
        "(python -m app.cli bootstrap)."
    )


class InvalidConfigurationValueError(AppError):
    code = ErrorCode.INVALID_CONFIGURATION_VALUE
    default_message = "Valor de configuração inválido."


class InvalidMonetaryValueError(AppError):
    code = ErrorCode.INVALID_MONETARY_VALUE
    default_message = "Valor monetário inválido."
