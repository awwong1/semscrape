from datetime import datetime
from time import mktime

import feedparser
import requests
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils.timezone import make_aware

from crawler.models import RSSEntry, RSSFeed

logger = get_task_logger(__name__)


def request_article(rss_entry, session=requests.Session(), timeout=8.0):
    """Perform the GET request and persist the HTML and meta in the database."""
    resp = None
    try:
        resp = session.get(rss_entry.link, timeout=6.0)
    except requests.exceptions.Timeout:
        # connection to server timed out or server did not send data in time
        logger.warn(f"Request timeout for `{rss_entry}`")
        return
    except requests.exceptions.RequestException as e:
        # arbitrary requests related exception
        logger.warn(f"Could not GET `{rss_entry}`: `{e}`")

    if not resp:
        return

    # response can be an http error, so we want to track this information also
    raw_html = None
    if resp.ok:
        raw_html = resp.text

    rss_entry, _ = RSSEntry.objects.update_or_create(
        pk=rss_entry.pk,
        defaults={
            "raw_html": raw_html,
            "resolved_url": resp.url,
            "status_code": resp.status_code,
            "requested_at": make_aware(datetime.now()),
            "headers": dict(resp.headers),
        },
    )
    return resp.ok


@shared_task
def retrieve_feed_entries(rss_feed_id):
    """Given an RSSFeed, iterate through all RSSEntries and download the HTML."""
    try:
        rss_feed = RSSFeed.objects.get(pk=rss_feed_id)
        data = feedparser.parse(rss_feed.url)
    except Exception as e:
        logger.warn(f"Failed to parse feed `{rss_feed}`: `{e}`")
        data = {}

    session = requests.Session()

    # Parse all of the RSS entries and create model instances
    for entry in data.get("entries", []):
        if any(req_key not in entry for req_key in ["link", "title"]):
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

        rss_entry, _created = RSSEntry.objects.update_or_create(
            link=entry["link"],
            defaults={
                "feed": rss_feed,
                "title": entry["title"],
                "description": description,
                "pub_date": pub_date,
            },
        )
        if not rss_entry.raw_html:
            request_article(rss_entry, session=session)


@shared_task
def dispatch_crawl_entries():
    """Iterate through all of the RSSEntries that don't have html and retry query"""
    rss_entries = RSSEntry.objects.filter(raw_html__isnull=True)
    session = requests.Session()
    for rss_entry in rss_entries:
        request_article(rss_entry, session=session)


@shared_task
def dispatch_crawl_feeds():
    """Iterate through all of the RSSFeeds and dispatch a task for each one."""
    for rss_feed in RSSFeed.objects.all():
        retrieve_feed_entries.delay(rss_feed.pk)
