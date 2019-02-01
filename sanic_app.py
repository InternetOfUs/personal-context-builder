from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.response import json
from wenet_models import LocationPoint
from wenet_algo import estimate_stay_points
import config
import datetime

app = Sanic(config.DEFAULT_APP_NAME)


def get_field_if_exist(container_dict, field, default_value):
    if field not in container_dict:
        return default_value
    else:
        return container_dict[field]


class SimpleView(HTTPMethodView):
    def post(self, request):
        req_json = request.json
        if req_json is None:
            return json({})

        if "locations" not in req_json:
            return json({})
        datetime_format = get_field_if_exist(
            req_json, "datetime_format", config.DEFAULT_DATETIME_FORMAT
        )
        time_max_ms = get_field_if_exist(
            req_json, "time_max_ms", config.DEFAULT_STAYPOINTS_TIME_MAX_MS
        )
        time_min_ms = get_field_if_exist(
            req_json, "time_min_ms", config.DEFAULT_STAYPOINTS_TIME_MIN_MS
        )
        distance_max_m = get_field_if_exist(
            req_json, "distance_max_m", config.DEFAULT_STAYPOINTS_DISTANCE_MAX_M
        )
        locations = []
        for location_dict in req_json["locations"]:
            location = LocationPoint(
                datetime.datetime.strptime(location_dict["pts_t"], datetime_format),
                location_dict["lat"],
                location_dict["lng"],
            )
            locations.append(location)
        res = estimate_stay_points(
            locations,
            time_min_ms=time_min_ms,
            time_max_ms=time_max_ms,
            distance_max_m=distance_max_m,
        )
        res = [s.__dict__ for s in res]
        for p in res:
            p['_t_start'] = p['_t_start'].strftime(datetime_format)
            p['_t_stop'] = p['_t_stop'].strftime(datetime_format)
        return json({"staypoints": res})


app.add_route(SimpleView.as_view(), "/staypoints/")


if __name__ == "__main__":  # pragma: no cover
    app.run(host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT)
