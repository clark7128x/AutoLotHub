class BusinessLogicError(Exception):
    """Raised when a business rule is violated (e.g. invalid status transition).

    This is distinct from ValueError("... not found") which indicates a missing entity.
    Handlers should map this to HTTP 400, while "not found" remains HTTP 404.
    """
