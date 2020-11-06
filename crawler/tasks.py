from datetime import datetime
from time import mktime

import feedparser
import requests
from analyzer.tasks import parse_html_entry
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Q
from django.utils.timezone import make_aware

from crawler.models import RSSEntry, RSSFeed

logger = get_task_logger(__name__)


def request_article(rss_entry, session=requests.Session(), timeout=8.0):
    """Perform the GET request and persist the HTML and meta in the database."""
    resp = None
    try:
        resp = session.get(rss_entry.link, timeout=timeout)
    except requests.exceptions.Timeout:
        # connection to server timed out or server did not send data in time
        logger.warn(f"Request timeout for `{rss_entry}`")
    except requests.exceptions.RequestException as e:
        # arbitrary requests related exception
        logger.warn(f"Could not GET `{rss_entry}`: `{e}`")

    if resp is None:
        # request response not instantiated
        return

    # response can be an http error, so we want to track all the meta
    content_type = resp.headers.get("Content-Type", "")
    raw_html = None

    if "text" in content_type:
        raw_html = resp.text
    else:
        logger.warn(f"Unsupported Content-Type `{content_type}` from `{rss_entry}`")
        raw_html = ""

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
    return rss_entry


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
            rss_entry = request_article(rss_entry, session=session)

        if not hasattr(rss_entry, "article"):
            if "html" in rss_entry.headers.get("Content-Type"):
                parse_html_entry.delay(rss_entry.pk)


@shared_task
def dispatch_crawl_entries():
    """Iterate through valid RSSEntries that don't have html and retry query"""
    missed_entries = RSSEntry.objects.filter(
        Q(raw_html__isnull=True)  # raw_html is null AND
        & (
            # Content-Type header is null OR
            Q(**{"headers__Content-Type__isnull": True})
            |
            # Content-Type header is textual
            Q(**{"headers__Content-Type__icontains": "text/html"})
        )
    )

    session = requests.Session()
    for rss_entry in missed_entries.iterator():
        request_article(rss_entry, session=session)


@shared_task
def dispatch_crawl_feeds():
    """Iterate through all of the RSSFeeds and dispatch a task for each one."""
    for rss_feed in RSSFeed.objects.all().iterator():
        retrieve_feed_entries.delay(rss_feed.pk)
