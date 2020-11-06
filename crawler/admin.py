from django.contrib import admin
from crawler.models import RSSEntry, RSSFeed

admin.site.register(RSSFeed)
admin.site.register(RSSEntry)
