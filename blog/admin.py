from django.contrib import admin

from .models import Bundle, Post, PostImages, Tags

# Register your models here.
admin.site.register(Bundle)
admin.site.register(Post)
admin.site.register(PostImages)
admin.site.register(Tags)
