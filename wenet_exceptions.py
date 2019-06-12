""" module with wenet exceptions
"""
from sanic.response import text


async def ignore_404s(request, exception):
    return text(f"404 - no route to {format(request.url)}", status=404)
