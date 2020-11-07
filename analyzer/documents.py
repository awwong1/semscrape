from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from analyzer.models import Article
from elasticsearch_dsl import analyzer as es_analyzer

html_strip = es_analyzer(
    "html_strip",
    tokenizer="standard",
    filter=["lowercase", "stop", "snowball"],
    char_filter=["html_strip"],
)


@registry.register_document
class ArticleDocument(Document):
    class Index:
        name = "article"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    id = fields.KeywordField()
    title = fields.TextField(analyzer=html_strip, fields={"raw": fields.KeywordField()})
    keywords = fields.NestedField(properties={"key": fields.KeywordField()})

    def prepare_keywords(self, instance):
        return [{"key": kw} for kw in instance.keywords]

    class Django:
        model = Article

        fields = [
            "author",
            "body",
        ]
