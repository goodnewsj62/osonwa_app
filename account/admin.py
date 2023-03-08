from django.contrib import admin

from .models import User, SocialAccount, Profile, Notification, Interest, TokenStore

# Register your models here.
admin.site.register(User)
admin.site.register(SocialAccount)
admin.site.register(Profile)
admin.site.register(Notification)
admin.site.register(Interest)
admin.site.register(TokenStore)
