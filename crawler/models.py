import uuid
from django.db import models


class RSSFeed(models.Model):
    """RSS (Really Simple Syndication) feeds for article collection."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    url = models.URLField(max_length=200)

    def __str__(self):
        return f"{self.organization}: {self.title} ({self.url})"


class RSSEntry(models.Model):
    """The entries, or articles, contained within an RSS feed."""

    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)

    link = models.URLField(primary_key=True)
    title = models.TextField(db_index=True)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(null=True)
