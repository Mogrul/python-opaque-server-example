from flask import Flask

from opaque_server.app.routes import login, register

def register_routes(app: Flask) -> None:
    app.register_blueprint(login.bp)
    app.register_blueprint(register.bp)