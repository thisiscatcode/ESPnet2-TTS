from pathlib import Path

from app import create_app


class FakeBackend:
    name = "fake-espnet"
    supported_languages = ("en", "ja")
    loaded_languages = ("en",)

    def synthesize(self, text: str, language: str, output_path: Path, speed: float) -> int:
        assert text
        assert speed > 0
        output_path.write_bytes(f"WAV:{language}".encode())
        return 24000


def client(tmp_path):
    application = create_app(FakeBackend(), output_dir=tmp_path / "output")
    application.config["TESTING"] = True
    return application.test_client()


def test_health(tmp_path):
    response = client(tmp_path).get("/health")
    assert response.get_json()["loaded_languages"] == ["en"]


def test_synthesis_and_download(tmp_path):
    api = client(tmp_path)
    response = api.post(
        "/synthesize", json={"text": "こんにちは", "language": "ja"}
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["sample_rate"] == 24000
    assert api.get(body["audio_url"]).data == b"WAV:ja"


def test_normalises_language_name(tmp_path):
    response = client(tmp_path).post(
        "/texttospeech", json={"text": "hello", "lang": "English"}
    )
    assert response.status_code == 200
    assert response.get_json()["language"] == "en"


def test_rejects_invalid_speed(tmp_path):
    response = client(tmp_path).post(
        "/synthesize", json={"text": "hello", "language": "en", "speed": 3}
    )
    assert response.status_code == 400


def test_legacy_batch_rejects_traversal(tmp_path):
    response = client(tmp_path).post(
        "/get_espnet_batch",
        json={"text": "hello", "lang": "en", "file_path": "../voice.wav"},
    )
    assert response.status_code == 400
