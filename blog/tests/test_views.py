from django.urls import reverse
from rest_framework.test import APIClient


def test_post_create(db, user):
    client = APIClient()
    url = reverse("blog:post-list")
    client.force_authenticate(user)
    import json

    data = {
        "title": "some Title",
        "content": json.dumps(
            {"delta": {"ops": [{"insert": "so here we go\n"}]}, "html": ""}
        ),
    }
    resp = client.post(url, data=data)
    assert resp.status_code == 201
    assert isinstance(resp.data.get("content"), dict) == True


def test_post_retrieve(db, post_a):
    client = APIClient()
    url = reverse(
        "blog:post-detail",
        kwargs={"post_id": post_a.post_id, "slug_title": post_a.slug_title},
    )
    resp = client.get(url)
    assert isinstance(resp.data.get("content"), dict) == True
    assert resp.data.get("post_id") == post_a.post_id
    assert resp.data.status_code == 200
