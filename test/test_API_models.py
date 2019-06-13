import unittest
from sanic_app import WenetApp
import config


class APIModelsTestCase(unittest.TestCase):
    def setUp(self):
        self._app = WenetApp("test wenet")._app

    def test_simple_lda_exist(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION + "/models/"
        )
        self.assertIn("SimpleLDA", response.json)

    def test_simple_bow_exist(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION + "/models/"
        )
        self.assertIn("SimpleBOW", response.json)
