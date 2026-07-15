#!/bin/bash
set -e

echo "🚀 AudienceOS Production Deployment"
echo "==================================="
echo ""

# Kill any existing processes
pkill -f "uvicorn app.main:app" || true
pkill -f "next dev" || true
pkill -f "next start" || true
pkill -f ngrok || true

# Start backend
echo "1. Starting Backend API..."
cd /root/repos/audienceos/backend

# Create simple .env for production
cat > .env.production << EOF
APP_ENV=production
DATABASE_URL=sqlite+aiosqlite:///./audienceos_prod.db
SECRET_KEY=$(openssl rand -hex 32)
ANTHROPIC_API_KEY=demo-mode-no-key-needed
DEBUG=false
EOF

# Use production env
export $(cat .env.production | xargs)

# Initialize database
python3 -c "
from app.database import engine
from app.models import Base
import asyncio
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init_db())
print('✅ Database initialized')
"

# Start backend
nohup python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo ""
echo "2. Starting Frontend..."
cd /root/repos/audienceos/frontend

# Build for production
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run build

# Start frontend
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for services to start
sleep 5

# Expose with ngrok
echo ""
echo "3. Exposing services to internet..."

# Start ngrok for backend
nohup ngrok http 8000 --log-level=info --log=backend-ngrok.log > /dev/null 2>&1 &
NGROK_BACKEND_PID=$!

# Start ngrok for frontend  
nohup ngrok http 3000 --log-level=info --log=frontend-ngrok.log > /dev/null 2>&1 &
NGROK_FRONTEND_PID=$!

sleep 5

# Get URLs
echo ""
echo "4. Getting public URLs..."

# Get ngrok URLs via API
BACKEND_URL=$(curl -s localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)
FRONTEND_URL=$(curl -s localhost:4041/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)

# Fallback: try alternate ports
if [ -z "$BACKEND_URL" ]; then
    BACKEND_URL=$(curl -s localhost:4042/api/tunnels 2>/dev/null | grep -o '"public_url":"https://[^"]*' | grep -o 'https://[^"]*' | head -1)
fi

echo ""
echo "✅ DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "🌐 Frontend URL: ${FRONTEND_URL:-http://localhost:3000}"
echo "🔧 Backend URL: ${BACKEND_URL:-http://localhost:8000}"
echo ""
echo "📝 Process IDs:"
echo "   Backend: $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo "   Ngrok Backend: $NGROK_BACKEND_PID"
echo "   Ngrok Frontend: $NGROK_FRONTEND_PID"
echo ""
echo "📊 Logs:"
echo "   Backend: /root/repos/audienceos/backend/backend.log"
echo "   Frontend: /root/repos/audienceos/frontend/frontend.log"
echo ""
echo "To stop all services, run:"
echo "pkill -f uvicorn && pkill -f 'next start' && pkill -f ngrok"