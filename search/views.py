import pickle
from base64 import b64decode, b64encode

from django.core.handlers.wsgi import WSGIRequest
from django import http
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from search.models import SearchRequest
from search.services import SearchService


def async(request: WSGIRequest):
    try:
        search_request = pickle.loads(b64decode(request.GET.get("id")))
        assert isinstance(search_request, SearchRequest) == True
    except Exception as e:
        return http.HttpResponseBadRequest(str(e))

    def response():
        search = SearchService()
        for message in search.perform(search_request):
            yield "event: message\ndata: {}\n\n".format(
                message.to_json(indent=None)
            )

    response = http.StreamingHttpResponse(
        response(), content_type="text/event-stream"
    )
    response["Cache-Control"] = "no-cache"
    return response


@csrf_exempt
def index(request: WSGIRequest):
    if request.method == "POST":
        try:
            search_request = SearchRequest.from_json(request.body)
            return http.HttpResponse(b64encode(pickle.dumps(search_request)))
        except ValueError as e:
            return http.HttpResponseBadRequest(str(e))

    data = {
        "currencies": ["EUR", "USD", "GBP"],
        "locales": ["el_GR", "en_US", "en_GB"],
        "markets": ["gr", "us", "uk"],
    }

    return render(request, "index.html", data)
