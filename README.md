# 🐾 Pet Rescue Operations - AI-Powered Animal Rescue System

A complete AI-powered application for coordinating animal rescue operations using multi-agent systems. Upload an animal photo and the system automatically analyzes the condition, assesses priority, finds the best rescue team, and dispatches them.

**Live Demo**: Soon on Streamlit Cloud ☁️

---

## ✨ Features

- 📸 **Citizen Photo Upload** - Citizens report animals with photo + location
- 🤖 **Multi-Agent System** - 4 AI agents work together:
  - **Condition Agent** (🔍) - Analyzes animal condition using Claude Vision
  - **Priority Agent** (🚨) - Assesses urgency level
  - **Resource Finder** (🎯) - Matches best volunteer, vehicle, hospital
  - **Coordinator** (👥) - Dispatches rescue team
- 📍 **Geolocation Matching** - Finds nearest resources using Haversine formula
- 📊 **Live Dashboard** - Track agent progress in real-time
- 🐾 **Pet-Friendly UI** - Beautiful, intuitive interface
- 🌍 **10 City Coverage** - Bangalore, Mumbai, Delhi, Hyderabad + 6 more

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Streamlit Frontend                         │
│  (Pet-friendly UI with real-time agent tracking)        │
└──────────────────┬──────────────────────────────────────┘
                   │
                   │ HTTP/REST
                   ▼
┌─────────────────────────────────────────────────────────┐
│           Flask Backend API                             │
│  • Case Management                                       │
│  • Agent Orchestration                                   │
│  • Resource Matching                                     │
└──────────────────┬──────────────────────────────────────┘
                   │
        ┌──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
    │Condition│ │Priority│ │Resource│ │Coord   │
    │ Agent  │ │ Agent  │ │Finder  │ │Agent   │
    │(Claude │ │        │ │(Match) │ │(Notify)│
    │Vision) │ │        │ │        │ │        │
    └────────┘ └────────┘ └────────┘ └────────┘
        │          │          │          │
        └──────────┼──────────┼──────────┘
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
    ┌──────────────┐   ┌──────────────┐
    │  PostgreSQL  │   │  File Store  │
    │  Database    │   │  (Photos)    │
    └──────────────┘   └──────────────┘
```

---

## 📁 Project Structure

```
rescue-app/
├── app.py                    # Main Streamlit entry point
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── .env.example              # Environment variables template
│
├── pages/
│   ├── upload.py            # Citizen report upload page
│   └── cases.py             # Case tracking dashboard
│
├── backend/
│   ├── app.py               # Flask API server
│   ├── agents/
│   │   ├── condition_agent.py
│   │   ├── priority_agent.py
│   │   ├── resource_finder_agent.py
│   │   ├── coordinator_agent.py
│   │   └── __init__.py
│   └── database/
│       ├── db.py            # Database layer
│       └── __init__.py
│
├── data/
│   ├── volunteers.csv       # 30 volunteers across 10 cities
│   ├── vehicles.csv         # 30 rescue vehicles
│   └── hospitals.csv        # 30 veterinary hospitals
│
└── config/
    ├── settings.py          # Configuration
    └── .env                 # Environment variables
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip or conda
- PostgreSQL (optional, uses in-memory DB for demo)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/rescue-app.git
cd rescue-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Create Environment File

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:
```env
# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Flask
FLASK_ENV=development
FLASK_PORT=8000

# Streamlit
STREAMLIT_PORT=8501

# Optional: PostgreSQL
DATABASE_URL=postgresql://user:password@localhost/rescue_db
```

### 4. Start Backend API

```bash
cd backend
python app.py
```

You should see:
```
🚀 Starting Pet Rescue API Server...
📡 Running on http://localhost:8000
```

### 5. Start Streamlit Frontend (in new terminal)

```bash
streamlit run app.py
```

You should see:
```
🐾 Pet Rescue Operations
📡 Local URL: http://localhost:8501
```

Open your browser to `http://localhost:8501`

---

## 📖 Usage

### For Citizens (Report Animal)

1. Go to **📤 Upload** page
2. Take/upload a photo of the animal
3. Enter your details:
   - Your name
   - Phone number
   - Location (latitude, longitude)
   - Street address/landmarks
4. Click **✅ Create Case & Start Rescue**
5. Watch the **🤖 Agent Progress** in real-time!

### For Rescue Coordinators (Track Cases)

1. Go to **📋 Cases** page
2. See all active cases with:
   - Agent processing status
   - Matched volunteer/vehicle/hospital
   - Match quality score
   - Contact details for all resources
3. Monitor rescue progress until completion

---

## 🤖 How Agents Work

### Step 1: 🔍 Condition Agent
```
Input: Animal photo
↓
Claude Vision API analyzes the image
↓
Output: 
  - Species (dog, cat, bird, reptile, etc.)
  - Injury type (fracture, poisoning, etc.)
  - Severity (Critical/High/Medium/Low)
  - Condition notes
```

