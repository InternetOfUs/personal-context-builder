""" module with wenet exceptions
"""
from sanic.response import text
import config


async def ignore_404s(request, exception):
    return text(f"404 - no route to {format(request.url)}", status=404)


async def server_error(request, exception):
    return text(
        f"500 - sorry, we have issue with our application\nplease contact {config.MAINTENER}"
    )
