#!/bin/bash
set -euo pipefail

# Run database migrations
echo "Running database migrations..."
alembic upgrade head || { echo "Database migration failed. Exiting."; exit 1; }

# Start the backend server
echo "Starting backend server..."
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000