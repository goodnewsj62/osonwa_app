import pytest

from ..models import Liked, Saved, Comment


@pytest.fixture
def create_like_objects(db):
    def _create(*posts):
        liked = []
        for post in posts:
            entity = Liked.objects.create(content_object=post, user=post.author)
            liked.append(entity)
        return liked

    return _create


@pytest.fixture
def liked_posts_object(db, post, post_a, create_like_objects):
    return create_like_objects(post, post_a)


@pytest.fixture
def create_saved_objects(db):
    def _create(*posts):
        saved = []
        for post in posts:
            entity = Saved.objects.create(content_object=post, user=post.author)
            saved.append(entity)
        return saved

    return _create


@pytest.fixture
def create_comment(db):
    def _create(post, *args, **kwargs):
        return Comment.objects.create(content_object=post, *args, **kwargs)

    return _create


@pytest.fixture
def saved_posts_object(db, post, post_a, create_saved_objects):
    return create_saved_objects(post, post_a)


@pytest.fixture
def comment_object(db, post, create_comment):
    import json

    return create_comment(
        post,
        created_by=post.author,
        content=json.dumps(
            {"delta": {"ops": [{"insert": "so here we go\n"}]}, "html": ""}
        ),
        text_content="waiting for the exhale...",
    )
