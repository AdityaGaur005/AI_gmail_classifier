#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI Email Classifier + Gmail Auto Triage

Features:
- Reads unread Gmail emails using IMAP
- Classifies emails into Work / Spam / Urgent / Personal
- Applies Gmail labels automatically (AI/<Category>)
- Moves Spam emails to Gmail Spam
- Generates short AI replies (optional)
- Shows final classified email summary in terminal

Install dependencies:
pip install transformers torch beautifulsoup4 python-dotenv
"""

import os
import re
import imaplib
import smtplib
import email
from email.header import decode_header, make_header
from email.utils import parseaddr
from email.mime.text import MIMEText

# Load .env variables if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

from transformers import pipeline
from bs4 import BeautifulSoup

# ================= CONFIG =================

EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT", "your_email@gmail.com").strip()
EMAIL_PASSWORD = (os.getenv("EMAIL_APP_PASSWORD") or os.getenv("EMAIL_PASSWORD") or "your_app_password")
EMAIL_PASSWORD = EMAIL_PASSWORD.replace(" ", "").strip()

IMAP_SERVER = "imap.gmail.com"
SMTP_SERVER = "smtp.gmail.com"
IMAP_MAILBOX = "INBOX"

CATEGORIES = ["Work", "Spam", "Urgent", "Personal"]
SPAM_THRESHOLD = 0.85
MAX_EMAILS = 25
APPLY_GMAIL_LABELS = True
LABEL_PREFIX = "AI"

# ================= MODELS =================

print("Loading AI models... (first run may take time)")

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

try:
    generator = pipeline("text2text-generation", model="google/flan-t5-small")
    GEN_MODE = "t5"
except:
    generator = pipeline("text-generation", model="distilgpt2")
    GEN_MODE = "gpt2"

# ================= HELPERS =================

def decode_mime_words(s):
    if not s:
        return ""
    try:
        return str(make_header(decode_header(s)))
    except:
        return s

def get_body_from_msg(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ctype = part.get_content_type()
            if ctype == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    return payload.decode(errors="ignore")
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                html = part.get_payload(decode=True)
                return BeautifulSoup(html, "html.parser").get_text()
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            return payload.decode(errors="ignore")
    return ""

def open_imap():
    imap = imaplib.IMAP4_SSL(IMAP_SERVER)
    imap.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
    imap.select(IMAP_MAILBOX)
    return imap

def fetch_unread_emails(imap, limit=MAX_EMAILS):
    status, data = imap.uid("search", None, "(UNSEEN)")
    uids = data[0].split()

    emails = []
    for uid in uids[:limit]:
        status, msg_data = imap.uid("fetch", uid, "(RFC822)")
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = decode_mime_words(msg.get("Subject"))
        from_addr = parseaddr(msg.get("From"))[1]
        body = get_body_from_msg(msg)

        emails.append({
            "uid": uid.decode(),
            "subject": subject,
            "from": from_addr,
            "body": body,
            "msg": msg
        })

    return emails

def classify_email(subject, sender, body):
    text = f"Subject: {subject}\nFrom: {sender}\n\n{body[:1500]}"
    result = classifier(text, CATEGORIES, multi_label=True)

    scores = dict(zip(result["labels"], result["scores"]))
    top_category = max(scores, key=scores.get)

    if scores.get("Spam", 0) >= SPAM_THRESHOLD:
        top_category = "Spam"

    return top_category, scores

def add_gmail_labels(imap, uid, labels):
    label_arg = "(" + " ".join(f'"{l}"' for l in labels) + ")"
    imap.uid("STORE", uid, "+X-GM-LABELS", label_arg)

def move_to_spam(imap, uid):
    imap.uid("COPY", uid, "[Gmail]/Spam")
    imap.uid("STORE", uid, "+FLAGS", r"(\Deleted)")
    imap.expunge()

def generate_reply(text, category):
    if category == "Spam":
        return None

    prompt = f"Write a polite short reply to this {category} email in 2 sentences:\n{text}"
    out = generator(prompt, max_new_tokens=60)[0]["generated_text"]
    return out.strip()

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["From"] = EMAIL_ACCOUNT
    msg["To"] = to
    msg["Subject"] = "Re: " + subject

    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())

# ================= MAIN =================

if __name__ == "__main__":

    print(f"\nStarting Gmail AI Classifier for {EMAIL_ACCOUNT}\n")

    imap = open_imap()
    emails = fetch_unread_emails(imap)

    classified_results = []

    if not emails:
        print("No unread emails found.")
    else:
        for item in emails:
            print(f"\nProcessing: {item['subject']}")

            category, scores = classify_email(
                item["subject"],
                item["from"],
                item["body"]
            )

            classified_results.append({
                "from": item["from"],
                "subject": item["subject"],
                "category": category,
                "scores": {k: round(v, 3) for k, v in scores.items()}
            })

            print("Category:", category)

            # Apply Gmail label
            if APPLY_GMAIL_LABELS:
                add_gmail_labels(imap, item["uid"], [f"{LABEL_PREFIX}/{category}"])

            # Move spam
            if category == "Spam":
                move_to_spam(imap, item["uid"])
                continue

            # Generate reply
            reply = generate_reply(item["body"], category)

            if reply:
                send_email(item["from"], item["subject"], reply)

    # ===== FINAL OUTPUT =====
    print("\n==============================")
    print("FINAL CLASSIFIED EMAILS")
    print("==============================")

    for idx, mail in enumerate(classified_results, 1):
        print(f"\n{idx}. {mail['subject']}")
        print(f"From     : {mail['from']}")
        print(f"Category : {mail['category']}")
        print(f"Scores   : {mail['scores']}")

    imap.logout()

    print("\nDone.")
