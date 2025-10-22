class ApplicationError(Exception):
    """
    Base exception for application layer errors.
    """

    pass


class UserAlreadyExistsError(ApplicationError):
    """
    Raised when attempting to create a user with an email that already exists.
    """

    pass


class InvalidCredentialsError(ApplicationError):
    """
    Raised when login credentials are invalid.
    """

    pass


class VerificationError(ApplicationError):
    """
    Raised when email verification fails.
    """

    pass


class UserNotFoundError(ApplicationError):
    """
    Raised when a requested user is not found.
    """

    pass


class ForbiddenError(ApplicationError):
    """
    Raised when user doesn't have permission to perform an action.
    """

    pass
