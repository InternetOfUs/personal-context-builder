import unittest
import json
import datetime
from sanic_app import app


class StayPointAPITestCase(unittest.TestCase):
    def test_status_code_200(self):
        _, response = app.test_client.post("/staypoints/")
        self.assertEqual(response.status, 200)

    def test_return_empty_answer(self):
        _, response = app.test_client.post("/staypoints/")
        self.assertEqual(response.json, {})

    def test_one_stay_points(self):
        data = {
            "locations": [
                {"pts_t": str(datetime.datetime.now()), "lat": 1, "lng": 2},
                {"pts_t": str(datetime.datetime.now()), "lat": 1, "lng": 2},
            ]
        }
        _, response = app.test_client.post("/staypoints/", data=json.dumps(data))
        self.assertEqual(len(response.json.get("staypoints")), 1)

    def test_without_locations(self):
        data = {}
        _, response = app.test_client.post("/staypoints/", data=json.dumps(data))
        self.assertEqual(response.json, {})

    def test_empty_locations(self):
        data = {"locations": []}
        _, response = app.test_client.post("/staypoints/", data=json.dumps(data))
        self.assertEqual(len(response.json.get("staypoints")), 0)

    def test_custom_datetime_format(self):
        datetime_format = "%A, %d. %B %Y %I:%M%p"
        t1 = datetime.datetime.now().strftime(datetime_format)
        t2 = datetime.datetime.now().strftime(datetime_format)
        data = {
            "locations": [
                {"pts_t": t1, "lat": 1, "lng": 2},
                {"pts_t": t2, "lat": 1, "lng": 2},
            ],
            "datetime_format": datetime_format,
        }
        _, response = app.test_client.post("/staypoints/", data=json.dumps(data))
        self.assertEqual(len(response.json.get("staypoints")), 1)


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
