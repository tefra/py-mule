import logging
import time
from codecs import open
from os import makedirs
from os.path import isdir

from pkg_resources import resource_filename
from python3_gearman import GearmanClient

from mule.models import Serializable
from seeya.models import SeeyaRequest

logger = logging.getLogger(__name__)


class SeeyaClient:
    QUEUE = "seeya_webservice"

    @classmethod
    def send(cls, request: SeeyaRequest, clazz: Serializable.__class__):
        try:
            client = GearmanClient(["localhost:4730"])
            workload = request.to_json()
            response = client.submit_job(cls.QUEUE, workload, background=False)
            cls.log_conversation(request, response.result)
            return clazz.from_json(response.result)
        finally:
            client.shutdown()

    @classmethod
    def log_conversation(cls, request: SeeyaRequest, response: str):
        try:
            now = int(time.time() * 1000)
            provider = request.provider
            transaction = request.transactionId
            method = request.method
            dir = resource_filename(__name__, "data/logs/{}".format(provider))

            if not isdir(dir):
                makedirs(dir)

            path = "{}/{}_{}_{}".format(dir, now, method, transaction)
            req_path = "{}_{}.json".format(path, "request")
            res_path = "{}_{}.json".format(path, "response")

            with open(req_path, encoding="utf-8", mode="w") as f:
                f.write(request.to_json())

            with open(res_path, encoding="utf-8", mode="w") as f:
                f.write(response)
        except Exception as e:
            logger.exception(repr(e))
