Ah, my apologies! You meant the **`README.md`** instead of the deployment guide.

Here is your **final, updated `README.md**` file, tailored for your stunning new UI and the Google Gemini integration:

```markdown
# 🐾 SafePaws: AI-Powered Pet Rescue Operations

SafePaws is a modern, intelligent emergency response application designed to streamline animal rescue operations. It leverages **Google Gemini Vision AI** to analyze emergency animal reports, assess injury severity, prioritize cases, and automatically coordinate nearby rescue resources (volunteers, vehicles, and veterinary hospitals).

---

## ✨ Features

- **📸 AI Vision Triage:** Upload photos of injured animals for instant AI analysis, species identification, and severity rating.
- **⚡ Smart Prioritization:** Algorithmic scoring engine that ranks cases by urgency and life-threatening conditions.
- **📍 Resource Matching:** Automatically matches the nearest available rescue volunteers, vehicles, and equipped hospitals using geographic Haversine distance calculations.
- **📊 Live Dashboard:** Track active incidents, monitor mission statuses, and view real-time operational metrics.
- **🎨 Modern Glassmorphism UI:** Built with Streamlit, featuring a gorgeous dark-mode aesthetic and smooth responsive layouts.

---

## 🛠️ Technology Stack

- **Frontend:** Streamlit (Python) with custom CSS Glassmorphism
- **AI / LLM:** Google Gemini API (`google-genai` SDK with `gemini-2.0-flash`)
- **Backend API:** Flask & Flask-CORS (Python)
- **Data Layer:** Pandas & In-memory database with CSV datasets (Volunteers, Vehicles, Hospitals)

---

## 🚀 Quick Start (Local Development)

### 1. Clone the Repository
```bash
git clone [https://github.com/Harsha-Boddu-2025/rescue-app.git](https://github.com/Harsha-Boddu-2025/rescue-app.git)
cd rescue-app

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Set Up Environment Variables

Copy the configuration template and add your Google Gemini API key:

```bash
cp .env.example .env

```

Open `.env` and set your key:

```env
GEMINI_API_KEY=your-gemini-api-key-here

```

### 4. Run the Application

Start the backend server and the Streamlit frontend:

**Terminal 1 (Backend API):**

```bash
cd backend
python app.py

```

**Terminal 2 (Frontend UI):**

```bash
streamlit run app.py

```

Open your browser at `http://localhost:8501`.

---

## 📁 Project Structure

```text
rescue-app/
├── app.py                    # Main Streamlit frontend UI
├── requirements.txt          # Python dependencies
├── README.md                 # Project documentation
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
│
├── pages/                    # Additional Streamlit pages
│   ├── upload.py             # Citizen report upload page
│   └── cases.py              # Case tracking dashboard
│
├── backend/                  # Flask API Backend
│   ├── app.py                # Main Flask server entry point
│   ├── agents/               # AI & Workflow Agents
│   │   ├── condition_agent.py      # Gemini Vision analyzer
│   │   ├── priority_agent.py       # Urgency scoring engine
│   │   ├── resource_finder_agent.py # Geographic resource matcher
│   │   └── coordinator_agent.py    # Mission dispatcher & notifier
│   └── database/             # Data persistence layer
│       └── db.py             # In-memory case & mission store
│
├── data/                     # Mock operational datasets
│   ├── volunteers.csv        # Volunteers across cities
│   ├── vehicles.csv          # Rescue vehicles & ambulances
│   └── hospitals.csv         # Veterinary hospitals & clinics
│
└── config/                   # Configuration settings

```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

---

**Built with 🐾 to help animals in need.**

```

```
