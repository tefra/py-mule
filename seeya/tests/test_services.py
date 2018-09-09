import os
from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

from attr import attrs
from pkg_resources import resource_filename
from python3_gearman import GearmanClient
from python3_gearman.errors import ServerUnavailable

from mule.models import Serializable
from seeya.models import SeeyaRequest
from seeya.services import SeeyaClient


@attrs(auto_attribs=True)
class SeeyaTestResponse(Serializable):
    foo: str


@attrs(auto_attribs=True)
class GearmanJobRequest:
    result: dict


class SeeyaClientTestCase(TestCase):
    def setUp(self):
        self.client = SeeyaClient()

    @patch.object(SeeyaClient, "log_conversation")
    @patch.object(GearmanClient, "shutdown")
    @patch.object(GearmanClient, "submit_job")
    @patch.object(GearmanClient, "__init__", return_value=None)
    def test_send(self, client_init, submit, shutdown, log_conversation):
        job = GearmanJobRequest(result='{"foo": "bar"}')
        submit.return_value = job
        request = SeeyaRequest(transactionId="1234")

        expected = SeeyaTestResponse("bar")
        self.assertEqual(
            expected, self.client.send(request, SeeyaTestResponse)
        )

        client_init.assert_called_once_with(["localhost:4730"])
        submit.assert_called_once_with(
            "seeya_webservice", request.to_json(), background=False
        )
        log_conversation.assert_called_once_with(request, job.result)
        shutdown.assert_called_once()

    @patch.object(GearmanClient, "shutdown")
    @patch.object(GearmanClient, "submit_job", side_effect=ServerUnavailable)
    @patch.object(GearmanClient, "__init__", return_value=None)
    def test_send_with_side_effect(self, client_init, submit, shutdown):
        request = SeeyaRequest(transactionId="1234")
        with self.assertRaises(ServerUnavailable):
            self.client.send(request, SeeyaTestResponse)

        client_init.assert_called_once_with(["localhost:4730"])
        shutdown.assert_called_once()

    @patch("time.time", MagicMock(return_value=12345))
    def test_log_conversation(self):
        request = SeeyaRequest(transactionId="1234")
        request.MODAL = "train"
        request.ACTION = "fly"
        request.provider = "python"
        response = '{"foo": "bar"}'

        path = resource_filename("seeya", "data/logs/python/")
        filepath = "{}{}".format(path, "12345000_train.python.fly_1234")
        req_path = "{}_{}.json".format(filepath, "request")
        res_path = "{}_{}.json".format(filepath, "response")

        try:
            self.client.log_conversation(request, response)
            with open(req_path, mode="r") as f:
                self.assertEqual(request.to_json(), f.read())

            with open(res_path, mode="r") as f:
                self.assertEqual(response, f.read())
        finally:
            os.remove(req_path)
            os.remove(res_path)
            os.rmdir(path)

    @patch("time.time", Mock(side_effect=Exception("time went wrong")))
    @patch("seeya.services.logger.exception")
    def test_log_conversation_logs_errors(self, logger):
        self.client.log_conversation(None, None)

        logger.assert_called_once_with("Exception('time went wrong',)")
