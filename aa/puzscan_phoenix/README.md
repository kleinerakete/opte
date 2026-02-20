PUZSCAN Phoenix API
===================

Dieses Phoenix-Projekt stellt die API für PUZSCAN bereit: /api/upload, /api/status, /api/admin/*, /api/storage/:key

Quickstart:
1. Installiere Elixir, Erlang, PostgreSQL.
2. Setze Umgebungsvariablen (siehe config/config.exs).
3. mix deps.get
4. mix ecto.create
5. mix ecto.migrate
6. mix phx.server

Integration:
- Configure PY_WORKER_HTTP to point to your Python worker's process endpoint (e.g. http://python-worker:8000/process)
- Configure S3 credentials via AWS env vars or ExAws config

Admin:
- Use /api/admin/auth and /api/admin/update-weights for admin actions.

Hinweis: This repository is prepared to call an external Python worker for the heavy image analysis. Keep Python worker running and reachable.
