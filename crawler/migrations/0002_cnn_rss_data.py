from django.db import migrations


def initialize_cnn_rss_links(apps, schema_editor):
    RSSFeed = apps.get_model("crawler", "RSSFeed")
    RSSFeed.objects.bulk_create(
        [
            # CNN Money (https://money.cnn.com/services/rss/)
            RSSFeed(
                organization="CNN Money",
                title="All Stories",
                url="http://rss.cnn.com/rss/money_latest.rss",
            ),
            RSSFeed(
                organization="CNN Money",
                title="Top Stories",
                url="http://rss.cnn.com/rss/money_topstories.rss",
            ),
            RSSFeed(
                organization="CNN Money",
                title="Most Popular",
                url="http://rss.cnn.com/rss/money_mostpopular.rss",
            ),
            RSSFeed(
                organization="CNN Money",
                title="Companies",
                url="http://rss.cnn.com/rss/money_news_companies.rss",
            ),
            RSSFeed(
                organization="CNN Money",
                title="International",
                url="http://rss.cnn.com/rss/money_news_international.rss"
            ),
            RSSFeed(
                organization="CNN Money",
                title="Economy",
                url="http://rss.cnn.com/rss/money_news_economy.rss",
            ),
            RSSFeed(
                organization="CNN Money",
                title="Markets",
                url="http://rss.cnn.com/rss/money_markets.rss",
            ),
            RSSFeed(
                organization="CNN Money",
                title="The Buzz",
                url="http://rss.cnn.com/cnnmoneymorningbuzz",
            ),
            # CNN (https://www.cnn.com/services/rss/)
            RSSFeed(
                organization="CNN",
                title="Top Stories",
                url="http://rss.cnn.com/rss/cnn_topstories.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="World",
                url="http://rss.cnn.com/rss/cnn_world.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="U.S.",
                url="http://rss.cnn.com/rss/cnn_us.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Politics",
                url="http://rss.cnn.com/rss/cnn_allpolitics.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Technology",
                url="http://rss.cnn.com/rss/cnn_tech.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Health",
                url="http://rss.cnn.com/rss/cnn_health.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Entertainment",
                url="http://rss.cnn.com/rss/cnn_showbiz.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Travel",
                url="http://rss.cnn.com/rss/cnn_travel.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Video",
                url="http://rss.cnn.com/rss/cnn_freevideo.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="Most Recent",
                url="http://rss.cnn.com/rss/cnn_latest.rss",
            ),
            RSSFeed(
                organization="CNN",
                title="CNN Underscored",
                url="http://rss.cnn.com/cnn-underscored",
            ),
        ]
    )


class Migration(migrations.Migration):
    dependencies = [
        ("crawler", "0001_initial"),
    ]

    operations = [migrations.RunPython(initialize_cnn_rss_links)]
