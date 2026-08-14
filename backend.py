"""Lazy English/Japanese ESPnet2 synthesis backend."""

from __future__ import annotations

import os
import threading
from pathlib import Path
from typing import Any, Protocol


class TTSBackend(Protocol):
    name: str

    @property
    def loaded_languages(self) -> tuple[str, ...]: ...

    @property
    def supported_languages(self) -> tuple[str, ...]: ...

    def synthesize(self, text: str, language: str, output_path: Path, speed: float) -> int: ...


class ESPnetBackend:
    name = "espnet2"

    def __init__(self) -> None:
        self.model_tags = {
            "en": os.getenv("ESPNET_EN_MODEL", "kan-bayashi/ljspeech_vits"),
            "ja": os.getenv(
                "ESPNET_JA_MODEL", "kan-bayashi/jsut_full_band_vits_prosody"
            ),
        }
        self.device = os.getenv("ESPNET_DEVICE", "")
        self.noise_scale = float(os.getenv("ESPNET_NOISE_SCALE", "0.333"))
        self.noise_scale_dur = float(os.getenv("ESPNET_NOISE_SCALE_DUR", "0.333"))
        self._models: dict[str, Any] = {}
        self._torch: Any | None = None
        self._soundfile: Any | None = None
        self._load_lock = threading.Lock()
        self._inference_lock = threading.Lock()

    @property
    def loaded_languages(self) -> tuple[str, ...]:
        return tuple(sorted(self._models))

    @property
    def supported_languages(self) -> tuple[str, ...]:
        return tuple(self.model_tags)

    def _get_model(self, language: str, speed: float) -> tuple[Any, Any, Any]:
        if language not in self.model_tags:
            raise ValueError(f"unsupported language: {language}")
        if language not in self._models:
            with self._load_lock:
                if language not in self._models:
                    import soundfile
                    import torch
                    from espnet2.bin.tts_inference import Text2Speech

                    device = self.device or ("cuda" if torch.cuda.is_available() else "cpu")
                    self.device = device
                    self._models[language] = Text2Speech.from_pretrained(
                        model_tag=self.model_tags[language],
                        device=device,
                        speed_control_alpha=speed,
                        noise_scale=self.noise_scale,
                        noise_scale_dur=self.noise_scale_dur,
                    )
                    self._torch = torch
                    self._soundfile = soundfile
        model = self._models[language]
        model.speed_control_alpha = speed
        return model, self._torch, self._soundfile

    def synthesize(self, text: str, language: str, output_path: Path, speed: float) -> int:
        model, torch, soundfile = self._get_model(language, speed)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with self._inference_lock, torch.inference_mode():
            result = model(text)
            waveform = result["wav"].view(-1).cpu().numpy()
            soundfile.write(str(output_path), waveform, model.fs)
        return int(model.fs)
