import base64


def serialise_bytes(obj: bytes) -> str:
    return base64.b64encode(obj).decode("utf-8")

def deserialise_bytes(obj: str) -> bytes:
    return base64.b64decode(obj.encode("utf-8"))