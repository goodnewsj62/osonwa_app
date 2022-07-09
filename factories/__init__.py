from datetime import datetime, timezone

import factory


class FeedFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    gid = factory.Faker("uuid4")
    title = factory.Faker("sentence")
    description = factory.Faker("text")
    link = factory.Faker("url")
    date_published = datetime.now(tz=timezone.utc)
    date_scraped = datetime.now(tz=timezone.utc)
    image_url = factory.Faker("url")
    logo_url = factory.Faker("url")
    website = factory.Faker("word")
    scope = factory.Faker("word")


class ReactionFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    user = factory.SubFactory("account.factories.UserFactory")
    reaction = "redheart"


class FeedGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        abstract = True

    name = factory.Faker("word")
    topics_rank = {"python": 0.8, "php": 0.6, "cyber": 0.2, "cryptography": 0.1}
