#!/bin/bash

# Start DataReplicator Application (Backend + Frontend)
echo "Starting DataReplicator Application..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Start Backend FastAPI Server
echo "Starting FastAPI Backend on http://localhost:8000"
cd "$(dirname "$0")"

# Check if virtual environment exists and activate it
if [ -d "venv" ]; then
  echo "Activating virtual environment..."
  source venv/bin/activate
else
  echo "Warning: Virtual environment not found, using system Python"
fi

# Start the backend server
python -m uvicorn datareplicator.api.app:app --host 0.0.0.0 --port 8000 > logs/backend.log 2>&1 &
BACKEND_PID=$!

# Wait a bit for backend to initialize
sleep 2

# Start Frontend React Server
echo "Starting React Frontend on http://localhost:3000"
cd frontend
npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "DataReplicator is running!"
echo "- Backend: http://localhost:8000 (PID: $BACKEND_PID)"
echo "- Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
echo "- API Documentation: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to press Ctrl+C
trap "echo 'Shutting down...'; kill $BACKEND_PID; kill $FRONTEND_PID; exit" INT
wait
