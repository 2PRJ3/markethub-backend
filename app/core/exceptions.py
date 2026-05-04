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
