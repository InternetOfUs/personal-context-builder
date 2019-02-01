from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.response import json

app = Sanic("wenet_personal_context_builder")


class SimpleView(HTTPMethodView):
    def post(self, request):
        return json({"stay": "points"})


app.add_route(SimpleView.as_view(), "/staypoints/")


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000)
