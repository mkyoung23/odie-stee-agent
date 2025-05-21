import os

# Find the Desktop folder, fallback to current dir if missing
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
if not os.path.exists(desktop):
    os.makedirs(desktop)

SETUP_NOTES = os.path.join(desktop, "firebase_setup_notes.txt")

def save_notes(text):
    with open(SETUP_NOTES, "a", encoding="utf-8") as f:
        f.write(text + "\n\n")