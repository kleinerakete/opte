"""Worker analysis entrypoint.

Reads feature flags from environment and selects the model implementation
to run. For now responses are simulated so the service is runnable without
external APIs.
"""
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _bool_env(name: str, default: bool = False) -> bool:
	v = os.getenv(name)
	if v is None:
		return default
	return v.lower() in ("1", "true", "yes", "on")


CLAUDE_ENABLED = _bool_env("CLAUDE_HAIKU_ENABLED", False)
CLAUDE_VERSION = os.getenv("CLAUDE_HAIKU_VERSION", "4.5")


def _fake_claude_haiku(text: str, version: str) -> str:
	words = text.split()
	first = words[0] if words else "Quiet"
	return f"{first} morning\npaper clues align\n{version} humming"


def _fake_openai(text: str) -> str:
	return f"(openai-sim) processed: {text[:200]}"


def analyze(text: str) -> dict:
	if CLAUDE_ENABLED:
		logger.info("Worker: using Claude Haiku %s", CLAUDE_VERSION)
		resp = _fake_claude_haiku(text, CLAUDE_VERSION)
		return {"model": f"claude-haiku-{CLAUDE_VERSION}", "result": resp}

	logger.info("Worker: using OpenAI-sim fallback")
	resp = _fake_openai(text)
	return {"model": "openai-sim", "result": resp}


if __name__ == "__main__":
	if len(sys.argv) > 1:
		input_text = " ".join(sys.argv[1:])
	else:
		input_text = "example puzzle text"
	out = analyze(input_text)
	print(out)