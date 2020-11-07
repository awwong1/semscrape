import uuid
from statistics import mean, stdev

from crawler.models import RSSEntry
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Article(models.Model):
    """Human-readable text extracted from RSSEntry, search document"""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # cannot use as PK due to elasticsearch serialization gotcha
    rss_entry = models.OneToOneField(RSSEntry, null=False, on_delete=models.CASCADE)

    title = models.CharField(max_length=2048, null=True, default=None)
    keywords = ArrayField(models.CharField(max_length=1024, null=False), default=list)
    author = models.CharField(max_length=2048, null=True, default=None)
    body = models.TextField(null=True, default=None)

    # store all of the sentiment per sentence within body
    sentiment = models.JSONField(default=dict)
    # sentence is key, value is sentiment output

    def __str__(self):
        return f"`{self.title}` by `{self.author}`"

    @property
    def url(self):
        """Return a link to the article for the user to click"""
        return self.rss_entry.link

    @property
    def publication_date(self):
        """Return an estimate of the article publication date."""
        return self.rss_entry.pub_date or self.rss_entry.requested_at

    @property
    def overall_sentiment(self):
        """Return the overall sentiment of the article if defined."""
        # sentiment values have a label (POS/NEG) and score [0, 1] indicating confidence
        # overall sentiment is an aggregation of all sentence sentiments.
        pos_scores = []
        for output in self.sentiment.values():
            score = output["score"]
            if output["label"] == "NEGATIVE":
                score = 1 - score
            pos_scores.append(score)

        # return summary stats of positive score
        average = None
        deviation = 0.0
        label = "UNKNOWN"
        if len(pos_scores):
            average = mean(pos_scores)  # needs 1 data point
            label = "POSITIVE" if average >= 0.5 else "NEGATIVE"
        if len(pos_scores) > 1:
            deviation = stdev(pos_scores)  # needs 2 data points

        return {"label": label, "avg": average, "std": deviation}
