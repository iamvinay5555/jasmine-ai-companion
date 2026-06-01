"""Cron schedule helpers for companion jobs."""

from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class CronJob:
    """A portable cron job definition."""

    name: str
    schedule: str
    command: str
    description: str = ""

    def crontab_line(self) -> str:
        comment = f" # {self.name}" if self.name else ""
        return f"{self.schedule} {self.command}{comment}"


def checkin_cron_job(
    command: str = "python demo.py --send-checkin",
    hours: tuple[int, ...] = (8, 12, 16, 20, 22),
    minute: int = 0,
    name: str = "jasmine-spontaneous-checkin",
) -> CronJob:
    """Build a cron job for spontaneous companion check-ins."""

    if not 0 <= minute <= 59:
        raise ValueError("minute must be between 0 and 59")
    if not hours or any(hour < 0 or hour > 23 for hour in hours):
        raise ValueError("hours must contain values from 0 through 23")
    hour_field = ",".join(str(hour) for hour in sorted(set(hours)))
    return CronJob(
        name=name,
        schedule=f"{minute} {hour_field} * * *",
        command=command,
        description="Send a spontaneous AI companion check-in at selected hours.",
    )


def parse_schedule_preset(preset: str) -> str:
    """Convert a friendly schedule preset into a cron expression.

    Supported forms:
    - spontaneous: 0 8,12,16,20,22 * * *
    - hourly: 0 * * * *
    - daily HH:MM
    - every Nh, for example every 2h
    - raw five-field cron expressions
    """

    value = preset.strip().lower()
    if value == "spontaneous":
        return checkin_cron_job().schedule
    if value == "hourly":
        return "0 * * * *"
    daily = re.fullmatch(r"daily\s+(\d{1,2}):(\d{2})", value)
    if daily:
        hour = int(daily.group(1))
        minute = int(daily.group(2))
        if hour > 23 or minute > 59:
            raise ValueError("daily schedule must use HH:MM in 24-hour time")
        return f"{minute} {hour} * * *"
    every = re.fullmatch(r"every\s+(\d{1,2})h", value)
    if every:
        step = int(every.group(1))
        if not 1 <= step <= 23:
            raise ValueError("hour step must be between 1 and 23")
        return f"0 */{step} * * *"
    if is_valid_cron(value):
        return value
    raise ValueError(f"Unsupported schedule preset: {preset}")


def is_valid_cron(expression: str) -> bool:
    """Lightweight validation for standard five-field cron expressions."""

    parts = expression.split()
    if len(parts) != 5:
        return False
    return all(_valid_field(part) for part in parts)


def _valid_field(field: str) -> bool:
    return bool(re.fullmatch(r"[\d*/,\-]+", field))


def render_install_instructions(job: CronJob) -> str:
    """Return copy-paste instructions for installing a cron job."""

    return "\n".join(
        (
            f"# {job.description or job.name}",
            "(crontab -l 2>/dev/null; echo " + repr(job.crontab_line()) + ") | crontab -",
        )
    )


__all__ = [
    "CronJob",
    "checkin_cron_job",
    "is_valid_cron",
    "parse_schedule_preset",
    "render_install_instructions",
]
