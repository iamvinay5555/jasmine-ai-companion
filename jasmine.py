from jasmine_core import CompanionProfile, MemoryEntry, MemorySystem, get_core
from skills import CompanionSkill, DEFAULT_SKILLS, SkillRouter, render_skill_catalog
from voice import ElevenLabsProvider, PocketTTSProvider, VoiceProviderError, VoiceResult, provider_from_env

__version__ = "1.1.0"

# Backwards-compatible alias for people importing `Jasmine` from the first demo.
Jasmine = CompanionProfile

__all__ = [
    "CompanionProfile",
    "CompanionSkill",
    "DEFAULT_SKILLS",
    "ElevenLabsProvider",
    "Jasmine",
    "MemoryEntry",
    "MemorySystem",
    "PocketTTSProvider",
    "SkillRouter",
    "VoiceProviderError",
    "VoiceResult",
    "get_core",
    "provider_from_env",
    "render_skill_catalog",
]
