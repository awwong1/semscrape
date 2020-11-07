from crawler.tasks import dispatch_crawl_feeds
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Immediately dispatch RSSFeed crawlers."

    def handle(self, *args, **options):
        dispatch_crawl_feeds()
