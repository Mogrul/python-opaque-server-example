from flask import Blueprint, request

from opaque_server.database import Database
from opaque_server.opaque import Opaque
from opaque_server.util import deserialise_bytes, serialise_bytes

bp = Blueprint("login", __name__, url_prefix="/login")

@bp.route("/start", methods=["POST"])
def start():
    opaque = Opaque()
    database = Database()

    data = request.get_json(silent=True) or {}
    username = data["username"]
    client_request = deserialise_bytes(data["request"])

    password = database.get_user_password(username)

    if not password:
        print(f"User not found: {username}")
        return {
            "error": "user not found"
        }, 404

    response = opaque.login.start(username, password, client_request)

    return {
        "response": serialise_bytes(response),
    }, 200

@bp.route("/finish", methods=["POST"])
def finish():
    opaque = Opaque()

    data = request.get_json(silent=True) or {}
    username = data["username"]
    client_response = deserialise_bytes(data["response"])

    state = opaque.login.get_state(username)

    if not state:
        print(f"state not found: {username}")
        return {
            "error": "user not found"
        }, 404

    session_key = opaque.login.finish(username, state, client_response)

    return {}, 200

