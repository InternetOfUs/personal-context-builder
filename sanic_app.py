from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.response import json
from wenet_models import LocationPoint
from wenet_algo import estimate_stay_points
import config
import datetime

app = Sanic(config.DEFAULT_APP_NAME)


class SimpleView(HTTPMethodView):
    def post(self, request):
        req_json = request.json
        if req_json is None:
            return json({})

        if "locations" not in req_json:
            return json({})
        datetime_format = config.DEFAULT_DATETIME_FORMAT
        if "datetime_format" in req_json:
            datetime_format = req_json["datetime_format"]
        locations = []
        for location_dict in req_json["locations"]:
            location = LocationPoint(
                datetime.datetime.strptime(location_dict["pts_t"], datetime_format),
                location_dict["lat"],
                location_dict["lng"],
            )
            locations.append(location)
        res = estimate_stay_points(locations, time_min_ms=-1)
        res = [s.__dict__ for s in res]
        return json({"staypoints": res})


app.add_route(SimpleView.as_view(), "/staypoints/")


if __name__ == "__main__":  # pragma: no cover
    app.run(host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT)
