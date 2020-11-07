from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from analyzer.viewsets import ArticleDocumentView

router = DefaultRouter()
articles = router.register(r"articles", ArticleDocumentView, basename="articledocument")

urlpatterns = [url(r"^", include(router.urls))]
