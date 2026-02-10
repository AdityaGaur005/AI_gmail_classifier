from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from gmail_classifier import (
    open_imap,
    fetch_unread_emails,
    classify_email
)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all frontends
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "AI Gmail Classifier API running"}

@app.get("/classify-emails")
def classify_emails():

    imap = open_imap()
    emails = fetch_unread_emails(imap)

    results = []

    for item in emails:
        category, scores = classify_email(
            item["subject"],
            item["from"],
            item["body"]
        )

        results.append({
            "subject": item["subject"],
            "from": item["from"],
            "category": category,
            "confidence": scores
        })

    imap.logout()

    return {
        "total": len(results),
        "emails": results
    }
