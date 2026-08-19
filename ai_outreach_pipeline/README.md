# AI Video Outreach Pipeline for Real Estate Leads

An automated outbound pipeline that takes real estate property photos, creates 5-second cinematic 3D video previews using generative AI (Replicate Kling/MiniMax), polishes the video with branding overlays and ambient audio via FFmpeg/MoviePy, uploads the result to Google Drive, sends a personalized outreach email, and logs follow-ups to Google Sheets.

---

## 🏗️ Architecture & Modules

```
ai_outreach_pipeline/
├── generator.py         # AI video generation via Replicate (Kling v1.5 / MiniMax)
├── editor.py            # Text overlay & ambient sound design (MoviePy/FFmpeg)
├── drive_service.py     # Google Drive upload & public permissions
├── mailer.py            # Personalized outreach email dispatch (Gmail SMTP)
├── sheets_service.py    # Google Sheets tracker logging
├── main.py              # Central orchestrator loop
├── requirements.txt     # Python dependencies
└── .env.example         # Environment variable template
```

---

## 🚀 Setup & Installation

### 1. Install Dependencies
```bash
pip install -r ai_outreach_pipeline/requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` in the `ai_outreach_pipeline` directory and provide your credentials:
```env
REPLICATE_API_TOKEN=r8_...
GMAIL_SENDER_EMAIL=your_email@gmail.com
GMAIL_APP_PASSWORD=xxxx-xxxx-xxxx-xxxx
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
GOOGLE_SHEET_NAME="Real Estate Outreach Leads"
```

### 3. Run Locally
```bash
python ai_outreach_pipeline/main.py
```

---

## ⚙️ Automated Deployment (GitHub Actions)

A scheduled GitHub Actions workflow is located in [`.github/workflows/daily_outreach.yml`](file:///.github/workflows/daily_outreach.yml). It triggers automatically every weekday morning at `09:00 UTC`.

### Required GitHub Secrets:
- `REPLICATE_API_TOKEN`
- `GMAIL_SENDER_EMAIL`
- `GMAIL_APP_PASSWORD`
- `GOOGLE_CREDENTIALS` (Raw JSON content of your Google Cloud Service Account)
- `GOOGLE_SHEET_NAME`
