class MyPermobilException(Exception):
    """Permobil Exception. Generic Permobil Exception."""


class MyPermobilAPIException(MyPermobilException):
    """Permobil Exception. Exception raised when the API returns an error."""


class MyPermobilConnectionException(MyPermobilException):
    """Permobil Exception. Exception raised when the AIOHTTP."""


class MyPermobilClientException(MyPermobilException):
    """Permobil Exception. Exception raised when the Client is used incorrectly."""


class MyPermobilEulaException(MyPermobilException):
    """Permobil Exception. Exception raised when the client has not accepted the EULA."""


class MyPermobilNoProductException(MyPermobilException):
    """Permobil Exception. Exception raised when the client has no product linked to their account."""
