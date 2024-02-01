#!/bin/sh

mkdir -p /root/.config/gcloud
echo "$MONGO_DB_KEY_BASE64" | base64 -d > /backend/db.pem

exec "$@"
