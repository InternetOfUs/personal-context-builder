import unittest
import json
from sanic_app import app


class StayPointAPITestCase(unittest.TestCase):
    def test_status_code_200(self):
        _, response = app.test_client.post("/staypoints/")
        self.assertEqual(response.status, 200)

    def test_return_empty_answer(self):
        _, response = app.test_client.post("/staypoints/")
        self.assertEqual(response.json, {})

    def test_one_stay_points(self):
        data = {"locations": [{"lat": 1, "lng": 2}, {"lat": 1, "lng": 2}]}
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


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
