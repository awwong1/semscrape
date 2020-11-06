import uuid
from django.db import models
from django.contrib.postgres.indexes import GinIndex


class RSSFeed(models.Model):
    """RSS (Really Simple Syndication) feeds for article collection."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.CharField(max_length=30)
    title = models.CharField(max_length=30)
    url = models.URLField(max_length=2048)

    def __str__(self):
        return f"{self.organization}: {self.title} ({self.url})"


class RSSEntry(models.Model):
    """The entries, or articles, contained within an RSS feed."""

    class Meta:
        indexes = [GinIndex(fields=["headers"])]

    feed = models.ForeignKey(RSSFeed, on_delete=models.CASCADE)

    link = models.URLField(primary_key=True)
    title = models.TextField(db_index=True)
    description = models.TextField(blank=True)
    pub_date = models.DateTimeField(null=True)

    # storage for raw html, request metadata
    raw_html = models.TextField(null=True, default=None)  # Raw HTML text
    resolved_url = models.URLField(null=True, max_length=2048)  # ie. redirects
    status_code = models.IntegerField(null=True)  # HTTP status code
    requested_at = models.DateTimeField(null=True)  # Latest request datetime
    headers = models.JSONField(db_index=True, default=dict)  # HTTP response headers

    def __str__(self):
        return f"{self.link} (HTTP {self.status_code})"
