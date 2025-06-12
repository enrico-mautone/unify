#!/bin/bash
echo "Starting Unify Backend Services..."

# Set Python path
export PYTHONPATH=$(pwd)/backend

echo "Starting Entity Service..."
(cd backend && uvicorn entity.entities:app --reload --port 8081) &

echo "Starting Auth Service..."
(cd backend && uvicorn auth.auth:app --reload --port 8000) &

echo "Both services are starting..."
echo "Entity Service will be available at http://localhost:8081"
echo "Auth Service will be available at http://localhost:8000"

# Wait for both services to finish (they run in the background)
# Press Ctrl+C to stop all services
wait
