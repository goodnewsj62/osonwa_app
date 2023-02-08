import json
from django.urls import reverse
from rest_framework.test import APIClient


def test_post_create(db, user):
    client = APIClient()
    url = reverse("blog:post-list")
    client.force_authenticate(user)

    data = {
        "title": "some Title",
        "content": json.dumps(
            {"delta": {"ops": [{"insert": "so here we go\n"}]}, "html": ""}
        ),
    }
    resp = client.post(url, data=data)
    assert resp.status_code == 201
    assert isinstance(resp.data.get("content"), dict) == True


def test_post_list(db, post_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse("blog:post-list")
    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data["results"][0].get("post_id") == post_a.post_id


def test_post_retrieve(db, post_a):
    client = APIClient()
    url = reverse(
        "blog:post-detail",
        kwargs={"post_id": post_a.post_id, "slug_title": post_a.slug_title},
    )
    resp = client.get(url)
    assert isinstance(resp.data.get("content"), dict) == True
    assert resp.data.get("post_id") == post_a.post_id
    assert resp.status_code == 200


def test_post_partial_update(db, post_a, bundle_a):
    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse(
        "blog:post-detail",
        kwargs={"post_id": post_a.post_id, "slug_title": post_a.slug_title},
    )
    data = {
        "title": "some asf",
        "content": json.dumps(
            {"delta": {"ops": [{"insert": "so here we go\n"}]}, "html": ""}
        ),
        "bundle": bundle_a.id,
    }
    resp = client.patch(url, data=data)
    assert data.get("bundle") == resp.data.get("bundle")
    assert data.get("title") == resp.data.get("title")
    assert resp.status_code == 200


def test_post_update_by_wrong_creator(db, test_user_gen, post):
    client = APIClient()
    client.force_authenticate(test_user_gen)
    url = reverse(
        "blog:post-detail",
        kwargs={"post_id": post.post_id, "slug_title": post.slug_title},
    )
    data = {"title": "some asf"}
    resp = client.patch(url, data=data)
    assert resp.status_code == 403


def test_check_for_existing_order_number(db, post_a, post, bundle_a):
    post.order = 999
    post.bundle = bundle_a
    post.save()

    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse(
        "blog:post-detail",
        kwargs={"post_id": post_a.post_id, "slug_title": post_a.slug_title},
    )
    data = {
        "bundle": bundle_a.id,
        "order": 999,
    }
    resp = client.patch(url, data=data)
    assert resp.status_code == 400


def test_for_bundle_update_by_wrong_creator(db, test_user_gen, post_a, bundle_a):
    post_a.author = test_user_gen
    post_a.save()

    client = APIClient()
    client.force_authenticate(post_a.author)
    url = reverse(
        "blog:post-detail",
        kwargs={"post_id": post_a.post_id, "slug_title": post_a.slug_title},
    )
    data = {
        "bundle": bundle_a.id,
    }
    resp = client.patch(url, data=data)
    assert resp.status_code == 400


def test_bundle_list(db, bundle_a):
    client = APIClient()
    url = reverse("blog:bundle-list")
    resp = client.get(url)
    assert resp.status_code == 200


def test_bundle_post(db, user_a):
    client = APIClient()
    client.force_authenticate(user_a)
    url = reverse("blog:bundle-list")
    topic = "python for beginners"

    resp = client.post(url, data={"topic": topic})

    assert resp.data.get("created_by") == user_a.id
    assert resp.data.get("topic") == topic
    assert resp.status_code == 201


def test_bundle_post(db, user_a):
    client = APIClient()
    client.force_authenticate(user_a)
    url = reverse("blog:bundle-list")
    topic = "python for beginners"

    resp = client.post(url, data={"topic": topic})

    assert resp.data.get("created_by") == user_a.id
    assert resp.data.get("topic") == topic
    assert resp.status_code == 201


def test_bundle_patch(db, bundle_a):
    client = APIClient()
    client.force_authenticate(bundle_a.created_by)
    url = reverse("blog:bundle-detail", kwargs={"pk": bundle_a.id})
    topic = "python for beginners"

    resp = client.patch(url, data={"topic": topic})

    assert resp.data.get("topic") == topic
    assert resp.status_code == 200


def test_bundle_update_by_wrong_creator(db, test_user_gen, bundle_a):
    client = APIClient()
    client.force_authenticate(test_user_gen)
    url = reverse("blog:bundle-detail", kwargs={"pk": bundle_a.id})
    topic = "python for beginners"

    resp = client.patch(url, data={"topic": topic})
    assert resp.status_code == 404


def test_tag_list(db, tag_a):
    client = APIClient()
    url = reverse("blog:tag-list")

    resp = client.get(url)
    assert resp.status_code == 200


def test_tag_post(db, user):
    client = APIClient()
    client.force_authenticate(user)
    url = reverse("blog:tag-list")

    resp = client.post(url, data={"tag_name": "faithful"})
    assert resp.status_code == 201


def test_tag_retrieve(db, user, tag_a):
    client = APIClient()
    url = reverse("blog:tag-detail", kwargs={"pk": tag_a.id})

    resp = client.get(url)
    assert resp.status_code == 200


def test_tag_update_restriction(db, user, tag_a):
    client = APIClient()
    client.force_authenticate(user)
    url = reverse("blog:tag-detail", kwargs={"pk": tag_a.id})

    resp = client.patch(url, data={"tag_name": "faithful"})
    assert resp.status_code == 403


def test_tag_search(db, tag_a):
    client = APIClient()
    url = reverse("blog:tag-search") + f"?keyword={tag_a.tag_name[:5]}"

    resp = client.get(url)
    assert resp.status_code == 200
    assert resp.data[0].get("tag_name") == tag_a.tag_name


def test_bundle_search(db, bundle_a):
    client = APIClient()
    client.force_authenticate(bundle_a.created_by)

    url = reverse("blog:bundle-search") + f"?topic={bundle_a.topic}"

    resp = client.get(url)

    assert resp.status_code == 200
    assert resp.data[0].get("topic") == bundle_a.topic
