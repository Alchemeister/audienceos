#!/bin/bash
set -e

echo "🚀 AudienceOS Quick Deploy"
echo "========================="
echo ""

# Kill any existing processes
pkill -f "uvicorn" || true
pkill -f "next" || true

# Backend setup
echo "1. Starting Backend..."
cd /root/repos/audienceos/backend

# Activate venv
source venv/bin/activate

# Set minimal env vars
export DATABASE_URL="sqlite+aiosqlite:///./audienceos.db"
export APP_ENV="production"
export SECRET_KEY="temporary-secret-key-for-demo"
export ANTHROPIC_API_KEY="sk-demo"

# Start backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend
sleep 3

# Frontend setup
echo ""
echo "2. Starting Frontend..."
cd /root/repos/audienceos/frontend

# Set API URL
export NEXT_PUBLIC_API_URL="http://localhost:8000"

# Build and start
npm run build
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

# Wait for services
sleep 5

echo ""
echo "3. Testing services..."
curl -s http://localhost:8000/health || echo "Backend not responding"
curl -s http://localhost:3000 || echo "Frontend not responding"

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "====================="
echo ""
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "To expose publicly, run:"
echo "ngrok http 3000  # For frontend"
echo "ngrok http 8000  # For backend (in another terminal)"