#!/usr/bin/env bash
set -e
echo "PUZX Final deploy starter"
if [ ! -f .env ]; then
  echo ".env missing - copy .env.sample or edit .env"
  exit 1
fi
docker-compose build --no-cache
docker-compose up -d
echo "Services started. Run migrations for Phoenix as documented in README."
