"""Backward-compatible Gunicorn entry point; prefer ``app:app``."""

from app import app, create_app

__all__ = ["app", "create_app"]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
