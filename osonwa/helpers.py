__author__ = "goodnews osonwa john"

import uuid
import base64

from PIL import Image
from io import BytesIO


def assert_true(expr):
    if expr:
        assert True
    else:
        assert False


def assert_false(expr):
    if not expr:
        assert True
    else:
        assert False


def assert_equals(input_a, input_b):
    assert input_a == input_b


def generate_b64_uuid_string():
    return base64.urlsafe_b64encode(str(uuid.uuid4()).encode()).decode("utf-8")


def resizeImage(image, width_size=400):
    file = Image.open(image)
    thumb_io = BytesIO()
    width, height = file.size
    # keep aspect ratio
    file = file.resize([width_size, int((width_size * height) / width)])
    try:
        file.save(thumb_io, format="jpeg", quality=70)
    except ValueError:
        file = file.convert("RGB")
        file.save(thumb_io, format="jpeg", quality=70)

    # reset pointer to starting byte
    thumb_io.seek(0)
    return thumb_io
