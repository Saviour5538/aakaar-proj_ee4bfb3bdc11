#!/bin/bash
set -euo pipefail

# Start the backend in the background
echo "Starting backend in development mode..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &

# Start the frontend development server
echo "Starting frontend development server..."
cd frontend
npm run dev