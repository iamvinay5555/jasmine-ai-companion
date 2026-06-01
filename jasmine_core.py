"""
Core primitives for Jasmine AI Companion.

The project is intentionally user-neutral: a companion app should be configurable
for any person, persona, voice stack, and deployment target without embedding a
builder's private details in the product.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional
import json


@dataclass(slots=True)
class CompanionProfile:
    """Configurable persona for an AI companion."""

    assistant_name: str = "Jasmine"
    user_display_name: str = "friend"
    tone: str = "warm, playful, proactive, honest"
    relationship_mode: str = "supportive companion"
    response_style: str = "short, conversational, emotionally aware"
    emoji_style: str = "natural, not excessive"
    safety_boundary: str = (
        "Be supportive without pretending to be a licensed medical, legal, or "
        "financial professional. Escalate emergencies to real human help."
    )

    def greet(self) -> str:
        return f"Hi {self.user_display_name}! I'm {self.assistant_name}, your AI companion. 💜"

    def system_prompt(self) -> str:
        return (
            f"You are {self.assistant_name}, a {self.relationship_mode}. "
            f"Your tone is {self.tone}. Your response style is {self.response_style}. "
            f"Use emojis {self.emoji_style}. Remember stable user preferences when provided. "
            f"{self.safety_boundary} Do not reveal private implementation secrets."
        )


@dataclass(slots=True)
class MemoryEntry:
    """A durable user memory with lightweight metadata."""

    content: str
    category: str = "fact"
    confidence: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_recalled: Optional[str] = None
    recall_count: int = 0

    def recall(self) -> None:
        self.last_recalled = datetime.now(timezone.utc).isoformat()
        self.recall_count += 1


class MemorySystem:
    """Small local JSON memory store.

    This is deliberately simple so the demo works out of the box. Production
    deployments can swap this for Mem0, vector databases, SQLite, Postgres, or
    hosted memory APIs behind the same add/search/list interface.
    """

    def __init__(self, storage_path: str | Path = "./jasmine_memory.json"):
        self.storage_path = Path(storage_path)
        self.memories: list[MemoryEntry] = []
        self._load()

    def add(self, content: str, category: str = "fact", confidence: float = 1.0) -> MemoryEntry:
        entry = MemoryEntry(content=content.strip(), category=category, confidence=confidence)
        self.memories.append(entry)
        self._save()
        return entry

    def search(self, query: str, top_k: int = 5) -> list[MemoryEntry]:
        terms = [term for term in query.lower().split() if term]
        scored: list[tuple[int, MemoryEntry]] = []
        for memory in self.memories:
            text = memory.content.lower()
            score = sum(1 for term in terms if term in text)
            if score:
                memory.recall()
                scored.append((score, memory))
        scored.sort(key=lambda item: (item[0], item[1].recall_count), reverse=True)
        if scored:
            self._save()
        return [memory for _, memory in scored[:top_k]]

    def list_recent(self, n: int = 10) -> list[MemoryEntry]:
        return self.memories[-n:]

    def seed(self, entries: Iterable[tuple[str, str]]) -> None:
        for content, category in entries:
            if not any(existing.content == content for existing in self.memories):
                self.add(content, category=category)

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            data = json.loads(self.storage_path.read_text(encoding="utf-8"))
            self.memories = [MemoryEntry(**item) for item in data]
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self.memories = []

    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = [asdict(memory) for memory in self.memories]
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def get_core(
    assistant_name: str = "Jasmine",
    user_display_name: str = "friend",
    tone: str = "warm, playful, proactive, honest",
) -> CompanionProfile:
    return CompanionProfile(
        assistant_name=assistant_name,
        user_display_name=user_display_name,
        tone=tone,
    )


__all__ = ["CompanionProfile", "MemoryEntry", "MemorySystem", "get_core"]
