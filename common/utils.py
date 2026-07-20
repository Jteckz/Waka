import re
import uuid


def uuid_slugify(value):
    if isinstance(value, uuid.UUID):
        return value.hex
    return re.sub(r"[^a-f0-9]", "", str(value).replace("-", ""))[:32]
