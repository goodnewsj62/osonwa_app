import json

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class DumpDB(models.Model):
    string_blob = models.TextField(null=True)
    byte_blob = models.BinaryField(null=True)

    class Meta:
        abstract = True


class Feed(models.Model):
    hash_id = models.TextField(unique=True, null=True, blank=False)
    gid = models.CharField(max_length=300, null=False, unique=True, blank=False)
    title = models.CharField(max_length=400, blank=False, null=False)
    slug_title = models.SlugField(max_length=700, null=True, blank=True)
    description = models.TextField(null=True)
    link = models.URLField(max_length=700, null=False, blank=False)
    date_published = models.DateTimeField(null=False, blank=False)
    date_scraped = models.DateTimeField(auto_now_add=True)
    image_url = models.URLField(max_length=500, null=True, blank=True)
    logo_url = models.URLField(max_length=500, null=True, blank=True)
    website = models.CharField(max_length=500, null=True, blank=False)
    scope = models.CharField(max_length=100, null=True, blank=True)
    subscope = models.JSONField(default=dict)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.title}"

    @property
    def subscopes(self):
        return self.subscope

    @subscopes.setter
    def subscopes(self, dict_scope):
        subscopes = self.subscope
        subscopes.update(dict_scope)
        self.subscope = subscopes

    def save(self, *args, **kwargs) -> None:
        self.slug_title = slugify(self.title)
        return super().save(*args, **kwargs)


class UserFeedGroup(models.Model):
    name = models.CharField(max_length=300, null=True, blank=True, unique=True)
    topics_rank = models.JSONField(default=dict)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.name}"

    def __repr__(self) -> str:
        return f"UserFeedGroup({self.name})"

    @property
    def topics(self):
        return self.topics_rank

    @topics.setter
    def topics(self, new_topics_dict: dict):
        existing_topics = self.topics_rank

        for topic, weight in new_topics_dict.items():
            existing_topics[topic] = weight

        self.topics_rank = existing_topics


class UserReaction(models.Model):
    REACTION_CHOICES = [
        ("facesunglass", "face with sunglass"),  # "\U0001F60E"
        ("rocket", "rocket"),  # "\U0001F680"
        ("fire", "fire"),  # "\U0001F525"
        ("redheart", "red heart"),  # "\u2764\uFE0F"
        ("hundred", "hundred points"),  # "\U0001F4AF"
        ("okhand", "ok hand"),  # "\U0001F44C"
        ("wine", "wine"),  # "\U0001F377"
        ("explodinghead", "exploding head"),  # "\U0001F92F"
    ]
    user = models.ForeignKey(
        "account.User",
        on_delete=models.CASCADE,
        related_name="%(app_label)s_%(class)s",
        related_query_name="%(app_label)s_%(class)s",
    )
    reaction = models.CharField(
        max_length=100, null=False, blank=False, choices=REACTION_CHOICES
    )

    class Meta:
        abstract = True

    @property
    def reactions(self):
        return self.reaction

    @reactions.setter
    def reactions(self, data):
        if not isinstance(data, dict):
            raise ValueError("must be a mapping")

        existing_reactions = self.reaction
        incoming_reactions = data.keys()

        for reaction in incoming_reactions:
            existing_reactions[reaction] = existing_reactions.get(reaction, 0) + 1

        self.reaction = existing_reactions

    # check if data is instance of str if it is get existing reaction and loads incoming reactions
    # then add all incoming reactions to existing reaction then set reaction and save return the saved reasctions


class Tag(models.Model):
    tag_name = models.CharField("tags", max_length=300, unique=True, null=False)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.tag_name
