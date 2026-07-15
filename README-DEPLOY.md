# AudienceOS Deployment Guide

## 🚀 Quick Deploy to Production

### Option 1: Deploy to Render (Recommended - Free Tier)

1. **Backend API**
   - Go to https://render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repo
   - Settings:
     - Root Directory: `backend`
     - Build Command: `pip install -r requirements.txt`
     - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
     - Add environment variables:
       - `DATABASE_URL`: Use Render's PostgreSQL add-on
       - `ANTHROPIC_API_KEY`: Your API key
       - `SECRET_KEY`: Generate a random string

2. **Frontend**
   - Click "New +" → "Static Site"
   - Connect same repo
   - Settings:
     - Root Directory: `frontend`
     - Build Command: `npm install && npm run build`
     - Publish Directory: `.next`
     - Add environment variable:
       - `NEXT_PUBLIC_API_URL`: Your backend URL from step 1

### Option 2: Deploy to Vercel + Railway

1. **Frontend on Vercel**
   ```bash
   cd frontend
   npx vercel
   ```

2. **Backend on Railway**
   ```bash
   cd backend
   railway login
   railway init
   railway up
   ```

### Option 3: Deploy to Heroku

1. **Create Heroku apps**
   ```bash
   heroku create audienceos-api
   heroku create audienceos-frontend
   ```

2. **Deploy Backend**
   ```bash
   cd backend
   git push heroku main
   ```

3. **Deploy Frontend**
   ```bash
   cd frontend
   git push heroku main
   ```

## 🔥 Production URLs

Once deployed, your app will be available at:

- Frontend: `https://audienceos.onrender.com` (or your chosen domain)
- Backend API: `https://audienceos-api.onrender.com`
- API Docs: `https://audienceos-api.onrender.com/docs`

## 📱 Test Your Deployment

1. Visit the frontend URL
2. Sign up for an account
3. Create your first audience
4. Generate content
5. Start making revenue!

## 💰 Revenue Checklist

- [ ] Stripe integration configured
- [ ] Pricing plans set up
- [ ] Payment webhooks active
- [ ] Email notifications working
- [ ] Analytics tracking enabled