import unittest
from personal_context_builder.sanic_app import WenetApp
from personal_context_builder.wenet_cli_entrypoint import update, train
from personal_context_builder import config

train(is_mock=True)
update(is_mock=True)


class APIRoutinesTestCase(unittest.TestCase):
    def setUp(self):
        self._app = WenetApp("test wenet", is_mock=True)._app

    def test_simple_lda_exist(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION + "/routines/"
        )
        self.assertIn("SimpleLDA:PipelineBOW", response.json)

    def test_simple_lda_not_exist(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION
            + "/routines/?models=SimplePOW:PipelineBOW"
        )
        self.assertNotIn("SimpleLDA:PipelineBOW", response.json)

    def test_mock_user_1(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION + "/routines/"
        )
        self.assertIn("mock_user_1", response.json.get("SimpleLDA:PipelineBOW"))

    def test_not_mock_user_1(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION + "/routines/mock_user_1/"
        )
        self.assertNotIn("mock_user_2", response.json.get("SimpleLDA:PipelineBOW"))

    def test_mock_user_1_with_mock_user_1(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION + "/routines/mock_user_1/"
        )
        self.assertIn("mock_user_1", response.json.get("SimpleLDA:PipelineBOW"))
