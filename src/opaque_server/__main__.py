from opaque_server.app.app import App
from opaque_server.logger import configure_logger

def main():
    configure_logger()

    app = App()
    app.run(
        host="127.0.0.1",
        port=5000,
        use_reloader=False,
        debug=True,
    )


if __name__ == "__main__":
    main()