import pytest

from account.tests.conftest import test_user_one
from blog.models import Post


@pytest.fixture
def post_one(db, test_user_one):
    return Post.objects.create(
        author=test_user_one,
        title="the sun is also a star",
    )


# @pytest.fixture
# def Post
