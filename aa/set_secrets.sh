#!/usr/bin/env bash
# set_secrets.sh - helper to replace placeholders in .env from environment variables
ENVFILE=".env"
if [ ! -f "$ENVFILE" ]; then
  echo ".env not found"
  exit 1
fi

# Replace specific keys if environment variables provided
if [ -n "$ADMIN_SECRET" ]; then
  perl -0777 -pe "s/^ADMIN_SECRET=.*$/ADMIN_SECRET=$ADMIN_SECRET/m" -i "$ENVFILE"
fi
if [ -n "$PHOENIX_API_KEY" ]; then
  perl -0777 -pe "s/^PHOENIX_API_KEY=.*$/PHOENIX_API_KEY=$PHOENIX_API_KEY/m" -i "$ENVFILE"
fi
if [ -n "$OPENAI_API_KEY" ]; then
  perl -0777 -pe "s/^OPENAI_API_KEY=.*$/OPENAI_API_KEY=$OPENAI_API_KEY/m" -i "$ENVFILE"
fi

echo "Secrets updated in .env (ensure you secure the file)"
