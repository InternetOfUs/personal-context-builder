import unittest
from personal_context_builder.sanic_app import WenetApp
from personal_context_builder import config
from uuid import uuid4


class APIModelsTestCase(unittest.TestCase):
    def setUp(self):
        self._app = WenetApp(f"test wenet API models {uuid4()}")._app

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
