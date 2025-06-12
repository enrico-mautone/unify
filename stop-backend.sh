#!/bin/bash
echo "Stopping Unify Backend Services..."

# Find and kill the Entity Service (port 8081)
echo "Stopping Entity Service..."
pkill -f "uvicorn entity.entities:app --reload --port 8081"

# Find and kill the Auth Service (port 8000)
echo "Stopping Auth Service..."
pkill -f "uvicorn auth.auth:app --reload --port 8000"

echo "All services have been stopped."
