import feedparser
from datetime import datetime
from time import mktime
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import make_aware

from crawler.models import RSSFeed, RSSEntry


logger = get_task_logger(__name__)


@shared_task
def retrieve_feed_entries(rss_feed_id):
    """Given an rss_feed object, query and schedule articles for parsing."""
    rss_feed = RSSFeed.objects.get(pk=rss_feed_id)
    try:
        data = feedparser.parse(rss_feed.url)
    except Exception as e:
        logger.warn(f"Failed to parse feed: `{e}`")
        data = {}

    req_keys = ["link", "title"]
    for entry in data.get("entries", []):
        if any(req_key not in entry for req_key in req_keys):
            logger.warn(f"Entry missing 'link' or 'title' `{entry}` from `{rss_feed}`")
            continue

        pub_date = None  # may not always exist
        if "published_parsed" in entry:
            # https://stackoverflow.com/a/1697907/1942263
            pub_date = datetime.utcfromtimestamp(mktime(entry["published_parsed"]))
            pub_date = make_aware(pub_date)

        description = entry.get("description", "")
        if not description and "summary" in entry:
            description = entry["summary"]

        RSSEntry.objects.update_or_create(
            link=entry["link"],
            defaults={
                "feed": rss_feed,
                "title": entry["title"],
                "description": description,
                "pub_date": pub_date,
            },
        )


@shared_task
def dispatch_crawl_feeds():
    """Iterate through all of the RSSFeeds and dispatch a task for each one."""
    for rss_feed in RSSFeed.objects.all():
        retrieve_feed_entries.delay(rss_feed.pk)
