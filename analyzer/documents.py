from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from analyzer.models import Article
from elasticsearch_dsl import analyzer as es_analyzer

strp_html = es_analyzer(
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
    url = fields.TextField()
    title = fields.TextField(analyzer=strp_html, fields={"raw": fields.KeywordField()})
    author = fields.TextField(analyzer=strp_html, fields={"raw": fields.KeywordField()})
    publication_date = fields.DateField()
    overall_sentiment = fields.ObjectField()
    sentiment = fields.ObjectField(properties={
        "sentence": fields.TextField(),
        "sentiment": fields.ObjectField()
    })
    keywords = fields.NestedField(properties={"key": fields.KeywordField()})
    body = fields.TextField(analyzer=strp_html, fields={"raw": fields.TextField()})

    def prepare_url(self, instance):
        return instance.url

    def prepare_keywords(self, instance):
        return [{"key": kw} for kw in instance.keywords]

    def prepare_publication_date(self, instance):
        return instance.publication_date

    def prepare_overall_sentiment(self, instance):
        return instance.overall_sentiment

    def prepare_sentiment(self, instance):
        # convert it to a list of [{sentence, sentiment}] dictionaries
        return [
            {"sentence": k, "sentiment": v} for (k, v) in instance.sentiment.items()
        ]

    class Django:
        model = Article
