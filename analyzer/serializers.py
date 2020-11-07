from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

from analyzer.documents import ArticleDocument


class ArticleDocumentSerializer(DocumentSerializer):
    """REST API Serializer for the Article Elastic Search Document"""

    class Meta(object):
        document = ArticleDocument

        fields = (
            "id",
            "url",
            "title",
            "author",
            "publication_date",
            "overall_sentiment",
            "keywords",
            "body",
            "sentiment",
        )
