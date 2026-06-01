from checkins import CheckInGenerator, CheckInMessage, DeliveryResult, FileOutboxDelivery
from jasmine_core import CompanionProfile, MemoryEntry, MemorySystem, get_core
from scheduler import CronJob, checkin_cron_job, parse_schedule_preset, render_install_instructions
from skills import CompanionSkill, DEFAULT_SKILLS, SkillRouter, render_skill_catalog
from voice import ElevenLabsProvider, PocketTTSProvider, VoiceProviderError, VoiceResult, provider_from_env

__version__ = "1.2.0"

# Backwards-compatible alias for people importing `Jasmine` from the first demo.
Jasmine = CompanionProfile

__all__ = [
    "CompanionProfile",
    "CompanionSkill",
    "CheckInGenerator",
    "CheckInMessage",
    "CronJob",
    "DEFAULT_SKILLS",
    "DeliveryResult",
    "ElevenLabsProvider",
    "FileOutboxDelivery",
    "Jasmine",
    "MemoryEntry",
    "MemorySystem",
    "PocketTTSProvider",
    "SkillRouter",
    "VoiceProviderError",
    "VoiceResult",
    "checkin_cron_job",
    "get_core",
    "parse_schedule_preset",
    "provider_from_env",
    "render_install_instructions",
    "render_skill_catalog",
]
