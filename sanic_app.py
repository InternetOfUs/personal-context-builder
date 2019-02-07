from sanic import Sanic
from sanic.views import HTTPMethodView
from sanic.response import text
from sanic.response import json
from wenet_models import LocationPoint, StayPoint
from wenet_algo import (
    estimate_stay_points,
    estimate_stay_regions_a_day,
    estimate_stay_regions,
)
import config
import datetime
from pprint import pprint

app = Sanic(config.DEFAULT_APP_NAME)


def get_field_if_exist(container_dict, field, default_value):
    if field not in container_dict:
        return default_value
    else:
        return container_dict[field]


def is_staypoints_request_valide(req_json):
    return req_json is not None and "locations" in req_json


def is_stayregions_request_valide(req_json):
    return req_json is not None and "staypoints" in req_json


def retreive_staypoints_parameters(req_json):
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
    return datetime_format, time_max_ms, time_min_ms, distance_max_m


def retreive_stayregions_parameters(req_json):
    datetime_format = get_field_if_exist(
        req_json, "datetime_format", config.DEFAULT_DATETIME_FORMAT
    )
    distance_threshold_m = get_field_if_exist(
        req_json, "distance_threshold_m", config.DEFAULT_STAYREGION_DISTANCE_THRESHOLD_M
    )
    return datetime_format, distance_threshold_m


class StayPointsView(HTTPMethodView):
    def post(self, request):
        req_json = request.json
        if not is_staypoints_request_valide(req_json):
            return json({})
        datetime_format, time_max_ms, time_min_ms, distance_max_m = retreive_staypoints_parameters(
            req_json
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
            p["_t_start"] = p["_t_start"].strftime(datetime_format)
            p["_t_stop"] = p["_t_stop"].strftime(datetime_format)
        return json({"staypoints": res})


class StayRegionsOneDayView(HTTPMethodView):
    def post(self, request):
        req_json = request.json
        if not is_stayregions_request_valide(req_json):
            return json({})
        datetime_format, distance_threshold_m = retreive_stayregions_parameters(
            req_json
        )
        stay_points = []
        for stay_point_dict in req_json["staypoints"]:
            stay_point = StayPoint(
                datetime.datetime.strptime(
                    stay_point_dict["_t_start"], datetime_format
                ),
                datetime.datetime.strptime(stay_point_dict["_t_stop"], datetime_format),
                stay_point_dict["_lat"],
                stay_point_dict["_lng"],
            )
            stay_points.append(stay_point)

        res = estimate_stay_regions_a_day(stay_points, distance_threshold_m)
        res = [s.__dict__ for s in res]
        for p in res:
            p["_t_start"] = p["_t_start"].strftime(datetime_format)
            p["_t_stop"] = p["_t_stop"].strftime(datetime_format)
        return json({"stayregions": res})


class StayRegionsView(HTTPMethodView):
    def post(self, request):
        req_json = request.json
        if not is_stayregions_request_valide(req_json):
            return json({})
        datetime_format, distance_threshold_m = retreive_stayregions_parameters(
            req_json
        )
        stay_points = []
        for stay_point_dict in req_json["staypoints"]:
            stay_point = StayPoint(
                datetime.datetime.strptime(
                    stay_point_dict["_t_start"], datetime_format
                ),
                datetime.datetime.strptime(stay_point_dict["_t_stop"], datetime_format),
                stay_point_dict["_lat"],
                stay_point_dict["_lng"],
            )
            stay_points.append(stay_point)

        res = estimate_stay_regions(stay_points, distance_threshold_m)
        dict_res = {}
        for day, stayregions in res.items():
            stayregions = [s.__dict__ for s in stayregions]
            for p in stayregions:
                p["_t_start"] = p["_t_start"].strftime(datetime_format)
                p["_t_stop"] = p["_t_stop"].strftime(datetime_format)
            dict_res[day] = stayregions

        return json(dict_res)


app.add_route(StayPointsView.as_view(), "/staypoints/")
app.add_route(StayRegionsOneDayView.as_view(), "/stayregionsoneday/")
app.add_route(StayRegionsView.as_view(), "/stayregions/")


if __name__ == "__main__":  # pragma: no cover
    app.run(host=config.DEFAULT_APP_INTERFACE, port=config.DEFAULT_APP_PORT)
