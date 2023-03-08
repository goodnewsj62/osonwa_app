from django.contrib import admin

from .models import (
    ArticleFeed,
    ArticleTag,
    ContentArticleFeedGroup,
    ContentBasedRecommendedArticle,
    CollabBasedRecommendedArticle,
    CollaborativeArticleFeedGroup,
)

# Register your models here.

admin.site.register(ArticleFeed)
admin.site.register(ArticleTag)
admin.site.register(ContentBasedRecommendedArticle)
admin.site.register(CollabBasedRecommendedArticle)
admin.site.register(ContentArticleFeedGroup)
admin.site.register(CollaborativeArticleFeedGroup)
