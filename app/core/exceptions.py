class AppException(Exception):
    pass


class NotFoundError(AppException):
    pass


class EmailAlreadyExistsError(AppException):
    pass


class InvalidCredentialsError(AppException):
    pass


class UserSuspendedError(AppException):
    pass


class ForbiddenActionError(AppException):
    pass


class InvalidStateTransitionError(AppException):
    pass


class InvalidOrderError(AppException):
    pass


class IdempotencyConflictError(AppException):
    pass
