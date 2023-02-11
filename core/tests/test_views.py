from rest_framework.test import APIClient
from django.urls import reverse


def test_liked_posts(db, liked_posts_object):
    client = APIClient()
    post_user = liked_posts_object[0].content_object.author
    url = reverse("core:liked", kwargs={"pk": post_user.pk}) + "?type=article"
    client.force_authenticate(post_user)

    resp = client.get(url)

    assert resp.status_code == 200
    assert isinstance(resp.data.get("results"), list)
    assert len(resp.data.get("results")) == 2


def test_toggle_like_state(db, liked_posts_object):
    client = APIClient()
    post_author = liked_posts_object[0].content_object.author
    post_pk = liked_posts_object[0].content_object.pk
    url = reverse("core:liked", kwargs={"pk": post_pk})
    client.force_authenticate(post_author)

    resp = client.patch(url, {"type": "post"})

    assert resp.status_code == 200


def test_saved_posts(db, saved_posts_object):
    client = APIClient()
    post_author = saved_posts_object[0].content_object.author
    url = reverse("core:saved", kwargs={"pk": post_author.pk}) + "?type=article"
    client.force_authenticate(post_author)

    resp = client.get(url)

    assert resp.status_code == 200
    assert isinstance(resp.data.get("results"), list)
    assert len(resp.data.get("results")) == 2
