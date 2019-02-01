from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.response import json
from wenet_models import LocationPoint
from wenet_algo import estimate_stay_points
import datetime

app = Sanic("wenet_personal_context_builder")


class SimpleView(HTTPMethodView):
    def post(self, request):
        req_json = request.json
        if req_json is None:
            return json({})

        if "locations" not in req_json:
            return json({})
        locations = []
        for location_dict in req_json["locations"]:
            location = LocationPoint(
                datetime.datetime.now(), location_dict["lat"], location_dict["lng"]
            )
            locations.append(location)
        res = estimate_stay_points(locations, time_min_ms=-1)
        res = [s.__dict__ for s in res]
        return json({"staypoints": res})


app.add_route(SimpleView.as_view(), "/staypoints/")


if __name__ == "__main__":  # pragma: no cover
    app.run(host="0.0.0.0", port=8000)
