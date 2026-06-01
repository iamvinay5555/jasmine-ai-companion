from pathlib import Path

from jasmine_core import MemorySystem, get_core
from skills import SkillRouter, render_skill_catalog
from voice import provider_from_env


def test_profile_is_generic():
    profile = get_core(user_display_name="Alex")
    assert "Alex" in profile.greet()
    prompt = profile.system_prompt()
    assert "private" in prompt.lower()
    assert "private_origin_story" not in prompt.lower()


def test_memory_add_search_roundtrip(tmp_path: Path):
    store = tmp_path / "memory.json"
    memory = MemorySystem(store)
    memory.add("I prefer concise reminders", category="preference")

    reloaded = MemorySystem(store)
    results = reloaded.search("concise reminders")

    assert len(results) == 1
    assert results[0].category == "preference"
    assert results[0].recall_count == 1


def test_skill_router_finds_voice_and_briefing():
    router = SkillRouter()
    assert router.route("please make a voice note").name == "voice_note"
    assert router.route("give me a schedule brief").name == "personal_briefing"
    assert router.route("plain small talk") is None


def test_skill_catalog_renders():
    catalog = render_skill_catalog()
    assert "daily_check_in" in catalog
    assert "voice_note" in catalog


def test_voice_provider_default_is_none(monkeypatch):
    monkeypatch.delenv("JASMINE_VOICE_PROVIDER", raising=False)
    assert provider_from_env() is None
