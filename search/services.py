import logging
import uuid
from typing import Any

from rx.concurrency import thread_pool_scheduler as scheduler
from rx.core import Observable

from search.managers import ResourceManager
from search.mappers import SearchResponseMapper, SeeyaSearchRequestMapper
from search.models import SearchRequest, SearchResponse
from seeya.models import SeeyaSearchRequest, SeeyaSearchResponse
from seeya.services import SeeyaClient

logger = logging.getLogger(__name__)
resources = ResourceManager()


class SearchService:
    @property
    def providers(self):
        return ["petas", "figame", "kiwi", "travel2be", "travelgenio"]

    def perform(self, request: SearchRequest):
        seeya_request = SeeyaSearchRequestMapper().map(request)
        return (
            Observable.from_iterable(self.providers)
            .flat_map(lambda x: self.prepare(x, seeya_request))
            .to_blocking()
            .to_iterable()
        )

    def prepare(self, provider: str, request: SeeyaSearchRequest) -> Any:
        request = request.copy(transactionId=uuid.uuid4())
        request.provider = provider
        return Observable.just(request).subscribe_on(scheduler).map(self.send)

    @classmethod
    def send(cls, request: SeeyaSearchRequest) -> SearchResponse:
        result = SeeyaClient.send(request, SeeyaSearchResponse)
        response = SearchResponseMapper(request).map(result)
        resources.enrich(response)
        return response
