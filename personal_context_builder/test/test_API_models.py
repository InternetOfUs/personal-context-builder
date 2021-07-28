""" Test for the API that handle models

Copyright (c) 2021 Idiap Research Institute, https://www.idiap.ch/
Written by William Droz <william.droz@idiap.ch>,
"""
import unittest

from fastapi.testclient import TestClient  # type: ignore

from personal_context_builder import config
from personal_context_builder.wenet_fastapi_app import app


class APIModelsTestCase(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_simple_lda_exist(self):
        response = self.client.get(config.PCB_VIRTUAL_HOST_LOCATION + "/models/")
        self.assertIn("SimpleLDA", response.json())

    def test_simple_bow_exist(self):
        response = self.client.get(config.PCB_VIRTUAL_HOST_LOCATION + "/models/")
        self.assertIn("SimpleBOW", response.json())
