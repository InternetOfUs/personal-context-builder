""" module with wenet exceptions

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,

"""

from personal_context_builder import config
from personal_context_builder.wenet_logger import create_logger

_LOGGER = create_logger(__name__)


class WenetError(Exception):
    """Generic winet exception"""

    def __init__(self, message: str = "Generic Wenet Error"):
        super().__init__(message)


class WenetUpdateProfileManagerError(WenetError):
    """Can't update the profile manager"""

    def __init__(self, message: str = "Fail to update profile manager"):
        super().__init__(message)


class WenetStreamBaseLocationsError(WenetError):
    """Fail to retreive any locations from streambase"""

    def __init__(self, message: str = "Fail to retreive any locations from streambase"):
        super().__init__(message)


class WenetStreamBaseLocationsParsingError(WenetError):
    """Fail to parse locations json from streambase"""

    def __init__(self, message: str = "Fail to parse locations json from streambase"):
        super().__init__(message)


class SemanticRoutinesComputationError(WenetError):
    """Fail to compute semantic routines"""

    def __init__(self, message: str = "Fail to compute semantic routines"):
        super().__init__(message)
