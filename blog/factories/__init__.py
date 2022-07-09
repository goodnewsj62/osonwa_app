import factory
from django.conf import settings

from factories import ReactionFactory

__all__ = [
    "BundleFactory",
    "PostFactory",
    "PostImagesFactory",
    "PostUserReactionFactory",
]


class BundleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "blog.Bundle"

    topic = factory.Faker("text")
    poster = factory.django.ImageField(
        from_path=settings.BASE_DIR / "test_media" / "wallpaper.jpg"
    )


class PostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "blog.Post"
        exclude = ("random_num",)

    title = factory.Faker("name")
    cover_image = factory.django.ImageField(
        from_path=settings.BASE_DIR / "test_media" / "wallpaper.jpg"
    )
    author = factory.SubFactory("account.factories.UserFactory")
    bundle = factory.SubFactory(BundleFactory)
    random_num = factory.Faker("random_digit")
    order = factory.LazyAttribute(lambda o: o.random_num + 1 if o.bundle else None)


class PostImagesFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "blog.PostImages"

    post = factory.SubFactory(PostFactory)
    image = factory.django.ImageField(
        from_path=settings.BASE_DIR / "test_media" / "wallpaper.jpg"
    )


class PostUserReactionFactory(ReactionFactory):
    class Meta:
        model = "blog.PostUserReactions"

    post = factory.SubFactory(PostFactory)


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "blog.Tags"

    tag_name = factory.Faker("name")
