#!/usr/bin/env python3
"""Terminal demo for Jasmine AI Companion.

The demo is intentionally generic: it shows how a configurable companion can use
persona, memory, skills, and optional voice providers without embedding any
private user story or personal details.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

from jasmine_core import CompanionProfile, MemorySystem, get_core
from skills import SkillRouter, render_skill_catalog
from voice import VoiceProviderError, provider_from_env

try:  # Optional dependency for local LLM responses.
    import ollama  # type: ignore

    OLLAMA_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on local environment
    OLLAMA_AVAILABLE = False


class JasmineApp:
    """Small terminal interface for the companion platform."""

    def __init__(self, profile: CompanionProfile, memory_path: Path):
        self.profile = profile
        self.memory = MemorySystem(memory_path)
        self.router = SkillRouter()
        self.session_history: list[dict[str, str]] = []
        self.memory.seed(
            (
                ("The companion should ask before taking external side effects.", "safety"),
                ("Voice notes can use PocketTTS locally or ElevenLabs for expressive cloud audio.", "capability"),
            )
        )

    def welcome(self) -> None:
        print("=" * 72)
        print("🌸 JASMINE AI COMPANION — reusable AI companion platform demo 🌸")
        print("=" * 72)
        print(self.profile.greet())
        print("This demo includes persona, memory, skill routing, and optional voice adapters.")
        print("Commands: skills, memory, recall <topic>, voice <text>, quit")
        print()

    def generate_response(self, user_input: str) -> str:
        routed_skill = self.router.route(user_input)
        memories = self.memory.search(user_input, top_k=3)
        memory_context = "; ".join(memory.content for memory in memories) or "No relevant durable memories yet."
        skill_context = (
            f"Relevant skill: {routed_skill.name} — {routed_skill.description}"
            if routed_skill
            else "No specific skill route; answer conversationally."
        )
        system_prompt = (
            self.profile.system_prompt()
            + f"\nMemory context: {memory_context}\n{skill_context}\n"
            + "Keep the reply useful, general-purpose, and suitable for a consumer app demo."
        )

        if OLLAMA_AVAILABLE:
            try:
                response = ollama.chat(
                    model="llama3.2",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        *self.session_history[-8:],
                        {"role": "user", "content": user_input},
                    ],
                )
                return response["message"]["content"]
            except Exception:
                pass

        return self._fallback_response(user_input, routed_skill is not None)

    def _fallback_response(self, user_input: str, has_skill: bool) -> str:
        lower = user_input.lower()
        if any(word in lower for word in ("hello", "hi", "hey")):
            return f"Hey {self.profile.user_display_name}! I’m here — what would make today easier? 💜"
        if "voice" in lower or "audio" in lower:
            return "I can generate voice notes when PocketTTS or ElevenLabs is configured. Try: voice You’ve got this."
        if "remember" in lower or "recall" in lower:
            memories = self.memory.search(user_input, top_k=3)
            if memories:
                return "I found these relevant memories: " + "; ".join(m.content for m in memories)
            return "I don’t have that stored yet. Tell me a stable preference and I’ll remember it."
        if any(word in lower for word in ("sad", "tired", "stressed", "overwhelmed")):
            return "I’m with you. Let’s make it smaller: one breath, one sip of water, one next step. 💜"
        if has_skill:
            skill = self.router.route(user_input)
            return f"I’d route that to the {skill.name} skill: {skill.description}"
        return "Tell me a little more — I can remember preferences, make a plan, or turn this into a voice note."

    def run_scripted(self, prompts: Iterable[str]) -> None:
        self.welcome()
        for prompt in prompts:
            print(f"User: {prompt}")
            self._handle_input(prompt)

    def run_interactive(self) -> None:
        self.welcome()
        while True:
            try:
                user_input = input(f"{self.profile.user_display_name}: ").strip()
            except (EOFError, KeyboardInterrupt):
                print(f"\n{self.profile.assistant_name}: Bye for now 💜")
                break
            if not user_input:
                continue
            if user_input.lower() == "quit":
                print(f"{self.profile.assistant_name}: See you soon 💜")
                break
            self._handle_input(user_input)

    def _handle_input(self, user_input: str) -> None:
        command, _, argument = user_input.partition(" ")
        if command.lower() == "skills":
            print(render_skill_catalog())
            return
        if command.lower() == "memory":
            self._print_memory()
            return
        if command.lower() == "recall":
            self._print_recall(argument or user_input)
            return
        if command.lower() == "voice":
            self._voice(argument or "You’ve got this.")
            return

        self._extract_memory_candidates(user_input)
        self.session_history.append({"role": "user", "content": user_input})
        response = self.generate_response(user_input)
        print(f"{self.profile.assistant_name}: {response}")
        self.session_history.append({"role": "assistant", "content": response})

    def _print_memory(self) -> None:
        print("Stored memories:")
        for memory in self.memory.list_recent(10):
            print(f"- [{memory.category}] {memory.content}")

    def _print_recall(self, query: str) -> None:
        memories = self.memory.search(query, top_k=5)
        if not memories:
            print("No matching memories yet.")
            return
        print("Relevant memories:")
        for memory in memories:
            print(f"- [{memory.category}] {memory.content}")

    def _voice(self, text: str) -> None:
        try:
            provider = provider_from_env()
            if provider is None:
                print("Voice provider not configured. Set JASMINE_VOICE_PROVIDER=pockettts or elevenlabs.")
                return
            result = provider.synthesize(text, Path("./audio_cache/demo_voice_output.wav"))
            print(f"Generated voice with {result.provider}: {result.output_path}")
        except VoiceProviderError as exc:
            print(f"Voice generation unavailable: {exc}")

    def _extract_memory_candidates(self, text: str) -> None:
        lower = text.lower()
        indicators = ("i like", "i love", "i prefer", "my name is", "i live", "remember that")
        if any(indicator in lower for indicator in indicators):
            self.memory.add(text, category="user_preference", confidence=0.75)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the Jasmine AI Companion terminal demo.")
    parser.add_argument("--assistant-name", default="Jasmine")
    parser.add_argument("--user", default="friend", help="Display name for the demo user")
    parser.add_argument("--memory", default="./jasmine_memory.json", help="Path to the local JSON memory store")
    parser.add_argument("--scripted", action="store_true", help="Run a deterministic scripted demo instead of interactive mode")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    profile = get_core(assistant_name=args.assistant_name, user_display_name=args.user)
    app = JasmineApp(profile=profile, memory_path=Path(args.memory))
    if args.scripted:
        app.run_scripted(
            (
                "hello",
                "I prefer short encouraging reminders",
                "skills",
                "recall reminders",
                "voice You are doing better than you think.",
            )
        )
    else:
        app.run_interactive()


if __name__ == "__main__":
    main()
