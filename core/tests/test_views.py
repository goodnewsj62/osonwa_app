import json

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


def test_search_saved(db, post_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse("core:search_saved") + f"?q={post_a.title[:5]}&type=article"

    Saved.objects.create(content_object=post_a, user=post_a.author)

    resp = client.get(url)

    assert resp.status_code == 200
    post_title = resp.data.get("results")[0].get("content_object").get("title")
    assert post_title == post_a.title


def test_search_like(db, post_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse("core:search_liked") + f"?q={post_a.title[:5]}&type=article"

    Liked.objects.create(content_object=post_a, user=post_a.author)

    resp = client.get(url)

    assert resp.status_code == 200
    post_title = resp.data.get("results")[0].get("content_object").get("title")
    assert post_title == post_a.title


def test_comments_list(db, comment_object):
    client = APIClient()
    url = (
        reverse("core:comment-list")
        + f"?type=post&id={comment_object.content_object.id}"
    )

    resp = client.get(url)

    assert resp.status_code == 200
    assert resp.data.get("results")[0].get("id") == comment_object.content_object.id


def test_create_comment(db, post_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse("core:comment-list")

    data = {
        "object_id": post_a.id,
        "type": "post",
        "content": json.dumps(
            {"delta": {"ops": [{"insert": "so here we go\n"}]}, "html": ""}
        ),
        "text_content": "friends with the monster",
    }

    resp = client.post(url, data=data)

    assert resp.status_code in [201, 200]


def test_create_comment_on_comment(db, comment_object, post):
    client = APIClient()
    client.force_authenticate(post.author)
    url = reverse("core:comment-list")

    data = {
        "object_id": comment_object.id,
        "type": "comment",
        "content": json.dumps(
            {"delta": {"ops": [{"insert": "so here we go\n"}]}, "html": ""}
        ),
        "text_content": "friends with the monster",
    }

    resp = client.post(url, data=data)
    data["object_id"] = resp.data.get("id")
    response = client.post(url, data=data)

    assert resp.status_code in [201, 200]
    assert response.status_code == 400


def test_patch_comments(db, comment_object):
    client = APIClient()
    client.force_authenticate(comment_object.content_object.author)
    url = reverse("core:comment-detail", kwargs={"pk": comment_object.id})

    data = {
        "content": json.dumps(
            {"delta": {"ops": [{"insert": "so we go up\n"}]}, "html": ""}
        ),
        "text_content": "friends with the monster",
    }

    resp = client.patch(url, data=data)
    assert resp.status_code == 200


def test_news_list(db, newsfeed):
    client = APIClient()
    url = reverse("core:news")

    resp = client.get(url)

    assert resp.status_code == 200
    assert resp.data.get("results")[0].get("id") == newsfeed.id


def test_news_detail(db, newsfeed):
    client = APIClient()
    url = reverse(
        "core:news_detail",
        kwargs={"slug_title": newsfeed.slug_title, "post_id": newsfeed.gid},
    )

    resp = client.get(url)

    assert resp.status_code == 200
    assert resp.data.get("id") == newsfeed.id
