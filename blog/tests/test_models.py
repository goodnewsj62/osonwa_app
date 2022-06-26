import pytest
from django.db import IntegrityError


from pytest_factoryboy import register
from faker import Factory as FakerFactory

from osonwa.assert_helpers import (
    assert_equal,
    assert_false,
    assert_isinstance,
    assert_not_equal,
    assert_true,
)


from blog.models import Post, PostImages, PostUserReactions, Tags

faker = FakerFactory.create()


def test_post_creation(db, post_a):
    post = Post.objects.filter(pk=post_a.pk)
    assert_true(post.exists())
    assert_isinstance(post_a, Post)


def test_post_noauthor(db, post_a):
    with pytest.raises(IntegrityError):
        post_a.author = None
        post_a.save()


def test_slug_title(db, post_a):
    post_a.title = "wherever you go bla"
    post_a.save()
    assert_equal(post_a.slug_title, "wherever-you-go-bla")


def test_bundle_creation(db, post_a):
    assert post_a.bundle.topic
    assert post_a.order


@pytest.mark.skip
def test_postcreation_signals():
    pass


def test_post_images_reg(db, post_image_a):
    assert_true(PostImages.objects.filter(reg=post_image_a.reg).exists())


def test_post_images_post(db, post_image_a):
    assert_isinstance(post_image_a.post, Post)


def test_post_user_reactions(db, post_reaction_a):
    assert_true(PostUserReactions.objects.filter(pk=post_reaction_a.id).exists())


def test_post_user_set_reactions(db, post_reaction_a):
    post_reaction_a.reactions = {"unicode": "a", "unicode-x": "b"}
    post_reaction_a.save()
    assert_equal(post_reaction_a.reactions.get("unicode"), 2)


def test_created_tag(db, tag_a):
    assert_true(Tags.objects.filter(pk=tag_a.pk).exists())


def test_duplicate_created_tags(db, tag_a, tags):
    with pytest.raises(IntegrityError):
        tags.tag_name = tag_a.tag_name
        tags.save()


def test_assign_post_to_tags(db, tag_a, post_a, post):
    tag_a.posts.set([post_a, post])
    assert_equal(tag_a.posts.count(), 2)
