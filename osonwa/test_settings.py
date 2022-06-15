from .settings import *


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "test_db.sqlite3"),
    }
}


REST_FRAMEWORK.update({"TEST_REQUEST_DEFAULT_FORMAT": "json"})
