import re
from collections import Counter

import nltk.data
from bs4 import BeautifulSoup
from celery import shared_task
from celery.utils.log import get_task_logger
from crawler.models import RSSEntry
from django.db.models import Q
from transformers import pipeline

from analyzer.models import Article

logger = get_task_logger(__name__)


def find_title(soup):
    """Use BeautifulSoup to find the article title"""
    possible_titles = []

    # check <head><title>
    head_titles = soup.head.find_all("title")
    for head_title in head_titles:
        if head_title.string:
            possible_titles.append(head_title.string)

    # check <meta content="Title" name=".*title" />
    meta_names = soup.find_all("meta", attrs={"name": re.compile(r".*title")})
    for meta_name in meta_names:
        if meta_name["content"]:
            possible_titles.append(meta_name["content"])

    # check <meta content="Title" property=".*title" />
    meta_names = soup.find_all("meta", attrs={"property": re.compile(r".*title")})
    for meta_name in meta_names:
        if meta_name["content"]:
            possible_titles.append(meta_name["content"])

    title = None
    if len(possible_titles):
        # trim all leading and trailing whitespace from candidates
        possible_titles = [pt.strip() for pt in possible_titles]
        title, _ = Counter(possible_titles).most_common(n=1)[0]
    return title


def find_keywords(soup):
    """Use BeautifulSoup to find the article search keywords"""
    keywords = []

    # check <meta name=".*keywords">
    tag = soup.find("meta", attrs={"name": re.compile(r".*keywords")})
    if tag and tag["content"]:
        keywords.extend(tag["content"].split(","))

    keywords = [kw.strip() for kw in keywords]
    return keywords


def find_author(soup):
    """Use BeautifulSoup to find who wrote the article"""

    # check <meta content="Name" name=".*author" />
    tag = soup.find("meta", attrs={"name": re.compile(r".*author")})
    if tag and tag["content"]:
        return tag["content"].strip()

    return None


def find_article_body(soup):
    """Return the relevant part of the article as human readable text."""
    article_tags = soup.find_all("article")
    body = []
    for article_tag in article_tags:
        body.extend(article_tag.strings)

    if body:
        body = [line.strip() for line in body]
        body = [line for line in body if line]
        return " ".join(body)
    return None


@shared_task
def compute_sentiment(article_id):
    try:
        article = Article.objects.get(pk=article_id)
        assert article.body, f"Article body is falsy! `{article.body}`"
    except Exception as e:
        logger.warn(f"Article invalid `pk={article_id}`, {e}")
        return

    if hasattr(article, "sentiment") and article.sentiment:
        if article.sentiment.keys():
            # we've already computed sentiment for this article
            return

    # loading these models is time-consuming, and you can't use the kwarg trick :(
    sentence_tokenizer = nltk.data.load("tokenizers/punkt/english.pickle")
    sentiment_analyzer = pipeline(
        "sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english"
    )

    # run all the sentences through the the sentence tokenizer to get sentences
    sentences = sentence_tokenizer.tokenize(article.body.strip())

    # run through the sentiment analyzer to get pos/neg label and score
    sentiments = sentiment_analyzer(sentences)

    # join the sentiment output and sentences together into a dictionary
    article.sentiment = dict(zip(sentences, sentiments))
    article.save()


@shared_task
def dispatch_compute_sentiments():
    """Find entries that have not been sentiment analyzed and dispatch analysis"""
    missed_articles = Article.objects.filter(sentiment__exact={}).exclude(
        body__isnull=True
    )
    for article in missed_articles.iterator():
        compute_sentiment.delay(article.pk)


@shared_task
def parse_html_entry(rss_entry_id):
    try:
        rss_entry = RSSEntry.objects.get(pk=rss_entry_id)
        content_type = rss_entry.headers.get("Content-Type")
        assert "html" in content_type, f"Content-Type == {content_type}, expected html"
        soup = BeautifulSoup(rss_entry.raw_html, "html.parser")
    except Exception as e:
        logger.warn(f"RSSEntry invalid `pk={rss_entry_id}`, {e}")
        return

    article, _ = Article.objects.update_or_create(
        rss_entry=rss_entry,
        defaults={
            "title": find_title(soup),
            "keywords": find_keywords(soup),
            "author": find_author(soup),
            "body": find_article_body(soup),
        },
    )

    compute_sentiment.delay(article.pk)


@shared_task
def dispatch_parse_html_entries():
    """Find entries that have not been parse_html'd dispatch parse_html task"""
    missed_entries = RSSEntry.objects.exclude(
        Q(raw_html__isnull=True)  # Exclude where raw_html is null OR
        | Q(article__isnull=False)  # article has already been parsed
    ).filter(
        # Handle where Content-Type header is textual
        **{"headers__Content-Type__icontains": "text/html"}
    )
    for entry in missed_entries.iterator():
        parse_html_entry.delay(entry.pk)
