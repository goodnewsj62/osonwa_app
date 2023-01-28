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
