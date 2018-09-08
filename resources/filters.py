import re

from rest_framework.exceptions import ParseError
from rest_framework.filters import BaseFilterBackend


class MultiValueFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        value_regex = getattr(view, "lookup_value_regex", "(.*?)")
        p = re.compile("^{}$".format(value_regex))
        values = request.GET.getlist(view.lookup_field)
        values = [c.upper() for c in values if p.match(c)]

        if not values:
            raise ParseError()

        params = {"{}__in".format(view.lookup_field): values}
        queryset = queryset.filter(**params)

        return queryset
