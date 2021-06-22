import unittest
from personal_context_builder.sanic_app import WenetApp
from personal_context_builder.wenet_cli_entrypoint import update, train
from personal_context_builder import config
from uuid import uuid4

train(is_mock=True)
update(is_mock=True)


class APICompareRoutinesTestCase(unittest.TestCase):
    def setUp(self):
<<<<<<< HEAD
        self._app = WenetApp(uuid4(), is_mock=True)._app
=======
        self._app = WenetApp(f"test wenet compare routine {uuid4()}", is_mock=True)._app
>>>>>>> dee8273acc4b3913aa5d293865cda09656ccf7f7

    def test_order(self):
        _, response = self._app.test_client.get(
            config.DEFAULT_VIRTUAL_HOST_LOCATION
            + "/compare_routines/mock_user_1/SimpleLDA:PipelineBOW/?users=mock_user_2&users=mock_user_3"
        )
        res = response.json
        res_list = list(res.items())
        sorted_res = sorted(res_list, key=lambda x: -x[1])
        self.assertTrue(res_list == sorted_res)
