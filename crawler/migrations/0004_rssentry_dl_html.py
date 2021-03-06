# Generated by Django 3.1.3 on 2020-11-06 01:21

import django.contrib.postgres.indexes
from django.contrib.postgres.operations import BtreeGinExtension
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("crawler", "0003_rssentry"),
    ]

    operations = [
        migrations.AddField(
            model_name="rssentry",
            name="headers",
            field=models.JSONField(db_index=True, default=dict),
        ),
        migrations.AddField(
            model_name="rssentry",
            name="raw_html",
            field=models.TextField(null=True, default=None),
        ),
        migrations.AddField(
            model_name="rssentry",
            name="requested_at",
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name="rssentry",
            name="resolved_url",
            field=models.URLField(max_length=2048, null=True),
        ),
        migrations.AddField(
            model_name="rssentry",
            name="status_code",
            field=models.IntegerField(null=True),
        ),
        BtreeGinExtension(),
        migrations.AddIndex(
            model_name="rssentry",
            index=django.contrib.postgres.indexes.GinIndex(
                fields=["headers"], name="crawler_rss_headers_fa2911_gin"
            ),
        ),
        migrations.AlterField(
            model_name='rssfeed',
            name='url',
            field=models.URLField(max_length=2048),
        ),

    ]
