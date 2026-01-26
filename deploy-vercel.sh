#!/bin/bash
set -e

echo "=== AudienceOS Vercel Deployment ==="
echo ""
echo "This script will deploy both frontend and backend to Vercel."
echo ""

# Check if already logged in
if ! vercel whoami &>/dev/null; then
    echo "Please login to Vercel first:"
    echo "Run: vercel login"
    echo ""
    echo "After logging in, run this script again."
    exit 1
fi

echo "Logged in as: $(vercel whoami)"
echo ""

# Deploy frontend
echo "1. Deploying Frontend..."
cd frontend

# Create vercel.json for frontend config
cat > vercel.json << EOF
{
  "framework": "nextjs",
  "buildCommand": "npm run build",
  "outputDirectory": ".next",
  "env": {
    "NEXT_PUBLIC_API_URL": "@audienceos-api-url"
  }
}
EOF

# Deploy with production flag
echo "Deploying frontend to Vercel..."
FRONTEND_URL=$(vercel --yes --prod 2>&1 | grep -E "https://.*\.vercel\.app" | tail -n 1 | xargs)

if [ -z "$FRONTEND_URL" ]; then
    echo "Frontend deployment failed!"
    exit 1
fi

echo "Frontend deployed to: $FRONTEND_URL"
echo ""

# Deploy backend
echo "2. Deploying Backend..."
cd ../backend

# Create vercel.json for backend (Python API)
cat > vercel.json << EOF
{
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ],
  "env": {
    "APP_ENV": "production",
    "DATABASE_URL": "@audienceos-database-url",
    "ANTHROPIC_API_KEY": "@audienceos-anthropic-key",
    "SECRET_KEY": "@audienceos-secret-key"
  }
}
EOF

# Create a minimal requirements.txt for Vercel
cat > requirements-vercel.txt << EOF
fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
sqlalchemy==2.0.23
aiosqlite==0.19.0
alembic==1.12.1
httpx==0.25.2
anthropic==0.7.8
praw==7.7.1
python-dotenv==1.0.0
EOF

echo "Deploying backend to Vercel..."
BACKEND_URL=$(vercel --yes --prod 2>&1 | grep -E "https://.*\.vercel\.app" | tail -n 1 | xargs)

if [ -z "$BACKEND_URL" ]; then
    echo "Backend deployment failed!"
    exit 1
fi

echo "Backend deployed to: $BACKEND_URL"
echo ""

# Summary
echo "=== Deployment Complete! ==="
echo ""
echo "Frontend URL: $FRONTEND_URL"
echo "Backend URL: $BACKEND_URL"
echo ""
echo "Next steps:"
echo "1. Set environment variables in Vercel dashboard"
echo "2. Update NEXT_PUBLIC_API_URL in frontend to point to backend"
echo "3. Configure database and other services"
echo ""
echo "To set env vars, run:"
echo "vercel env add ANTHROPIC_API_KEY production"
echo "vercel env add DATABASE_URL production"
echo "etc..."