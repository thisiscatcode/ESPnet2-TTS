"""Validated Flask API for ESPnet2 text-to-speech."""

from __future__ import annotations

import logging
import os
import time
import uuid
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, request, send_from_directory

from backend import ESPnetBackend, TTSBackend

LOGGER = logging.getLogger(__name__)


def _error(message: str, status: int):
    return jsonify({"error": message}), status


def create_app(
    backend: TTSBackend | None = None,
    *,
    output_dir: str | Path | None = None,
) -> Flask:
    app = Flask(__name__)
    app.config["BACKEND"] = backend or ESPnetBackend()
    app.config["OUTPUT_DIR"] = Path(
        output_dir or os.getenv("ESPNET_OUTPUT_DIR", "generated_audio")
    ).resolve()
    app.config["MAX_TEXT_CHARS"] = int(os.getenv("MAX_TEXT_CHARS", "2000"))
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_REQUEST_MB", "1")) * 1024 * 1024
    app.config["OUTPUT_DIR"].mkdir(parents=True, exist_ok=True)

    @app.get("/health")
    def health():
        selected: TTSBackend = app.config["BACKEND"]
        return jsonify(
            {
                "status": "ok",
                "backend": selected.name,
                "supported_languages": list(selected.supported_languages),
                "loaded_languages": list(selected.loaded_languages),
            }
        )

    def run_synthesis(payload: dict[str, Any], *, legacy: bool = False):
        text = payload.get("text")
        language = str(payload.get("language") or payload.get("lang") or "en").lower()
        if language == "english":
            language = "en"
        elif language == "japanese":
            language = "ja"
        if not isinstance(text, str) or not text.strip():
            return _error("'text' is required", 400)
        if len(text) > app.config["MAX_TEXT_CHARS"]:
            return _error("'text' is too long", 400)
        try:
            speed = float(payload.get("speed", os.getenv("ESPNET_SPEED", "1.0")))
        except (TypeError, ValueError):
            return _error("'speed' must be numeric", 400)
        if not 0.5 <= speed <= 2.0:
            return _error("'speed' must be between 0.5 and 2.0", 400)

        selected: TTSBackend = app.config["BACKEND"]
        if language not in selected.supported_languages:
            return _error(f"unsupported language: {language}", 400)

        requested_name = payload.get("file_path") if legacy else None
        if requested_name:
            filename = Path(str(requested_name)).name
            if filename != requested_name or Path(filename).suffix.lower() != ".wav":
                return _error("'file_path' must be a plain .wav filename", 400)
        else:
            filename = f"{uuid.uuid4().hex}.wav"
        destination = app.config["OUTPUT_DIR"] / filename
        started = time.perf_counter()
        try:
            sample_rate = selected.synthesize(
                text.strip(), language, destination, speed
            )
        except ValueError as exc:
            return _error(str(exc), 400)
        except RuntimeError as exc:
            LOGGER.warning("TTS backend is unavailable: %s", exc)
            return _error(str(exc), 503)
        except Exception:
            LOGGER.exception("speech synthesis failed")
            return _error("speech synthesis failed", 500)
        return jsonify(
            {
                "audio_path": filename,
                "audio_url": f"/audio/{filename}",
                "language": language,
                "sample_rate": sample_rate,
                "elapsed_seconds": round(time.perf_counter() - started, 3),
            }
        )

    @app.post("/synthesize")
    def synthesize():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("a JSON object is required", 400)
        return run_synthesis(payload)

    @app.get("/audio/<path:filename>")
    def audio(filename: str):
        if Path(filename).name != filename or Path(filename).suffix.lower() != ".wav":
            return _error("invalid audio filename", 400)
        return send_from_directory(app.config["OUTPUT_DIR"], filename)

    @app.post("/texttospeech")
    def legacy_text_to_speech():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("a JSON object is required", 400)
        return run_synthesis(payload)

    @app.post("/get_espnet_batch")
    def legacy_batch():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return _error("a JSON object is required", 400)
        return run_synthesis(payload, legacy=True)

    return app


app = create_app()


if __name__ == "__main__":
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5003")))
