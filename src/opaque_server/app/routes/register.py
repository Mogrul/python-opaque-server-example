import base64

from flask import Blueprint, request

from opaque_server.database import Database
from opaque_server.opaque import Opaque
from opaque_server.util import deserialise_bytes, serialise_bytes

bp = Blueprint("register", __name__, url_prefix="/register")

@bp.route("/start", methods=["POST"])
def start():
    opaque = Opaque()
    data = request.get_json(silent=True) or {}
    client_request = deserialise_bytes(data["request"])
    username = data["username"]

    return {
        "response": serialise_bytes(opaque.register.start(username, client_request)),
    }

@bp.route("/finish", methods=["POST"])
def finish():
    opaque = Opaque()
    database = Database()
    data = request.get_json(silent=True) or {}
    client_response = data["response"]
    username = data["username"]

    response = opaque.register.finish(username, deserialise_bytes(client_response))

    if not response:
        return {}, 404

    username, password = response
    database.register_user(username, password)
    return {}, 200