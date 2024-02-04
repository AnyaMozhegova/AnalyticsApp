#!/bin/bash

echo "Running migrations..."
python run_migrations.py

exec "$@"