### Step 2: 🚨 Priority Agent
```
Input: Condition analysis
↓
Assesses urgency based on:
  - Severity level
  - Species (endangered?)
  - Injury type (bleeding, poisoning?)
↓
Output: 
  - Priority level
  - Priority score (0-100)
  - Reasoning
```

### Step 3: 🎯 Resource Finder Agent
```
Input: Location + condition + priority
↓
Finds nearest using Haversine formula:
  - Volunteers (within 15km)
  - Vehicles (within 20km)  
  - Hospitals (within 25km)
↓
Scores based on:
  - Skills/equipment match
  - Distance
  - Availability
  - Specialization
↓
Output:
  - Best volunteer
  - Best vehicle
  - Best hospital
  - Matching score (0-100)
```

### Step 4: 👥 Coordinator Agent
```
Input: Matched resources
↓
Creates mission and notifies:
  - SMS to volunteer
  - SMS to hospital
  - Logs to system
↓
Output:
  - Mission ID
  - Notification status
  - Mission ready for dispatch
```

---

## 📊 Database

### Cities Covered (10 Major Cities)
- 🌆 Bangalore
- 🏙️ Mumbai
- 🌃 Delhi
- 🌉 Hyderabad
- 🌆 Kolkata
- 🏙️ Chennai
- 🌃 Pune
- 🌉 Jaipur
- 🌆 Ahmedabad
- 🏙️ Lucknow

### Resource Database
| Category | Records | Details |
|----------|---------|---------|
| Volunteers | 30 | 3 per city, diverse skills |
| Vehicles | 30 | 3 per city (ambulance/van/pickup) |
| Hospitals | 30 | 3 per city, various specializations |

### CSV Files Included
All data is in `/data/` directory:
- `volunteers.csv` - Volunteer database with skills/location
- `vehicles.csv` - Vehicle fleet with equipment
- `hospitals.csv` - Hospital directory with specializations

---

## 🔧 Configuration

### Backend Settings (backend/app.py)

```python
UPLOAD_FOLDER = 'uploads'           # Photo storage
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
FLASK_PORT = 8000
```

### Agent Parameters

**Condition Agent:**
- Uses Claude Vision API
- Supports JPG, PNG images
- Max 16MB file size

**Resource Finder:**
- Volunteer search radius: 15km
- Vehicle search radius: 20km
- Hospital search radius: 25km

---

## 🔐 Security

- CORS enabled for Streamlit ↔ Flask communication
- File upload validation (JPG/PNG only)
- Environment variables for sensitive data
- No hardcoded API keys

---

## 📈 Deployment

### Option 1: Heroku

```bash
# Create Procfile
echo "web: gunicorn backend.app:app" > Procfile

# Deploy
heroku create your-app-name
git push heroku main
```

### Option 2: Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["python", "backend/app.py", "&", "streamlit", "run", "app.py"]
```

### Option 3: Streamlit Cloud

1. Push to GitHub
2. Go to https://streamlit.io/cloud
3. Create new app, select this repository
4. Set environment variables
5. Deploy!

---

## 🐛 Troubleshooting

### "Cannot reach the rescue server"
- Make sure backend is running: `python backend/app.py`
- Check if it's on `http://localhost:8000`
- Check firewall settings

### "API key not found"
- Create `.env` file
- Add `ANTHROPIC_API_KEY=sk-ant-...`
- Restart both frontend and backend

### "Image format error"
- Use JPG or PNG format
- Maximum 16MB file size
- Check image is not corrupted

### "No resources found"
- Check your coordinates are within city bounds
- Verify CSV files are in `/data/` directory
- Resources might all be busy

---

## 📞 Support

- **Issues**: Open GitHub issues for bugs
- **Questions**: Check FAQ in wiki
- **Contact**: email@example.com

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🙏 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 🎯 Roadmap

- [ ] Real PostgreSQL integration
- [ ] SMS notifications (Twilio)
- [ ] Real-time GPS tracking
- [ ] Mobile app (React Native)
- [ ] 24/7 emergency hotline
- [ ] Machine learning for better matching
- [ ] Multi-language support
- [ ] Integration with government agencies

---

## 📸 Screenshots

### Page 1: Upload
[Screenshot showing upload form with pet photo and form fields]

### Page 2: Live Case Tracking
[Screenshot showing agent progress with real-time updates]

---

## 🎓 Built With

- **Streamlit** - Frontend UI
- **Flask** - Backend API
- **Claude 3.5 Sonnet** - AI/LLM with Vision
- **PostgreSQL** - Database (optional)
- **Pandas** - Data processing
- **Anthropic SDK** - AI integration

---

## 📚 Learning Resources

- [Streamlit Docs](https://docs.streamlit.io)
- [Flask Documentation](https://flask.palletsprojects.com)
- [Claude API](https://console.anthropic.com)
- [Multi-agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)

---

**Made with 🐾 for animal rescue**

Last updated: September 2026
