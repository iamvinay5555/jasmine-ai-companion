# Jasmine AI Companion 🌸

A reusable AI companion starter app with configurable persona, durable memory,
skill routing, proactive check-in concepts, and optional voice generation through
PocketTTS or ElevenLabs.

This repository is written as a general product scaffold. It does not embed any
private user details, relationship story, API keys, or local machine paths. A
team can fork it, configure their own persona and voice providers, and build a
consumer-ready companion experience on top of it.

## What the app demonstrates

- **Configurable companion persona** — name, user display name, tone, response
  style, relationship mode, and safety boundary are runtime settings.
- **Durable memory layer** — a local JSON memory store with add/search/list
  operations; simple enough for a demo, replaceable with Mem0, Postgres, SQLite,
  or a vector database in production.
- **Skill/application catalog** — built-in modules for check-ins, memory recall,
  voice notes, personal briefings, wellbeing nudges, and creative partnership.
- **Voice provider adapters** — PocketTTS for local/free voice cloning and
  ElevenLabs for expressive cloud-generated audio.
- **Terminal demo** — deterministic scripted mode for reviewers plus an
  interactive mode for local exploration.
- **Safety-conscious defaults** — no external side effects without explicit
  configuration, no secrets in code, and clear non-clinical wellbeing boundaries.

## Architecture

```text
┌──────────────────────────────────────────────────────────────┐
│                    Jasmine AI Companion                      │
│              configurable companion application              │
├─────────────────┬──────────────────┬─────────────────────────┤
│ Persona Profile │ Durable Memory   │ Skill Router            │
│ tone + safety   │ JSON demo store  │ check-ins/briefings/etc │
├─────────────────┴──────────────────┴─────────────────────────┤
│ Voice Providers: PocketTTS local clone | ElevenLabs cloud TTS │
├──────────────────────────────────────────────────────────────┤
│ Interfaces: terminal today; web/mobile/messaging ready later  │
└──────────────────────────────────────────────────────────────┘
```

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python demo.py --scripted
```

Interactive mode:

```bash
python demo.py --user Alex
```

Useful commands inside the demo:

```text
skills
memory
recall reminders
voice You are doing better than you think.
quit
```

## Voice setup

Voice is optional. The app runs without audio tooling and will explain what is
missing when the `voice` command is used.

### PocketTTS local voice cloning

PocketTTS is best when you want local generation, no per-request cloud TTS cost,
and full control over the reference voice sample.

```bash
export JASMINE_VOICE_PROVIDER=pockettts
export POCKET_TTS_BINARY=/absolute/path/to/pocket-tts
export POCKET_TTS_VOICE=/absolute/path/to/reference_voice.wav
export HF_TOKEN=your_huggingface_token_if_required
python demo.py
```

Then in the demo:

```text
voice Take a breath. One step at a time.
```

### ElevenLabs expressive audio

ElevenLabs is best for polished, expressive, special-purpose audio where a cloud
provider is acceptable.

```bash
export JASMINE_VOICE_PROVIDER=elevenlabs
export ELEVENLABS_API_KEY=your_api_key
export ELEVENLABS_VOICE_ID=your_voice_id
export ELEVENLABS_MODEL_ID=eleven_multilingual_v2
python demo.py
```

The ElevenLabs adapter writes an MP3-compatible response body to the configured
output path. Messaging apps may need an additional conversion step such as Opus
OGG for voice-bubble delivery.

## Skill/application modules

The default catalog in `skills.py` includes:

- `daily_check_in` — proactive morning/lunch/evening messages.
- `memory_recall` — user preferences and stable context.
- `voice_note` — PocketTTS or ElevenLabs voice generation.
- `personal_briefing` — calendar/task/news-style summaries.
- `wellbeing_nudge` — hydration, break, movement, and reflection nudges.
- `creative_partner` — writing, brainstorming, recommendations, and playful help.

The demo uses a simple keyword router so it works offline. Production versions
can replace that router with embeddings, tool-calling, or workflow orchestration
without changing the public skill catalog.

## Files

```text
jasmine_core.py   Persona, memory entries, and JSON memory store
demo.py           Terminal application and scripted reviewer demo
skills.py         Skill catalog and lightweight router
voice.py          PocketTTS and ElevenLabs provider adapters
jasmine.py        Public exports for package-style imports
tests/            Smoke tests for core behavior
```

## Production roadmap

This scaffold is intentionally small, but it is designed to grow into a real
super-app:

1. Add a web/mobile UI for onboarding, memory review, and voice settings.
2. Replace JSON memory with a permissioned database and user-controlled deletion.
3. Add scheduler-backed proactive check-ins with quiet hours.
4. Add messaging integrations such as Telegram, Discord, email, or SMS.
5. Add explicit consent screens before external actions like sending messages.
6. Add encrypted secret storage for provider keys.
7. Add observability, rate limits, and audit logs.

## Privacy and safety

- No personal details are hardcoded.
- No API keys are committed.
- Local memory stays in the configured JSON file.
- External voice providers are only called when explicitly configured.
- Wellbeing nudges are supportive but not medical care.

## License

MIT — build your own companion, safely and beautifully.
