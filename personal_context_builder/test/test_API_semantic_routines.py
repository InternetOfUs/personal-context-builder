""" Test for the API that touch the routines

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""
import unittest
from uuid import uuid4

from fastapi.testclient import TestClient  # type: ignore

from personal_context_builder import config
from personal_context_builder.wenet_cli_entrypoint import train, update
from personal_context_builder.wenet_fastapi_app import app


class APISemanticRoutinesTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_confidence_exist(self):
        response = self.client.get(
            config.PCB_VIRTUAL_HOST_LOCATION + "/semantic_routines/mock_user_1/2/1700/"
        )
        self.assertIn("confidence", response.json())
