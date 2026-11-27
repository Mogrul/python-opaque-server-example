import logging

from flask import Flask

from opaque_server.app.routes import register_routes


class App(Flask):
    def __init__(self):
        super().__init__(__name__)
        self._logger = logging.getLogger("app")

        register_routes(self)