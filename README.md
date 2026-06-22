# ✦ AI Resume & Portfolio Builder

An AI-powered career tools suite built with **Flask**, **Gemini API**, **Firebase Firestore**, and **ReportLab**. Generate ATS-optimised resumes, tailored cover letters, and portfolio pages in minutes.

---

## 📁 Project Structure

```
AI-Resume-Portfolio-Builder/
│
├── frontend/
│   ├── templates/
│   │   ├── index.html          ← Landing page
│   │   ├── resume.html         ← Resume builder
│   │   ├── coverletter.html    ← Cover letter builder
│   │   └── portfolio.html      ← Portfolio builder
│   └── static/
│       ├── css/
│       │   ├── main.css        ← Shared design tokens & nav
│       │   ├── index.css       ← Landing page styles
│       │   └── builder.css     ← Builder page layout
│       ├── js/
│       │   ├── auth.js         ← Firebase Authentication
│       │   ├── main.js         ← Landing page JS
│       │   ├── resume.js       ← Resume builder logic
│       │   ├── coverletter.js  ← Cover letter logic
│       │   └── portfolio.js    ← Portfolio builder logic
│       └── images/
│
├── backend/
│   ├── app.py                  ← Flask app factory & entry point
│   ├── routes.py               ← Blueprint registration
│   ├── gemini_api.py           ← Gemini API wrapper
│   ├── firebase_config.py      ← Firestore client & CRUD helpers
│   ├── pdf_generator.py        ← ReportLab PDF generation
│   │
│   ├── controllers/            ← HTTP request handlers (thin layer)
│   │   ├── page_controller.py
│   │   ├── resume_controller.py
│   │   ├── cover_controller.py
│   │   ├── portfolio_controller.py
│   │   └── user_controller.py
│   │
│   ├── services/               ← Business logic & AI orchestration
│   │   ├── resume_service.py
│   │   ├── cover_service.py
│   │   ├── portfolio_service.py
│   │   └── user_service.py
│   │
│   └── utils/
│       ├── logger.py           ← Centralised logging
│       ├── validators.py       ← Request field validation
│       └── response_helpers.py ← Consistent JSON responses
│
├── database/
│   └── firebase-service-account.json   ← (add yours, never commit)
│
├── generated_files/            ← PDF outputs (auto-created)
│
├── requirements.txt
├── .env.example                ← Copy to .env and fill values
├── .gitignore
└── README.md
```

---

## 🚀 Quick Start

### 1. Clone & set up environment

```bash
git clone <repo-url>
cd AI-Resume-Portfolio-Builder

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your keys (see Configuration section below)
```

### 3. Add Firebase credentials

Download your Firebase service account JSON from:
**Firebase Console → Project Settings → Service Accounts → Generate new private key**

Save it to: `database/firebase-service-account.json`

### 4. Run the server

```bash
cd backend
python app.py
# Server starts at http://localhost:5000
```

---

## ⚙️ Configuration

Edit `.env` with your values:

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Flask secret key (any random string) |
| `GEMINI_API_KEY` | From [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `GEMINI_MODEL` | `gemini-2.5-flash` (default) or `gemini-2.5-pro` |
| `FIREBASE_CREDENTIALS_PATH` | Path to service account JSON |
| `FLASK_ENV` | `development` or `production` |

### Firebase setup
1. Create a project at [Firebase Console](https://console.firebase.google.com)
2. Enable **Firestore Database** (start in test mode for development)
3. Enable **Authentication** → Google Sign-in provider
4. Download the service account JSON and place in `database/`
5. Update `firebaseConfig` in `frontend/static/js/auth.js` with your web app credentials

---

## 🌐 API Endpoints

### Resume
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/resume/generate` | Generate AI resume from raw input |
| `POST` | `/api/resume/enhance` | Enhance a specific section |
| `GET`  | `/api/resume/download/<id>` | Download PDF |
| `POST` | `/api/resume/save` | Save to Firestore |
| `GET`  | `/api/resume/list/<user_id>` | List user's resumes |
| `DELETE` | `/api/resume/<id>` | Delete a resume |

### Cover Letter
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/cover-letter/generate` | Generate cover letter |
| `GET`  | `/api/cover-letter/download/<id>` | Download PDF |
| `POST` | `/api/cover-letter/save` | Save to Firestore |
| `GET`  | `/api/cover-letter/list/<user_id>` | List cover letters |

### Portfolio
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/portfolio/generate` | Generate portfolio |
| `POST` | `/api/portfolio/save` | Save to Firestore |
| `GET`  | `/api/portfolio/list/<user_id>` | List portfolios |
| `DELETE` | `/api/portfolio/<id>` | Delete |

### User
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/user/profile` | Create/update profile |
| `GET`  | `/api/user/profile/<user_id>` | Get profile |

---

## 🏗️ Architecture

```
Browser ──► Flask (app.py)
              │
              ├─► Controllers  (HTTP parsing, routing)
              │       │
              │       └─► Services  (business logic + Gemini calls)
              │                │
              │                ├─► gemini_api.py   (AI text gen)
              │                ├─► pdf_generator.py (ReportLab)
              │                └─► firebase_config.py (Firestore CRUD)
              │
              └─► Templates (Jinja2 → HTML served to browser)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | Python 3.11+, Flask 3.0 |
| AI | Google Gemini 2.5 Flash/Pro |
| Database | Firebase Firestore |
| Auth | Firebase Authentication (Google) |
| PDF | ReportLab 4.x |
| Hosting (prod) | Gunicorn + any cloud (Railway, Render, GCP) |

---

## 📦 Production Deployment

```bash
# Using Gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

Set `FLASK_ENV=production` and use a reverse proxy (nginx) in front of Gunicorn.

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes
4. Open a pull request

---

## 📄 License

MIT
