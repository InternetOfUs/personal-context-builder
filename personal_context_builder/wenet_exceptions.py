""" module with wenet exceptions
"""
from sanic.response import text
from personal_context_builder.wenet_logger import create_logger
from personal_context_builder import config

_LOGGER = create_logger(__name__)


class WenetError(Exception):
    """ Generic winet exception
    """

    def __init__(self, message="Generic Wenet Error"):
        super().__init__(message)


class WenetUpdateProfileManagerError(WenetError):
    """ Can't update the profile manager
    """

    def __init__(self, message="Fail to update profile manager"):
        super().__init__(message)


async def ignore_404s(request, exception):
    error_code = 404
    return text(f"{error_code} - no route to {format(request.url)}", status=error_code)


async def server_error(request, exception):
    error_code = 500
    _LOGGER.error(f"error {error_code} on {request.url} - {str(exception)}")
    return text(
        f"{error_code} - sorry, we have issue with our applications\nplease contact {config.MAINTENER}",
        status=error_code,
    )
