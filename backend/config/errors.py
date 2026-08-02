"""The public API error catalogue and the single DRF exception boundary."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any


class ApiErrorCode(StrEnum):
    """Codes published in HotelAppPLAN.md section 3 and the OpenAPI schema."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    STAY_WINDOW_INVALID = "STAY_WINDOW_INVALID"
    NOT_AUTHENTICATED = "NOT_AUTHENTICATED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    NOT_FOUND = "NOT_FOUND"
    ROOM_UNAVAILABLE = "ROOM_UNAVAILABLE"
    PRICE_CHANGED = "PRICE_CHANGED"
    TRANSITION_NOT_ALLOWED = "TRANSITION_NOT_ALLOWED"
    PAYMENT_WINDOW_EXPIRED = "PAYMENT_WINDOW_EXPIRED"
    CANCELLATION_WINDOW_PASSED = "CANCELLATION_WINDOW_PASSED"


@dataclass(frozen=True)
class ErrorDefinition:
    status_code: int
    message: str


# Keep every public code, its status and its fallback message together. Domain
# modules raise DomainError; no view constructs this envelope directly.
ERROR_CATALOG: dict[ApiErrorCode, ErrorDefinition] = {
    ApiErrorCode.VALIDATION_ERROR: ErrorDefinition(400, "Некорректные данные запроса."),
    ApiErrorCode.STAY_WINDOW_INVALID: ErrorDefinition(
        400, "Даты проживания не соответствуют правилам."
    ),
    ApiErrorCode.NOT_AUTHENTICATED: ErrorDefinition(401, "Требуется аутентификация."),
    ApiErrorCode.PERMISSION_DENIED: ErrorDefinition(
        403, "Недостаточно прав для этого действия."
    ),
    ApiErrorCode.NOT_FOUND: ErrorDefinition(404, "Объект не найден."),
    ApiErrorCode.ROOM_UNAVAILABLE: ErrorDefinition(
        409, "На указанный период нет свободных номеров."
    ),
    ApiErrorCode.PRICE_CHANGED: ErrorDefinition(
        409, "Цена изменилась; получите новую котировку."
    ),
    ApiErrorCode.TRANSITION_NOT_ALLOWED: ErrorDefinition(409, "Переход статуса недоступен."),
    ApiErrorCode.PAYMENT_WINDOW_EXPIRED: ErrorDefinition(409, "Срок demo-оплаты истёк."),
    ApiErrorCode.CANCELLATION_WINDOW_PASSED: ErrorDefinition(409, "Срок отмены брони истёк."),
}


class DomainError(Exception):
    """Exception raised by a domain owner and rendered only at the HTTP boundary."""

    def __init__(
        self,
        code: ApiErrorCode,
        *,
        message: str | None = None,
        errors: Any | None = None,
    ) -> None:
        self.code = code
        self.message = message or ERROR_CATALOG[code].message
        self.errors = errors
        super().__init__(self.message)


def _error_response(
    code: ApiErrorCode,
    *,
    errors: Any | None = None,
    message: str | None = None,
) -> Any:
    from rest_framework.response import Response

    definition = ERROR_CATALOG[code]
    return Response(
        {"code": code, "message": message or definition.message, "errors": errors},
        status=definition.status_code,
    )


def _drf_error_code(exc: Exception) -> ApiErrorCode:
    from django.http import Http404
    from rest_framework import exceptions

    if isinstance(exc, exceptions.ValidationError):
        return ApiErrorCode.VALIDATION_ERROR
    if isinstance(exc, exceptions.NotAuthenticated | exceptions.AuthenticationFailed):
        return ApiErrorCode.NOT_AUTHENTICATED
    if isinstance(exc, exceptions.PermissionDenied):
        return ApiErrorCode.PERMISSION_DENIED
    if isinstance(exc, exceptions.NotFound | Http404):
        return ApiErrorCode.NOT_FOUND
    return ApiErrorCode.VALIDATION_ERROR


def exception_handler(exc: Exception, context: dict[str, Any]) -> Any | None:
    """Map domain and DRF exceptions to the one documented error envelope."""

    from rest_framework.views import exception_handler as drf_exception_handler

    if isinstance(exc, DomainError):
        return _error_response(exc.code, errors=exc.errors, message=exc.message)

    response = drf_exception_handler(exc, context)
    if response is None:
        return None

    code = _drf_error_code(exc)
    errors = response.data if code is ApiErrorCode.VALIDATION_ERROR else None
    normalized = _error_response(code, errors=errors)
    for header, value in response.items():
        normalized[header] = value
    return normalized
