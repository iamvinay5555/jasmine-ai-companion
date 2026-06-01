"""Skill/application modules for a reusable AI companion."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True, slots=True)
class CompanionSkill:
    """A capability the companion can advertise and route to."""

    name: str
    description: str
    examples: tuple[str, ...]
    handler_hint: str


DEFAULT_SKILLS: tuple[CompanionSkill, ...] = (
    CompanionSkill(
        name="daily_check_in",
        description="Send thoughtful proactive messages based on time of day, mood, and user preferences.",
        examples=("morning encouragement", "lunch reminder", "evening wind-down"),
        handler_hint="scheduler + LLM prompt + notification channel",
    ),
    CompanionSkill(
        name="memory_recall",
        description="Remember stable preferences, routines, names, and long-running goals across sessions.",
        examples=("favorite breakfast", "preferred communication style", "project context"),
        handler_hint="local JSON for demo; Mem0/vector DB/Postgres in production",
    ),
    CompanionSkill(
        name="voice_note",
        description="Generate voice notes through local PocketTTS or cloud ElevenLabs providers.",
        examples=("supportive voice memo", "celebration clip", "accessibility readout"),
        handler_hint="voice provider adapter selected by config",
    ),
    CompanionSkill(
        name="personal_briefing",
        description="Prepare concise briefings from calendar, tasks, learning goals, and selected news sources.",
        examples=("morning plan", "travel summary", "project standup"),
        handler_hint="connectors + summarizer + delivery template",
    ),
    CompanionSkill(
        name="wellbeing_nudge",
        description="Offer non-clinical nudges for hydration, breaks, movement, reflection, and sleep hygiene.",
        examples=("drink water", "take a walk", "journal prompt"),
        handler_hint="rules + user preferences + safety boundaries",
    ),
    CompanionSkill(
        name="creative_partner",
        description="Help write messages, brainstorm ideas, recommend movies, create scripts, and role-play scenarios.",
        examples=("draft a birthday note", "make me laugh", "space movie recommendations"),
        handler_hint="LLM prompt profiles + optional media generation tools",
    ),
)


class SkillRouter:
    """Tiny keyword router used by the terminal demo.

    Real deployments can replace this with embeddings, tool-calling, or workflow
    orchestration while keeping the same skill catalog.
    """

    def __init__(self, skills: tuple[CompanionSkill, ...] = DEFAULT_SKILLS):
        self.skills = skills

    def list_skills(self) -> tuple[CompanionSkill, ...]:
        return self.skills

    def route(self, text: str) -> CompanionSkill | None:
        lower = text.lower()
        keyword_map: dict[str, str] = {
            "remember": "memory_recall",
            "recall": "memory_recall",
            "voice": "voice_note",
            "audio": "voice_note",
            "check in": "daily_check_in",
            "remind": "daily_check_in",
            "brief": "personal_briefing",
            "schedule": "personal_briefing",
            "water": "wellbeing_nudge",
            "break": "wellbeing_nudge",
            "idea": "creative_partner",
            "write": "creative_partner",
            "movie": "creative_partner",
        }
        for keyword, skill_name in keyword_map.items():
            if keyword in lower:
                return next(skill for skill in self.skills if skill.name == skill_name)
        return None


def render_skill_catalog(skills: tuple[CompanionSkill, ...] = DEFAULT_SKILLS) -> str:
    lines = ["Available companion skills:"]
    for skill in skills:
        examples = ", ".join(skill.examples)
        lines.append(f"- {skill.name}: {skill.description} Examples: {examples}.")
    return "\n".join(lines)


__all__ = ["CompanionSkill", "DEFAULT_SKILLS", "SkillRouter", "render_skill_catalog"]
