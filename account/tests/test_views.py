from django.urls import reverse
from rest_framework.test import APIClient


def test_username_exists_view(test_user_one):
    client = APIClient()
    url = reverse("auth:valid_username")
    valid_response = client.get(url + f"?username={test_user_one.username}")
    invalid_response = client.get(url + "?username=sdhdndjdjuenden")
    assert valid_response.data.get("status") == True
    assert invalid_response.data.get("status") == False
