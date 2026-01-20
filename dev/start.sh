#!/bin/bash

# Navigate to the project root (assuming script is in dev/ directory)
cd "$(dirname "$0")/.."

echo "Starting ALS/FTD Research Dashboard Development Environment..."

# Ensure logs directory exists
mkdir -p logs

# 1. Start Docker Containers
echo "Starting Docker containers (Postgres, Redis, Adminer)..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "Failed to start Docker containers. Make sure Docker is running."
    exit 1
fi
echo "Docker containers are up."


# Function to kill background processes on script exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    if [ ! -z "$DJANGO_PID" ]; then kill $DJANGO_PID 2>/dev/null; fi
    if [ ! -z "$FRONTEND_PID" ]; then kill $FRONTEND_PID 2>/dev/null; fi
    exit
}

# Trap Ctrl+C (SIGINT)
trap cleanup SIGINT

# 2. Start Django Backend
echo "Starting Django Backend (0.0.0.0:8000)..."

# Force kill any process holding port 8000
PID_8000=$(lsof -ti :8000)
if [ ! -z "$PID_8000" ]; then
    echo "Freeing port 8000 (PID $PID_8000)..."
    kill -9 $PID_8000 2>/dev/null
fi

# Redirect output to console log
python3 manage.py runserver 0.0.0.0:8000 2>&1 | tee logs/console.log &
DJANGO_PID=$!

# 3. Start React Frontend
echo "Starting React Frontend..."

# Force kill any process holding port 5173
PID_5173=$(lsof -ti :5173)
if [ ! -z "$PID_5173" ]; then
    echo "Freeing port 5173 (PID $PID_5173)..."
    kill -9 $PID_5173 2>/dev/null
fi

cd frontend
# Using --host to ensure accessibility
# Append output to console log
npm run dev -- --host 2>&1 | tee -a ../logs/console.log &
FRONTEND_PID=$!
cd ..

echo "Environment is running!"
echo "   - Django API: http://localhost:8000 (or server IP)"
echo "   - React App:  http://localhost:5173"
echo "   - Metabase:   http://localhost:3000"


echo ""
echo "Press Ctrl+C to stop servers."

# Wait for processes
wait $DJANGO_PID $FRONTEND_PID
