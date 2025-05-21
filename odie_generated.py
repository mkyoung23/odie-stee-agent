import os
import time
import pyautogui
import requests
from dotenv import load_dotenv

# --- Load API Key Securely ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
NOTES_FILE = "firebase_setup_notes.txt"
FIREBASE_URL = "https://console.firebase.google.com/project/lifelapse-27e17/overview"

def open_firebase_console():
    os.system(f'start {FIREBASE_URL}')
    time.sleep(10)

def send_to_gemini_chat(message, x=1200, y=900):
    pyautogui.click(x, y)  # update for Gemini input box
    time.sleep(0.5)
    pyautogui.write(message, interval=0.03)
    pyautogui.press('enter')

def call_gemini_api(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    resp = requests.post(url, json=payload)
    data = resp.json()
    return (
        data.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", "")
    )

def save_notes(notes):
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(notes + "\n\n")

def backup_to_github():
    os.system("git add .")
    os.system('git commit -m "Firebase/FlutterFlow update [auto]"')
    os.system("git push")

# --- MAIN FLOW ---

open_firebase_console()

# Step 1: Gemini chat - Database, Auth, Storage, UI
send_to_gemini_chat(
    "Gemini, configure Cloud Firestore in us-east4, enable Storage, and set up Auth for Email/Password, Google, and Apple. Collections: Users, Groups, Videos. Use the project blueprint for fields."
)

# Step 2: Use Gemini API for secure rules/code generation
rules_prompt = (
    "Write secure Firestore rules for a production app. "
    "Collections: Users (user-only access), Groups (member-only access), Videos (group-access only). "
    "Enforce auth (Email/Google/Apple). Output only code."
)
rules_code = call_gemini_api(rules_prompt)
save_notes("Firestore Rules:\n" + rules_code)

# (Example) Update Remote Config via Gemini API
config_prompt = (
    "Generate Firebase Remote Config JSON for live API key and feature flag rollout."
)
config_code = call_gemini_api(config_prompt)
save_notes("Remote Config Example:\n" + config_code)

# (Example) AI captions A/B testing snippet for FlutterFlow
ai_caption_prompt = (
    "Flutter/Dart: Write a function using Gemini API to auto-caption video uploads. Enable A/B testing using Firebase Remote Config."
)
ai_caption_code = call_gemini_api(ai_caption_prompt)
save_notes("AI Captions with A/B Testing:\n" + ai_caption_code)

# Step 3: Backup all changes to GitHub (never commit .env)
backup_to_github()

# Error handling: If any error, log it, send to Gemini chat & API for fix, then retry step.
# (Add your error-catch + retry logic as needed)

# --- END ---