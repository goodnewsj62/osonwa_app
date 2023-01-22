from django.urls import reverse
from rest_framework.test import APIClient
from osonwa.helpers import get_auth_token


def test_username_exists_view(test_user_one):
    client = APIClient()
    url = reverse("auth:valid_username")
    valid_response = client.get(url + f"?username={test_user_one.username}")
    invalid_response = client.get(url + "?username=sdhdndjdjuenden")
    assert valid_response.data.get("status") == True
    assert invalid_response.data.get("status") == False


def test_account_profile_detail(test_user_one):
    client = APIClient()
    url = reverse("auth:profile", kwargs={"username": test_user_one.username})
    response = client.get(url)
    assert response.status_code == 200
    assert response.data.get("email") == test_user_one.email


def test_account_profile(test_user_one):
    client = APIClient()
    client.force_authenticate(test_user_one)
    url = reverse("auth:auth_user_profile")
    response = client.get(url)
    assert response.status_code == 200
    assert response.data.get("email") == test_user_one.email


def test_non_existing_profile(db):
    client = APIClient()
    url = reverse("auth:profile", kwargs={"username": "someusernamenotknow"})
    response = client.get(url)
    assert response.status_code == 404


def test_patch_profile(test_user_one):
    # arrange
    client = APIClient()
    token = get_auth_token(test_user_one).get("access")
    client.credentials(HTTP_AUTHORIZATION="Bearer " + token)
    url = reverse("auth:profile", kwargs={"username": test_user_one.username})
    name = "sweet boi"
    data = {"first_name": name}

    response = client.patch(url, data)

    assert response.data.get("first_name") == name


def test_email_patch_not_working(test_user_one):
    client = APIClient()
    client.force_authenticate(test_user_one)
    url = reverse("auth:profile", kwargs={"username": test_user_one.username})
    email = "joeboi@fk.com"
    data = {"email": email}

    response = client.patch(url, data)

    assert response.data.get("email") != email


def test_existing_username_patch(test_user_one, test_user_two):
    client = APIClient()
    client.force_authenticate(test_user_one)
    url = reverse("auth:profile", kwargs={"username": test_user_one.username})
    data = {"username": test_user_two.username}

    response = client.patch(url, data)

    assert response.status_code == 400


def test_interest_post(test_user_one, python_interest):
    client = APIClient()
    client.force_authenticate(test_user_one)
    url = reverse("auth:interests")

    response = client.post(url, data={"interests": [python_interest.name]})
    test_user_one.refresh_from_db()

    assert response.status_code == 200
    assert test_user_one.interests.filter(name=python_interest.name).exists()


def test_interest_delete(test_user_one, python_interest):
    test_user_one.interests.add(python_interest)
    client = APIClient()
    client.force_authenticate(test_user_one)
    url = reverse("auth:d_interest", kwargs={"username": test_user_one.username})

    response = client.delete(url, data={"interest": [python_interest.name]})
    test_user_one.refresh_from_db()

    assert response.status_code == 200
    assert test_user_one.interests.filter(name=python_interest.name).exists() == False


def test_interest_patch(test_user_one, python_interest):
    client = APIClient()
    client.force_authenticate(test_user_one)
    url = reverse("auth:d_interest", kwargs={"username": test_user_one.username})

    response = client.patch(url, data={"interest": [python_interest.name]})
    test_user_one.refresh_from_db()

    assert response.status_code == 200
    assert test_user_one.interests.filter(name=python_interest.name).exists()
