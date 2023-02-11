from rest_framework.test import APIClient
from django.urls import reverse

from ..models import Liked, Saved


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

    like_instance = Liked.objects.filter(
        post=liked_posts_object[0].content_object, user=post_author
    ).first()
    assert resp.status_code == 200
    assert like_instance == None


def test_saved_posts(db, saved_posts_object):
    client = APIClient()
    post_author = saved_posts_object[0].content_object.author
    url = reverse("core:saved", kwargs={"pk": post_author.pk}) + "?type=article"
    client.force_authenticate(post_author)

    resp = client.get(url)

    assert resp.status_code == 200
    assert isinstance(resp.data.get("results"), list)
    assert len(resp.data.get("results")) == 2


def test_toggle_saved_state(db, saved_posts_object):
    client = APIClient()
    post_author = saved_posts_object[0].content_object.author
    post_pk = saved_posts_object[0].content_object.pk
    url = reverse("core:saved", kwargs={"pk": post_pk})
    client.force_authenticate(post_author)

    resp = client.patch(url, {"type": "post"})

    like_instance = Saved.objects.filter(
        post=saved_posts_object[0].content_object, user=post_author
    ).first()
    assert resp.status_code == 200
    assert like_instance == None


def test_is_saved(db, saved_posts_object):
    client = APIClient()
    content_object = saved_posts_object[0].content_object
    client.force_authenticate(content_object.author)
    url = reverse("core:is_saved", kwargs={"type": "post", "pk": content_object.pk})

    resp = client.get(url)

    assert resp.status_code == 200


def test_is_liked(db, liked_posts_object):
    client = APIClient()
    content_object = liked_posts_object[0].content_object
    client.force_authenticate(content_object.author)
    url = reverse("core:is_liked", kwargs={"type": "post", "pk": content_object.pk})

    resp = client.get(url)

    assert resp.status_code == 200


def test_like(db, post_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse("core:liked", kwargs={"pk": post_a.pk})

    resp = client.patch(url, {"type": "post"})

    assert Liked.objects.first().content_object == post_a


def test_save(db, post_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse("core:saved", kwargs={"pk": post_a.pk})

    resp = client.patch(url, {"type": "post"})

    assert Saved.objects.first().content_object == post_a