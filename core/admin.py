from django.contrib import admin

from .models import Saved, Liked, Comment

# Register your models here.
admin.site.register(Saved)
admin.site.register(Liked)
admin.site.register(Comment)
