from django.contrib import admin

from .models import (
    NewsFeed,
    NewsTag,
    RawFeed,
    CollabBasedRecommendedNewsFeed,
    CollaborativeNewsFeedGroup,
    ContentBasedRecommendedNewsFeed,
    ContentNewsFeedGroups,
)

# Register your models here.
admin.site.register(NewsFeed)
admin.site.register(NewsTag)
admin.site.register(RawFeed)
admin.site.register(ContentNewsFeedGroups)
admin.site.register(ContentBasedRecommendedNewsFeed)
admin.site.register(CollabBasedRecommendedNewsFeed)
admin.site.register(CollaborativeNewsFeedGroup)
