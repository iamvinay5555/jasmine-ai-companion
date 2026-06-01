"""Spontaneous check-in generation and delivery.

The implementation is intentionally provider-neutral. A production app can route
messages to push notifications, Telegram, Discord, email, SMS, or in-app inboxes.
The default demo delivery writes JSON Lines to a local outbox so reviewers can
see a real side effect without needing external credentials.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import json
import random

from jasmine_core import CompanionProfile, MemoryEntry, MemorySystem


DEFAULT_TOPICS: tuple[str, ...] = (
    "encouragement",
    "curiosity",
    "focus",
    "gratitude",
    "creativity",
    "movement",
    "hydration",
    "reflection",
    "learning",
    "rest",
    "nature",
    "music",
    "books",
    "travel",
    "food",
    "technology",
)


@dataclass(frozen=True, slots=True)
class CheckInMessage:
    """A generated spontaneous check-in."""

    assistant_name: str
    user_display_name: str
    topic: str
    text: str
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True, slots=True)
class DeliveryResult:
    """Result returned by a delivery backend."""

    ok: bool
    destination: str
    detail: str


class FileOutboxDelivery:
    """Delivery backend that appends messages to a local JSONL outbox."""

    def __init__(self, outbox_path: str | Path = "./outbox/checkins.jsonl"):
        self.outbox_path = Path(outbox_path)

    def send(self, message: CheckInMessage) -> DeliveryResult:
        self.outbox_path.parent.mkdir(parents=True, exist_ok=True)
        with self.outbox_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(asdict(message), ensure_ascii=False) + "\n")
        return DeliveryResult(True, str(self.outbox_path), "Appended check-in to local outbox")


class CheckInGenerator:
    """Generate fresh-feeling check-ins with topic deduplication."""

    def __init__(
        self,
        history_path: str | Path = "./checkin_history.json",
        topics: tuple[str, ...] = DEFAULT_TOPICS,
        min_recent_gap: int = 8,
        rng: random.Random | None = None,
    ):
        self.history_path = Path(history_path)
        self.topics = topics
        self.min_recent_gap = min_recent_gap
        self.rng = rng or random.Random()

    def generate(self, profile: CompanionProfile, memory: MemorySystem | None = None) -> CheckInMessage:
        topic = self._pick_topic()
        memories = memory.list_recent(3) if memory else []
        text = self._render_message(profile, topic, memories)
        self._save_topic(topic)
        return CheckInMessage(
            assistant_name=profile.assistant_name,
            user_display_name=profile.user_display_name,
            topic=topic,
            text=text,
        )

    def send(
        self,
        profile: CompanionProfile,
        memory: MemorySystem | None = None,
        delivery: FileOutboxDelivery | None = None,
    ) -> tuple[CheckInMessage, DeliveryResult]:
        message = self.generate(profile, memory)
        result = (delivery or FileOutboxDelivery()).send(message)
        return message, result

    def _pick_topic(self) -> str:
        history = self._load_history()
        recent = set(history[-self.min_recent_gap :])
        candidates = [topic for topic in self.topics if topic not in recent]
        if not candidates:
            candidates = list(self.topics)
        return self.rng.choice(candidates)

    def _load_history(self) -> list[str]:
        if not self.history_path.exists():
            return []
        try:
            data = json.loads(self.history_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return []
        if not isinstance(data, list):
            return []
        return [str(item) for item in data]

    def _save_topic(self, topic: str) -> None:
        history = self._load_history()
        history.append(topic)
        self.history_path.parent.mkdir(parents=True, exist_ok=True)
        self.history_path.write_text(json.dumps(history[-100:], indent=2), encoding="utf-8")

    def _render_message(
        self,
        profile: CompanionProfile,
        topic: str,
        memories: list[MemoryEntry],
    ) -> str:
        memory_hint = self._memory_hint(memories)
        templates = {
            "encouragement": "Tiny check-in: you do not need to solve the whole day at once. Pick one useful next step and let that be enough.",
            "curiosity": "Random curiosity spark: ask one better question today. Good questions quietly unlock better decisions.",
            "focus": "Focus nudge: close one loop before opening three more. Your future self will absolutely notice.",
            "gratitude": "Quick gratitude pause: name one thing that is already working. Momentum likes being noticed.",
            "creativity": "Creative spark: write the messy first version. Polished ideas usually start as brave little drafts.",
            "movement": "Body check: stand up, roll your shoulders, and give your brain a little oxygen refill.",
            "hydration": "Gentle water reminder: a few sips now is a tiny act of maintenance for the whole system.",
            "reflection": "Reflection ping: what is one thing you can make simpler today? Simpler is often kinder.",
            "learning": "Learning nudge: capture one useful thing you learned today before it evaporates.",
            "rest": "Rest reminder: recovery is not laziness; it is part of the operating system.",
            "nature": "Nature thought: even five minutes of sky, trees, or fresh air can reset the mental weather.",
            "music": "Music check-in: one good song can change the texture of the next ten minutes.",
            "books": "Bookish nudge: read one page, not one chapter. Tiny doors still open into big rooms.",
            "travel": "Travel-brain moment: look at your routine like a visitor would. Something ordinary might become interesting again.",
            "food": "Food check: future-you deserves decent fuel, not just whatever is closest to the keyboard.",
            "technology": "Tech thought: automation is best when it gives a human more space to be human.",
        }
        base = templates.get(topic, templates["encouragement"])
        return f"Hey {profile.user_display_name}, {base}{memory_hint} — {profile.assistant_name}"

    @staticmethod
    def _memory_hint(memories: list[MemoryEntry]) -> str:
        if not memories:
            return ""
        best = memories[-1].content.rstrip(".")
        return f" I’m keeping your context in mind: {best}."


__all__ = [
    "CheckInGenerator",
    "CheckInMessage",
    "DEFAULT_TOPICS",
    "DeliveryResult",
    "FileOutboxDelivery",
]
