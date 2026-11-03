import os

from app import create_app


def listen_address() -> tuple[str, int]:
    host = os.environ.get("HOST", "127.0.0.1").strip() or "127.0.0.1"
    raw_port = os.environ.get("PORT", "5000").strip() or "5000"
    try:
        port = int(raw_port)
    except ValueError:
        raise SystemExit(f"PORT must be an integer, got {raw_port!r}.")
    if port < 1 or port > 65535:
        raise SystemExit("PORT must be between 1 and 65535.")
    return host, port


def main() -> None:
    app = create_app()
    host, port = listen_address()
    app.run(host=host, port=port, debug=app.config["DEBUG"])


if __name__ == "__main__":
    main()
