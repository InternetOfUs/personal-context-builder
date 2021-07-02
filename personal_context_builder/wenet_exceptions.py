""" module with wenet exceptions

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""
from sanic.response import text

from personal_context_builder import config
from personal_context_builder.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class WenetError(Exception):
    """Generic winet exception"""

    def __init__(self, message="Generic Wenet Error"):
        super().__init__(message)


class WenetUpdateProfileManagerError(WenetError):
    """Can't update the profile manager"""

    def __init__(self, message="Fail to update profile manager"):
        super().__init__(message)


class WenetStreamBaseLocationsError(WenetError):
    """Fail to retreive any locations from streambase"""

    def __init__(self, message="Fail to retreive any locations from streambase"):
        super().__init__(message)


class WenetStreamBaseLocationsParsingError(WenetError):
    """Fail to parse locations json from streambase"""

    def __init__(self, message="Fail to parse locations json from streambase"):
        super().__init__(message)


class SemanticRoutinesComputationError(WenetError):
    """Fail to compute semantic routines"""

    def __init__(self, message="Fail to compute semantic routines"):
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
