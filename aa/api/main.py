from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import logging
import os
from typing import Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PUZSCAN API")


class InferRequest(BaseModel):
    prompt: str
    client: str | None = None


def _bool_env(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.lower() in ("1", "true", "yes", "on")


CLAUDE_ENABLED = _bool_env("CLAUDE_HAIKU_ENABLED", False)
CLAUDE_VERSION = os.getenv("CLAUDE_HAIKU_VERSION", "4.5")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


def _fake_claude_haiku(prompt: str, version: str) -> str:
    # Very small deterministic haiku-style response for demonstration
    lines = []
    lines.append(f"{prompt.split()[0] if prompt.split() else 'Soft'} dawn,")
    lines.append("paper puzzles whisper,")
    lines.append(f"{version} hums beneath")
    return "\n".join(lines)


def _fake_openai_response(prompt: str) -> str:
    return f"(OpenAI-sim) Echo: {prompt[:200]}"


def call_model(prompt: str) -> Dict[str, str]:
    if CLAUDE_ENABLED:
        logger.info("Using Claude Haiku model: %s", CLAUDE_VERSION)
        return {"model": f"claude-haiku-{CLAUDE_VERSION}", "response": _fake_claude_haiku(prompt, CLAUDE_VERSION)}

    if OPENAI_API_KEY:
        logger.info("Using OpenAI (simulated) for prompt")
        return {"model": "openai-sim", "response": _fake_openai_response(prompt)}

    logger.warning("No model available: neither CLAUDE_HAIKU_ENABLED nor OPENAI_API_KEY set")
    raise HTTPException(status_code=503, detail="No model configured. Set CLAUDE_HAIKU_ENABLED or OPENAI_API_KEY.")


@app.get("/")
def root():
    return {"message": "PUZSCAN API is running", "claude_enabled": CLAUDE_ENABLED, "claude_version": CLAUDE_VERSION}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/infer")
def infer(req: InferRequest):
    result = call_model(req.prompt)
    return {"model": result["model"], "response": result["response"]}


if __name__ == "__main__":
    logger.info("Starting PUZSCAN API server on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)