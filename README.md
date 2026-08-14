# ESPnet2 English–Japanese TTS Service

A self-hosted Flask service for English and Japanese neural text-to-speech using [ESPnet2](https://github.com/espnet/espnet) pretrained models. It provides lazy per-language model loading, validated synthesis requests, downloadable WAV output, CPU/CUDA configuration, Docker and model-free API tests.

This repository is a cleaned, reusable version of TTS service patterns developed for multilingual media workflows. It contains no company database integration, private text, model checkpoint or generated customer audio.

## What it demonstrates

- English and Japanese VITS inference through ESPnet2 `Text2Speech`
- Lazy loading so the API starts without downloading both models
- Thread-safe synthesis and UUID output filenames
- Environment-configurable model tags, device and generation controls
- Health, synthesis and audio-delivery endpoints
- Compatibility with the original `/texttospeech` and `/get_espnet_batch` contracts
- Dependency-injected tests that require neither PyTorch nor model downloads
- Gunicorn, Docker and GitHub Actions delivery paths

## Architecture

```text
client JSON request
  -> Flask validation and request limit
  -> language-specific ESPnet2 Text2Speech model
  -> PyTorch inference
  -> SoundFile WAV output
  -> download endpoint
```

## Install

Python 3.10 is recommended for the ESPnet dependency stack.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Pretrained models download on the first request for their language and are cached by the underlying tooling.

## Run

```bash
gunicorn -c gunicorn.conf.py "app:app"
```

or:

```bash
python app.py
```

## API

### Synthesize speech

```bash
curl http://localhost:5003/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"これは日本語の音声合成デモです。","language":"ja","speed":1.0}'
```

```json
{
  "audio_path": "8f...c1.wav",
  "audio_url": "/audio/8f...c1.wav",
  "language": "ja",
  "sample_rate": 44100,
  "elapsed_seconds": 0.824
}
```

Download the generated file from `GET /audio/<generated-id>.wav`.

Legacy `POST /texttospeech` and `POST /get_espnet_batch` endpoints remain available. The latter accepts a plain `.wav` `file_path`; directory traversal is rejected.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `ESPNET_EN_MODEL` | `kan-bayashi/ljspeech_vits` | English pretrained model tag |
| `ESPNET_JA_MODEL` | `kan-bayashi/jsut_full_band_vits_prosody` | Japanese model tag |
| `ESPNET_DEVICE` | auto | Explicit `cpu` or `cuda` |
| `ESPNET_OUTPUT_DIR` | `generated_audio` | WAV output directory |
| `ESPNET_SPEED` | `1.0` | Default speed-control alpha |
| `ESPNET_NOISE_SCALE` | `0.333` | VITS noise scale |
| `ESPNET_NOISE_SCALE_DUR` | `0.333` | VITS duration noise scale |
| `MAX_TEXT_CHARS` | `2000` | Maximum request text length |
| `PORT` | `5003` | Development server port |

## Tests and quality checks

```bash
python -m pip install -r requirements-dev.txt
ruff check .
pytest -q
```

## Docker

```bash
docker build -t espnet2-tts-api .
docker run --rm -p 5003:5003 \
  -v espnet-output:/app/generated_audio \
  espnet2-tts-api
```

Model downloads can be mounted from a persistent cache in long-running deployments.

## Production considerations

- Add authentication and rate limiting before external exposure.
- Store generated audio in object storage with expiring signed URLs at scale.
- Use a queue for long jobs and define retention for generated files.
- Measure latency, real-time factor and pronunciation quality on target-domain text.
- Review every pretrained model's licence before commercial distribution.

## License and attribution

Service code is MIT licensed. ESPnet is Apache-2.0 licensed; pretrained model artefacts have their own terms. This independent wrapper is not affiliated with the ESPnet project or its model authors.
