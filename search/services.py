import logging
import multiprocessing
import uuid
from typing import Any

from rx import Observable
from rx.concurrency import ThreadPoolScheduler

from search.mappers import to_seeya, from_seeya
from search.models import SearchRequest
from seeya.models import SeeyaSearchRequest, SeeyaSearchResponse
from seeya.services import Client

logger = logging.getLogger(__name__)
optimal_thread_count = multiprocessing.cpu_count() + 1
scheduler = ThreadPoolScheduler(optimal_thread_count)


class SearchService(object):

    @property
    def providers(self):
        return [
            'petas', 'figame', 'kiwi', 'travel2be', 'travelgenio'
        ]

    def perform(self, request: SearchRequest):
        seeya_request = to_seeya(request)
        return Observable.from_iterable(self.providers) \
            .flat_map(lambda x: self.prepare(x, seeya_request)) \
            .to_blocking() \
            .to_iterable()

    def prepare(self, provider: str, request: SearchRequest) -> Any:
        request = request.copy(method=provider, transactionId=uuid.uuid4())
        return Observable.just(request).subscribe_on(scheduler).map(self.send)

    @classmethod
    def send(cls, request: SeeyaSearchRequest) -> SeeyaSearchResponse:
        response = Client.send(request, SeeyaSearchResponse)
        return from_seeya(response)
