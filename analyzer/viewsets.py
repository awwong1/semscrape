from django_elasticsearch_dsl_drf.constants import (
    LOOKUP_FILTER_TERMS,
    # LOOKUP_FILTER_RANGE,
    LOOKUP_FILTER_PREFIX,
    LOOKUP_FILTER_WILDCARD,
    LOOKUP_QUERY_IN,
    # LOOKUP_QUERY_GT,
    # LOOKUP_QUERY_GTE,
    # LOOKUP_QUERY_LT,
    # LOOKUP_QUERY_LTE,
    LOOKUP_QUERY_EXCLUDE,
)
from django_elasticsearch_dsl_drf.filter_backends import (
    CompoundSearchFilterBackend,
    FilteringFilterBackend,
    IdsFilterBackend,
    OrderingFilterBackend,
    DefaultOrderingFilterBackend,
)
from django_elasticsearch_dsl_drf.viewsets import BaseDocumentViewSet
from django_elasticsearch_dsl_drf.pagination import LimitOffsetPagination

from analyzer.documents import ArticleDocument
from analyzer.serializers import ArticleDocumentSerializer


class ArticleDocumentView(BaseDocumentViewSet):
    """The ArticleDocument view for Django Rest Framework/ElasticSearch"""

    document = ArticleDocument
    serializer_class = ArticleDocumentSerializer
    pagination_class = LimitOffsetPagination
    lookup_field = "id"

    filter_backends = [
        CompoundSearchFilterBackend,
        FilteringFilterBackend,
        OrderingFilterBackend,
    ]

    # Define search fields
    search_fields = ("title", "author", "keywords", "body")

    filter_fields = {
        "keywords": {
            "field": "key",
            # Note, that we limit the lookups of `keywords` field in
            # this example, to `terms, `prefix`, `wildcard`, `in` and
            # `exclude` filters.
            "lookups": [
                LOOKUP_FILTER_TERMS,
                LOOKUP_FILTER_PREFIX,
                LOOKUP_FILTER_WILDCARD,
                LOOKUP_QUERY_IN,
                LOOKUP_QUERY_EXCLUDE,
            ],
        },
    }

    ordering_fields = {"publication_date": "publication_date", "title": "title"}
