""" Test for the API that touch the routines

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""
import unittest
from uuid import uuid4

from personal_context_builder import config
from personal_context_builder.sanic_app import WenetApp
from personal_context_builder.wenet_cli_entrypoint import train, update

train(is_mock=True)
update(is_mock=True)


class APIRoutinesTestCase(unittest.TestCase):
    def setUp(self):
        self._app = WenetApp(str(uuid4()), is_mock=True)._app

    # def test_simple_lda_exist(self):
    #     _, response = self._app.test_client.get(
    #         config.PCB_VIRTUAL_HOST_LOCATION + "/routines/"
    #     )
    #     self.assertIn("SimpleLDA:PipelineBOW", response.json)

    def test_simple_lda_not_exist(self):
        _, response = self._app.test_client.get(
            config.PCB_VIRTUAL_HOST_LOCATION + "/routines/?models=SimplePOW:PipelineBOW"
        )
        self.assertNotIn("SimpleLDA:PipelineBOW", response.json)

    # def test_mock_user_1(self):
    #     _, response = self._app.test_client.get(
    #         config.PCB_VIRTUAL_HOST_LOCATION + "/routines/"
    #     )
    #     self.assertIn("mock_user_1", response.json.get("SimpleLDA:PipelineBOW"))

    def test_not_mock_user_1(self):
        _, response = self._app.test_client.get(
            config.PCB_VIRTUAL_HOST_LOCATION + "/routines/mock_user_1/"
        )
        self.assertNotIn("mock_user_2", response.json.get("SimpleLDA:PipelineBOW"))

    def test_mock_user_1_with_mock_user_1(self):
        _, response = self._app.test_client.get(
            config.PCB_VIRTUAL_HOST_LOCATION + "/routines/mock_user_1/"
        )
        self.assertIn("mock_user_1", response.json.get("SimpleLDA:PipelineBOW"))
