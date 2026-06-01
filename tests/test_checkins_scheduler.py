import random
from pathlib import Path

import pytest

from checkins import CheckInGenerator, FileOutboxDelivery
from jasmine_core import MemorySystem, get_core
from scheduler import checkin_cron_job, is_valid_cron, parse_schedule_preset, render_install_instructions


def test_checkin_generation_and_file_delivery(tmp_path: Path):
    memory_path = tmp_path / "memory.json"
    history_path = tmp_path / "history.json"
    outbox_path = tmp_path / "outbox" / "checkins.jsonl"
    profile = get_core(user_display_name="Alex")
    memory = MemorySystem(memory_path)
    memory.add("I prefer short encouraging reminders", category="preference")
    generator = CheckInGenerator(history_path=history_path, rng=random.Random(7))

    message, result = generator.send(profile, memory, FileOutboxDelivery(outbox_path))

    assert result.ok is True
    assert outbox_path.exists()
    assert message.user_display_name == "Alex"
    assert message.topic
    assert "Alex" in message.text
    assert "short encouraging reminders" in message.text


def test_checkin_topic_deduplication(tmp_path: Path):
    generator = CheckInGenerator(
        history_path=tmp_path / "history.json",
        topics=("alpha", "beta"),
        min_recent_gap=1,
        rng=random.Random(1),
    )
    profile = get_core()

    first = generator.generate(profile)
    second = generator.generate(profile)

    assert first.topic != second.topic


def test_cron_schedule_presets_and_rendering():
    assert parse_schedule_preset("spontaneous") == "0 8,12,16,20,22 * * *"
    assert parse_schedule_preset("daily 09:30") == "30 9 * * *"
    assert parse_schedule_preset("every 2h") == "0 */2 * * *"
    assert is_valid_cron("15 8,20 * * *") is True

    job = checkin_cron_job(command="python demo.py --send-checkin", hours=(9, 21), minute=15)
    assert job.schedule == "15 9,21 * * *"
    assert "python demo.py --send-checkin" in job.crontab_line()
    assert "crontab" in render_install_instructions(job)


def test_invalid_cron_schedule_rejected():
    with pytest.raises(ValueError):
        parse_schedule_preset("daily 25:00")
    with pytest.raises(ValueError):
        checkin_cron_job(minute=99)
