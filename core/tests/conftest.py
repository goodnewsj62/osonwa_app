import pytest

from ..models import Liked


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
