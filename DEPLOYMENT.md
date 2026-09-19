# 🚀 Deployment Guide

Complete guide to deploy the Pet Rescue Operations app to GitHub and run on Streamlit Cloud.

---

## Table of Contents

1. [GitHub Setup](#github-setup)
2. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
3. [Local Development](#local-development)
4. [Docker Deployment](#docker-deployment)
5. [Troubleshooting](#troubleshooting)

---

## GitHub Setup

### Step 1: Create GitHub Repository

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "🐾 Initial commit: Pet Rescue Operations with AI agents"

# Add remote repository
git remote add origin https://github.com/your-username/rescue-app.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 2: Verify Files on GitHub

Make sure these files are present:
```
✅ app.py
✅ requirements.txt
✅ README.md
✅ .env.example
✅ .gitignore
✅ pages/upload.py
✅ pages/cases.py
✅ backend/app.py
✅ backend/agents/*
✅ data/volunteers.csv
✅ data/vehicles.csv
✅ data/hospitals.csv
```

---

## Streamlit Cloud Deployment

### Step 1: Sign Up for Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub account (or create one)
3. Click **"New app"**

### Step 2: Create New App

1. **Repository**: Select `your-username/rescue-app`
2. **Branch**: `main`
3. **Main file path**: `app.py`
4. Click **"Deploy"**

### Step 3: Add Secrets

Once deployed, go to **App settings** → **Secrets**

Add this to `secrets.toml`:

```toml
# Anthropic API
ANTHROPIC_API_KEY = "sk-ant-your-key-here"

# API Configuration
API_URL = "https://rescue-api.example.com"
API_TIMEOUT = 30

# File Upload
UPLOAD_FOLDER = "uploads"
MAX_FILE_SIZE_MB = 16
```

### Step 4: Configure Backend

Since Streamlit Cloud runs only the frontend, you need a backend server:

#### Option A: Use Railway.app (Easy)

1. Go to [railway.app](https://railway.app)
2. New project → GitHub repo
3. Select the `rescue-app` repository
4. Service: Flask (auto-detected)
5. Set environment variables:
   ```
   ANTHROPIC_API_KEY=sk-ant-...
   FLASK_PORT=8000
   ```
6. Deploy!

#### Option B: Use Heroku (Legacy)

```bash
# Create Heroku app
heroku create your-app-name

# Set buildpack
heroku buildpacks:set heroku/python

# Set environment variables
heroku config:set ANTHROPIC_API_KEY=sk-ant-...

# Deploy
git push heroku main
```

#### Option C: Use AWS (Advanced)

1. Create EC2 instance (t2.micro for free tier)
2. SSH into instance
3. Clone repository and install dependencies
4. Run Flask with Gunicorn
5. Set up Nginx reverse proxy

### Step 5: Update Streamlit App Configuration

In `app.py`, update the API URL based on your deployment:

```python
# Update this in the create_case() function
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Or for production
API_URL = "https://your-backend-app.railway.app"  # or your URL
```

---

## Local Development

### Prerequisites

- Python 3.8+
- pip/conda
- Git

### Installation

```bash
# Clone repository
git clone https://github.com/your-username/rescue-app.git
cd rescue-app

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run Application

**Terminal 1 - Start Backend API**

```bash
cd backend
python app.py
```

Expected output:
```
🚀 Starting Pet Rescue API Server...
📡 Running on http://localhost:8000
```

**Terminal 2 - Start Frontend**

```bash
streamlit run app.py
```

Expected output:
```
🐾 Pet Rescue Operations
📡 Local URL: http://localhost:8501
```

Open browser to `http://localhost:8501`

---

## Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose ports
EXPOSE 8000 8501

# Create uploads directory
RUN mkdir -p uploads

# Set environment
ENV FLASK_PORT=8000
ENV STREAMLIT_PORT=8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run both services
CMD ["sh", "-c", "python backend/app.py & streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  # Frontend
  frontend:
    build: .
    ports:
      - "8501:8501"
    environment:
      - API_URL=http://backend:8000
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - backend
    volumes:
      - ./uploads:/app/uploads

  # Backend
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - FLASK_ENV=production
    volumes:
      - ./uploads:/app/uploads
      - ./data:/app/data

  # Database (Optional)
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_USER=rescue_user
      - POSTGRES_PASSWORD=secure_password
      - POSTGRES_DB=rescue_db
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### Run with Docker Compose

```bash
# Create .env file with ANTHROPIC_API_KEY
cp .env.example .env

# Build and run
docker-compose up -d

# Check logs
docker-compose logs -f

# Stop
docker-compose down
```

---

## Environment Variables

### Required
- `ANTHROPIC_API_KEY` - Your Anthropic API key

### Optional
- `FLASK_PORT` - Backend port (default: 8000)
- `STREAMLIT_PORT` - Frontend port (default: 8501)
- `API_URL` - Backend URL (default: http://localhost:8000)
- `DATABASE_URL` - PostgreSQL connection string

### Production Secrets (Never commit!)
```bash
ANTHROPIC_API_KEY=sk-ant-xxx
FLASK_SECRET_KEY=your-secret-key
DATABASE_PASSWORD=secure-password
```

---

## GitHub Actions CI/CD

### .github/workflows/deploy.yml

```yaml
name: Deploy to Streamlit Cloud

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Streamlit Cloud Deploy
        run: |
          streamlit run app.py
        env:
          STREAMLIT_CLOUD: true
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

---

## Monitoring & Logging

### Check Application Status

```bash
# Frontend
curl http://localhost:8501

# Backend
curl http://localhost:8000/health

# Logs
tail -f rescue_app.log
```

### Enable Debugging

```bash
# Backend
FLASK_DEBUG=True python backend/app.py

# Frontend
streamlit run app.py --logger.level=debug
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'streamlit'"

```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

### "ANTHROPIC_API_KEY not found"

```bash
# Check environment variable
echo $ANTHROPIC_API_KEY

# On Windows
echo %ANTHROPIC_API_KEY%

# If empty, add to .env
ANTHROPIC_API_KEY=sk-ant-your-key
```

### "Cannot connect to backend API"

```bash
# Check if backend is running
curl http://localhost:8000/health

# Start backend if needed
python backend/app.py
```

### "Port already in use"

```bash
# Kill process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql -U postgres

# Or use in-memory database (remove DATABASE_URL from .env)
```

---

## Performance Tips

1. **Caching**: Streamlit caches function results automatically
2. **Lazy Loading**: Load resources only when needed
3. **Async Processing**: Use threading for agent processing
4. **Image Optimization**: Compress photos before upload

---

## Security Checklist

- [ ] Change default passwords
- [ ] Enable HTTPS/SSL
- [ ] Use environment variables for secrets
- [ ] Validate all user inputs
- [ ] Implement rate limiting
- [ ] Enable CORS only for trusted domains
- [ ] Use strong API keys
- [ ] Rotate credentials regularly

---

## Support

- **Documentation**: See README.md
- **Issues**: GitHub Issues
- **Community**: GitHub Discussions

---

## Next Steps

After deployment:

1. ✅ Test all features thoroughly
2. ✅ Set up monitoring and alerts
3. ✅ Configure backups
4. ✅ Plan for scaling
5. ✅ Document deployment process

---

**Happy deploying! 🚀🐾**

For detailed Streamlit Cloud docs: https://docs.streamlit.io/streamlit-cloud
