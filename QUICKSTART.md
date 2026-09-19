# ⚡ Quick Start (5 Minutes)

Get the Pet Rescue app running in 5 minutes!

---

## Step 1: Clone (1 min)

```bash
git clone https://github.com/your-username/rescue-app.git
cd rescue-app
```

## Step 2: Setup (2 min)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux
# or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

## Step 3: Add API Key (1 min)

Edit `.env` and add your Anthropic API key:

```env
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
```

Get your key from: https://console.anthropic.com/api/keys

## Step 4: Run (1 min)

Open **two terminal windows**:

### Terminal 1 - Backend API
```bash
cd backend
python app.py
```

### Terminal 2 - Frontend
```bash
streamlit run app.py
```

## Step 5: Open Browser

Go to: **http://localhost:8501** 🎉

---

## What You Can Do

1. **📸 Upload** - Report an injured animal with a photo
2. **🤖 Watch** - See 4 AI agents process the case in real-time
3. **👥 Track** - View matched rescue team details

---

## Troubleshooting Quick Fixes

### API Key Error
```bash
# Make sure .env has your key
cat .env | grep ANTHROPIC_API_KEY

# If empty, get one from:
# https://console.anthropic.com/api/keys
```

### Backend not running?
```bash
# Check port 8000 is not in use
curl http://localhost:8000/health

# If fails, something else is using port 8000
# Use different port in backend/app.py:
# app.run(port=8001)
```

### Frontend shows "Connection Error"?
```bash
# Make sure both are running:
# Terminal 1: python backend/app.py
# Terminal 2: streamlit run app.py
```

---

## Demo Without API Key

Want to test without Anthropic API?

Comment out in `backend/agents/condition_agent.py`:
```python
# result = json.loads(response_text)
# Instead use mock data:
result = {
    "species": "Dog",
    "injury_type": "Fracture",
    "severity": "High",
    "condition_notes": "Right front leg appears broken"
}
```

---

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Explore the code in `backend/agents/`

---

**That's it! You're ready to rescue animals! 🐾**
