import logging
import os
from pathlib import Path

import opaque_ke_py as ke
from cryptography.fernet import Fernet

from opaque_server.metaclass import Singleton

ENC_FILE_PATH = Path(".keys/opaque_enc.key")
SETUP_FILE_PATH = Path(".keys/opaque_setup.bin")

class Opaque(metaclass=Singleton):
    def __init__(self):
        self._logger = logging.getLogger("opaque")
        self.setup = self._get_setup()

        self.register = self.Register(self)
        self.login = self.Login(self)

    def _get_setup(self) -> ke.ServerSetupData:
        if (
            ENC_FILE_PATH.exists()
            and SETUP_FILE_PATH.exists()
        ):
            with open(ENC_FILE_PATH, "rb") as f:
                encryption_key = f.read()

            with open(SETUP_FILE_PATH, "rb") as f:
                encrypted = f.read()

            cipher = Fernet(encryption_key)
            setup = ke.ServerSetupData.from_bytes(cipher.decrypt(encrypted))

            self._logger.debug("Found an existing OPAQUE setup")

            return setup

        else:
            encryption_key = Fernet.generate_key()

            with open(ENC_FILE_PATH, "wb") as f:
                f.write(encryption_key)

            cipher = Fernet(encryption_key)

            setup = ke.server_setup()
            encrypted = cipher.encrypt(setup.to_bytes())

            with open(SETUP_FILE_PATH, "wb") as f:
                f.write(encrypted)

            self._logger.debug("Generated an OPAQUE setup")

            return setup

    class Register:
        def __init__(self, parent: Opaque):
            self._logger = logging.getLogger("opaque.register")
            self._parent = parent

        def start(self, username: str, request: bytes) -> bytes:
            start = ke.server_registration_start(
                self._parent.setup,
                request,
                username.encode("utf-8"),
            )
            upload = start.get_message()

            self._logger.info(f"Started registration: {username}")

            return upload

        def finish(self, username: str, response: bytes) -> tuple[str, bytes] | None:
            finish = ke.server_registration_finish(response)
            file = finish.get_password_file()

            self._logger.info(f"Finished registration: {username}")

            return username, file

    class Login:
        def __init__(self, parent: Opaque):
            self._logger = logging.getLogger("opaque.login")
            self._parent = parent
            self._pending: dict[str, bytes] = {}

        def get_state(self, username: str) -> bytes | None:
            return self._pending.get(username)

        def start(self, username: str, password: bytes, request: bytes) -> bytes:
            start = ke.server_login_start(
                self._parent.setup,
                password,
                request,
                username.encode("utf-8"),
            )
            response = start.get_message()
            state = start.get_state()

            self._pending[username] = state
            self._logger.info(f"Started login: {username}")

            return response

        def finish(self, username: str, state: bytes, response: bytes) -> bytes:
            finish = ke.server_login_finish(
                state,
                response,
            )
            session_key = finish.get_session_key()

            self._logger.info(f"Finished login: {username}")
            self._pending.pop(username)

            return session_key