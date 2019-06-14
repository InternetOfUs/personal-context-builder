""" module with wenet exceptions
"""
from sanic.response import text
from wenet_pcb.wenet_logger import create_logger
from wenet_pcb import config

_LOGGER = create_logger(__name__)


async def ignore_404s(request, exception):
    return text(f"404 - no route to {format(request.url)}", status=404)


async def server_error(request, exception):
    _LOGGER.error(f"error 500 on {request.url} - {str(exception)}")
    return text(
        f"500 - sorry, we have issue with our applications\nplease contact {config.MAINTENER}",
        status=500,
    )

