import uuid
from crawler.models import RSSEntry
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Article(models.Model):
    """Human-readable text extracted from RSSEntry, search document"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # cannot use as PK due to elasticsearch serialization gotcha
    rss_entry = models.OneToOneField(RSSEntry, on_delete=models.CASCADE)

    title = models.CharField(max_length=2048, null=True, default=None)
    keywords = ArrayField(models.CharField(max_length=1024, null=False), default=list)
    author = models.CharField(max_length=2048, null=True, default=None)
    body = models.TextField(null=True, default=None)

    def __str__(self):
        return f"`{self.title}` by `{self.author}`"