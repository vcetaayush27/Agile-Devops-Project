"""Cross-platform production WSGI server for local demonstrations."""
import os
from waitress import serve
from app import app


def main():
    try:
        port = int(os.getenv("PORT", "5000"))
        if not 1 <= port <= 65535:
            raise ValueError
    except ValueError:
        raise SystemExit("PORT must be an integer from 1 to 65535.")
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Open http://127.0.0.1:{port} in your browser. Press Ctrl+C to stop.", flush=True)
    serve(app, host=host, port=port, threads=4)


if __name__ == "__main__":
    main()
