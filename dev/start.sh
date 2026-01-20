#!/bin/bash

# Navigate to the project root (assuming script is in dev/ directory)
cd "$(dirname "$0")/.."

echo "Starting ALS/FTD Research Dashboard Development Environment..."

# Ensure logs directory exists
mkdir -p logs

# Function to kill process on port
kill_port() {
    PORT=$1
    PID=$(lsof -ti :$PORT)
    if [ ! -z "$PID" ]; then
        echo "Port $PORT is in use by PID $PID. Killing..."
        kill -9 $PID
    fi
}

# Cleanup existing processes
echo "Checking for existing processes..."
kill_port 8000
kill_port 5173
kill_port 3000
kill_port 6379


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
    kill $DJANGO_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT)
trap cleanup SIGINT

# 2. Start Django Backend
echo "Starting Django Backend (0.0.0.0:8000)..."
# Using 0.0.0.0 to ensure accessibility if running on a remote server/VM
# Redirect output to console log
python3 manage.py runserver 0.0.0.0:8000 2>&1 | tee logs/console.log &
DJANGO_PID=$!

# 3. Start React Frontend
echo "Starting React Frontend..."
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

# Wait for processes using the `wait` command, 
# but simply waiting on PIDs allows the trap to catch SIGINT immediately.
wait $DJANGO_PID $FRONTEND_PID
