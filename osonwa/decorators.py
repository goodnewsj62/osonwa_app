from functools import wraps
from django.db import transaction


def ensure_atomic(view):
    @wraps(view)
    def atomic(*args, **kwargs):
        with transaction.atomic():
            return view(*args, **kwargs)

    return atomic
