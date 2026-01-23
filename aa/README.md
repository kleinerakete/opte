PUZSCAN README

Quick start (dev):

1. Copy the sample env and enable Claude Haiku if desired:

```bash
cd aa
cp .env.sample .env
# edit .env: CLAUDE_HAIKU_ENABLED=true and CLAUDE_HAIKU_VERSION=4.5
```

2. Run with docker-compose:

```bash
docker-compose up -d --build
```

3. Test the API locally (example):

```bash
curl -X POST -H "Content-Type: application/json" -d '{"prompt":"solve this puzzle"}' http://localhost:8000/infer
```

The API and worker read `CLAUDE_HAIKU_ENABLED` and `CLAUDE_HAIKU_VERSION` from the environment and will use a simulated Claude Haiku response when enabled. If disabled and `OPENAI_API_KEY` is provided, the service currently uses a simulated OpenAI response.