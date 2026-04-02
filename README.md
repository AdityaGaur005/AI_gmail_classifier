📨 AI Gmail Classifier & Auto Email Triage

An AI-powered system that automatically reads, classifies, organizes, and responds to emails using Natural Language Processing.

This is not just a classifier — it performs end-to-end email automation including labeling, spam handling, and AI-generated replies.

🚀 Features
📬 Fetch unread emails from Gmail (IMAP)
🧠 Classify emails into:
Work
Spam
Urgent
Personal
🏷️ Automatically apply Gmail labels (AI/<Category>)
🚫 Move spam emails to Gmail Spam
✉️ Generate AI-based reply suggestions
🌐 FastAPI backend for API access
🖥️ Simple dashboard UI to view classified emails
🧠 Core Idea

Traditional email management:

Manual sorting ❌

This system:

AI reads → classifies → organizes → responds ✅

🔄 Workflow
Connect to Gmail using IMAP
Fetch unread emails
Extract:
Subject
Sender
Email body
Run AI classification (Zero-shot model)
Based on category:
Apply Gmail label
Move spam to Spam folder
Generate reply (optional)
Return structured output via API
🏗️ System Architecture
Gmail Inbox
    ↓
IMAP Fetch (Unread Emails)
    ↓
Text Processing (Subject + Body)
    ↓
AI Classification (BART - Zero Shot)
    ↓
Decision Engine
   ├── Apply Labels
   ├── Move Spam
   └── Generate Reply
    ↓
API Response / Dashboard


🤖 AI Models Used
1. Email Classification
Model: facebook/bart-large-mnli
Type: Zero-shot classification
Advantage:
No training required
Flexible categories
2. Reply Generation
Model: google/flan-t5-small (fallback: GPT-2)
Generates short, polite responses

🌐 API Endpoints
Base URL
http://127.0.0.1:8000
1. Health Check
GET /
2. Classify Emails
GET /classify-emails
Response Example:
```json
{
  "total": 3,
  "emails": [
    {
      "subject": "Meeting tomorrow",
      "from": "manager@company.com",
      "category": "Work",
      "confidence": {
        "Work": 0.91,
        "Urgent": 0.72
      }
    }
  ]
}
```

## 🖥️ Frontend Dashboard

- Displays classified emails in a table  
- Highlights categories using colors:
  - 🟢 Work  
  - 🔴 Spam  
  - 🟠 Urgent  
  - 🔵 Personal  
- Fetch button to load latest emails  

---

## 🛠️ Tech Stack

### Backend
- Python  
- FastAPI  
- IMAP / SMTP  

### AI / NLP
- HuggingFace Transformers  
- BART (Zero-shot classification)  
- FLAN-T5 / GPT-2 (text generation)  

### Email Processing
- imaplib  
- smtplib  
- BeautifulSoup  

### Frontend
- HTML  
- CSS  
- JavaScript  

---

## 🔐 Configuration

Set your email credentials using environment variables:

```bash
EMAIL_ACCOUNT=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
```

📌 Why This Project Stands Out
Real-world automation (not just ML model)
Integrates AI with Gmail system
Uses zero-shot learning (no dataset required)
Handles full pipeline:
Read → Classify → Act → Respond

👉 Shows strong system design + AI integration skills

🔮 Future Improvements
Add email priority scoring
Auto calendar scheduling
Gmail OAuth (secure login)
Deploy on cloud (AWS / GCP)
Add database for email history
👨‍💻 Author

Aditya Gaur
