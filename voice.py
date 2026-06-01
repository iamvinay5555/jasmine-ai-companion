"""Voice provider adapters for Jasmine AI Companion.

Both providers are optional. The terminal demo can run without audio tooling, but
these adapters document and implement the production integration points:

- PocketTTS: local/free voice cloning through an installed pocket-tts binary.
- ElevenLabs: expressive cloud TTS through the REST API.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import os
import subprocess
import urllib.request


@dataclass(slots=True)
class VoiceResult:
    provider: str
    output_path: Path
    detail: str


class VoiceProviderError(RuntimeError):
    """Raised when a voice provider is not configured or generation fails."""


@dataclass(slots=True)
class PocketTTSProvider:
    """Local PocketTTS voice-cloning provider."""

    binary_path: str = "pocket-tts"
    voice_sample_path: str = "voice_profiles/default_voice.wav"
    hf_token: str | None = None

    def synthesize(self, text: str, output_path: str | Path) -> VoiceResult:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        env = os.environ.copy()
        if self.hf_token:
            env["HF_TOKEN"] = self.hf_token
        command = [
            self.binary_path,
            "generate",
            "--text",
            text,
            "--voice",
            self.voice_sample_path,
            "--output-path",
            str(output),
        ]
        completed = subprocess.run(command, env=env, text=True, capture_output=True, timeout=300)
        if completed.returncode != 0:
            raise VoiceProviderError(completed.stderr.strip() or completed.stdout.strip() or "PocketTTS failed")
        return VoiceResult("pockettts", output, "Generated with local PocketTTS voice clone")


@dataclass(slots=True)
class ElevenLabsProvider:
    """ElevenLabs REST TTS provider for expressive/special audio."""

    api_key: str
    voice_id: str
    model_id: str = "eleven_multilingual_v2"

    def synthesize(self, text: str, output_path: str | Path) -> VoiceResult:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.voice_id}"
        payload = json.dumps(
            {
                "text": text,
                "model_id": self.model_id,
                "voice_settings": {"stability": 0.45, "similarity_boost": 0.8},
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=payload,
            method="POST",
            headers={
                "xi-api-key": self.api_key,
                "Content-Type": "application/json",
                "Accept": "audio/mpeg",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                output.write_bytes(response.read())
        except Exception as exc:  # pragma: no cover - network/provider dependent
            raise VoiceProviderError(f"ElevenLabs request failed: {exc}") from exc
        return VoiceResult("elevenlabs", output, f"Generated with ElevenLabs model {self.model_id}")


def provider_from_env() -> PocketTTSProvider | ElevenLabsProvider | None:
    """Create a voice provider from environment variables.

    Environment examples:
    - JASMINE_VOICE_PROVIDER=pockettts
      POCKET_TTS_BINARY=/path/to/pocket-tts
      POCKET_TTS_VOICE=/path/to/sample.wav
      HF_TOKEN=...

    - JASMINE_VOICE_PROVIDER=elevenlabs
      ELEVENLABS_API_KEY=...
      ELEVENLABS_VOICE_ID=...
      ELEVENLABS_MODEL_ID=eleven_multilingual_v2
    """

    provider = os.getenv("JASMINE_VOICE_PROVIDER", "").strip().lower()
    if provider == "pockettts":
        return PocketTTSProvider(
            binary_path=os.getenv("POCKET_TTS_BINARY", "pocket-tts"),
            voice_sample_path=os.getenv("POCKET_TTS_VOICE", "voice_profiles/default_voice.wav"),
            hf_token=os.getenv("HF_TOKEN"),
        )
    if provider == "elevenlabs":
        api_key = os.getenv("ELEVENLABS_API_KEY")
        voice_id = os.getenv("ELEVENLABS_VOICE_ID")
        if not api_key or not voice_id:
            raise VoiceProviderError("ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID are required")
        return ElevenLabsProvider(
            api_key=api_key,
            voice_id=voice_id,
            model_id=os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2"),
        )
    return None


__all__ = [
    "ElevenLabsProvider",
    "PocketTTSProvider",
    "VoiceProviderError",
    "VoiceResult",
    "provider_from_env",
]
