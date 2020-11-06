from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from analyzer.models import Article


@registry.register_document
class ArticleDocument(Document):
    class Index:
        name = "article"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    keywords = fields.NestedField(properties={"key": fields.KeywordField()})

    def prepare_keywords(self, instance):
        return [{"key": kw} for kw in instance.keywords]

    class Django:
        model = Article

        fields = [
            "title",
            # "keywords",  # Postgres ArrayField needs logic
            "author",
            "body",
        ]
