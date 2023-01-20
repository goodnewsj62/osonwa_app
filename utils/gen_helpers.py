def setattr_if_exists(obj: object, data: dict):
    for field, val in data.items():
        if hasattr(obj, field):
            setattr(obj, field, val)
