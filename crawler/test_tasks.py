import os
from unittest.mock import patch
from django.test import TestCase

import crawler.tasks as tasks
import crawler.models as models


class CrawlerTasksTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        crawler_dir = os.path.dirname(os.path.realpath(__file__))
        stub_xml_fp = os.path.join(crawler_dir, "test_data", "rss_feed.xml")
        bad_lead_fp = os.path.join(crawler_dir, "test_data", "rss_feed_key_err.xml")

        cls.stub_rss_feed = models.RSSFeed.objects.create(
            organization="Test Stub", title="Validation Feed", url=stub_xml_fp
        )
        cls.bad_key_rss = models.RSSFeed.objects.create(
            organization="Test Stub", title="Missing Key", url=bad_lead_fp
        )
        cls.bad_url_rss = models.RSSFeed.objects.create(
            organization="Test Stub", title="Invalid URL", url="/"
        )

    def test_retrieve_feed_entries(self):
        """Verify behavior and robustness of parsing RSS XML"""
        tasks.retrieve_feed_entries(self.stub_rss_feed.pk)

        # have all RSS entries been saved?
        all_rss_entries = models.RSSEntry.objects.all()
        all_entry_ids = [rss.pk for rss in all_rss_entries]
        self.assertSequenceEqual(
            all_entry_ids,
            [
                "http://rss.cnn.com/~r/rss/money_topstories/~3/ojHifu3N_y4/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/lTv_AphBRo4/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/UWgkvIfP_XI/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/M4Jz1s5kLs8/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/MNBt3kv0JUY/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/hmN7_lOkZnU/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/SjtVyLlXRHA/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/IcjguPe3G-Y/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/mERKBBm5KmQ/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/3N8m4XT0qrk/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/fS9JwLh44nk/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/PAmyNhTyuog/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/0pKeXrlECGQ/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/QvPU4bw6fH4/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/uYYwo4u05g0/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/tVlkipYCq-c/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/-kmpoYc55R0/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/NfLK0SRobL8/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/jX98hg6VyEA/index.html",
                "http://rss.cnn.com/~r/rss/money_topstories/~3/Lp5v0-kd2nU/index.html",
            ],
        )

        # task should handle invalid rss data without unhandled runtime exceptions
        tasks.retrieve_feed_entries(self.bad_key_rss.pk)
        tasks.retrieve_feed_entries(self.bad_url_rss.pk)

    def test_dispatch_crawl_feeds(self):
        """Ensure all feed entries are called."""
        with patch.object(tasks.retrieve_feed_entries, "delay") as m:
            tasks.dispatch_crawl_feeds()

        # have all RSS Feeds been called?
        all_rss_feeds = models.RSSFeed.objects.all()
        for rss_feed in all_rss_feeds:
            m.assert_any_call(rss_feed.pk)
        self.assertEquals(len(all_rss_feeds), m.call_count)
