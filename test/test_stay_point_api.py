import unittest

from sanic_app import app


class StayPointAPITestCase(unittest.TestCase):
    def test_status_code_200(self):
        _, response = app.test_client.post("/staypoints/")
        self.assertEqual(response.status, 200)

    def test_return_stay_points(self):
        _, response = app.test_client.post("/staypoints/")
        self.assertEqual(response.json, {"stay": "points"})


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
