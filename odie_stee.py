import os
import time
import pyautogui
import pyperclip
import easyocr
import numpy as np
import subprocess
import openai
from dotenv import load_dotenv

# ====== CONFIG ======
TASK_FILE = "task.txt"
GITHUB_URL = "https://github.com/"
CODEX_URL = "https://chat.openai.com/"
REPO_NAME = "odie-stee-agent"
COPY_SCROLLS = 12

# ====== SETUP ======
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("No OPENAI_API_KEY found in .env. Exiting.")
    exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)
reader = easyocr.Reader(['en'], gpu=False)  # set gpu=True if you have CUDA

# ====== UTILS: GIT/SECRET PROTECTION ======
def ensure_gitignore_and_remove_env():
    # Add .env to .gitignore
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write('.env\n')
    else:
        with open('.gitignore', 'r+') as f:
            lines = f.readlines()
            if '.env\n' not in lines and '.env' not in [line.strip() for line in lines]:
                f.write('.env\n')
    # Remove .env from git if accidentally tracked
    os.system('git rm --cached .env')

def ensure_git_repo():
    if not os.path.exists(".git"):
        print("No Git repo found. Opening GitHub so you can create one...")
        open_browser(GITHUB_URL, wait=8)
        print("Create a new repo, then paste the HTTPS URL below.")
        repo_url = input("Paste your GitHub repo HTTPS URL here: ").strip()
        if repo_url:
            os.system(f"git init")
            os.system(f"git remote add origin {repo_url}")
            os.system("git config user.name 'Odie Stee'")
            os.system("git config user.email 'odie@stee.com'")
            print("Git repo linked. Ready to go!")

def push_to_github(commit_msg="Automated commit from Odie Stee"):
    os.system('git add .')
    os.system(f'git commit -m "{commit_msg}"')
    os.system('git push')

# ====== COPY/PASTE & OCR MODULE ======

def ocr_screen(delay=0):
    if delay > 0:
        time.sleep(delay)
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    results = reader.readtext(screenshot_np)
    return results

def scroll_and_find_text(target, max_scrolls=COPY_SCROLLS, delay=0.5):
    """Scrolls down, OCRs, and finds target text, returns center/bbox if found."""
    for i in range(max_scrolls):
        results = ocr_screen()
        for bbox, text, conf in results:
            if target.lower() in text.lower():
                print(f"Found '{target}' on screen!")
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                center = ((x1 + x2)//2, (y1 + y2)//2)
                return center, bbox
        pyautogui.scroll(-500)
        time.sleep(delay)
    print(f"Did not find '{target}' after {max_scrolls} scrolls.")
    return None, None

def select_and_copy_area(center):
    pyautogui.moveTo(center[0], center[1], duration=0.3)
    pyautogui.tripleClick()
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    copied = pyperclip.paste()
    print(f"Copied (first 100 chars): {copied[:100]}...")
    return copied

def copy_by_template(image_path, max_scrolls=COPY_SCROLLS, delay=0.5):
    for i in range(max_scrolls):
        btn = pyautogui.locateCenterOnScreen(image_path, confidence=0.85)
        if btn:
            pyautogui.moveTo(btn)
            pyautogui.click()
            print(f"Clicked button from {image_path}.")
            time.sleep(0.2)
            copied = pyperclip.paste()
            print(f"Copied (first 100 chars): {copied[:100]}...")
            return copied
        pyautogui.scroll(-500)
        time.sleep(delay)
    print(f"Button/image {image_path} not found after scrolling.")
    return None

def copy_anything(target_text=None, image_path=None, fallback_manual=True):
    copied = None
    if image_path:
        copied = copy_by_template(image_path)
    if not copied and target_text:
        center, bbox = scroll_and_find_text(target_text)
        if center:
            copied = select_and_copy_area(center)
    if not copied and fallback_manual:
        print("Could not auto-copy. Please manually select and copy, then press ENTER to continue.")
        input()
        copied = pyperclip.paste()
    return copied

def save_anywhere(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"Saved data to {filepath}")

# ====== AGENT'S BRAIN ======

def open_browser(url, wait=6):
    print(f"Opening browser to {url}")
    if os.name == 'nt':
        os.system(f'start {url}')
    elif os.name == 'posix':
        subprocess.call(['open', url])
    else:
        subprocess.call(['xdg-open', url])
    time.sleep(wait)

def run_file(filename):
    print(f"Running {filename} ...")
    result = subprocess.run(["python", filename], capture_output=True, text=True)
    print("--- STDOUT ---\n", result.stdout)
    print("--- STDERR ---\n", result.stderr)
    return result.returncode == 0, result.stderr

def get_task():
    if not os.path.exists(TASK_FILE):
        print(f"Put your request in {TASK_FILE}, then run again.")
        exit(1)
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def self_upgrade_cycle(task, generated="odie_generated.py"):
    # 1. Plan steps
    plan_prompt = f"You are an agent controlling Windows via Python/pyautogui/OCR. User task: {task}\nBreak it down into step-by-step numbered actions. Do not output any explanations."
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Expert Windows automation agent."},
            {"role": "user", "content": plan_prompt}
        ]
    )
    steps = response.choices[0].message.content
    print("---- PLANNED STEPS ----\n", steps)

    # 2. Ask Codex/ChatGPT for code to do the task
    code_prompt = f"Write a pure Python script to do this task on Windows. Use pyautogui, OCR, file I/O, and os as needed. No explanation, only code:\n{task}"
    open_browser(CODEX_URL, wait=8)
    time.sleep(2)
    pyautogui.typewrite(code_prompt, interval=0.02)
    pyautogui.press('enter')
    print("Prompt submitted to Codex/ChatGPT. Let it generate code, then let Odie auto-copy or manually copy code as needed.")
    print("If automation doesn't copy the code, select and copy code manually, then press ENTER here.")

    # Try to auto-copy (if code block visible)
    time.sleep(12)
    code = copy_anything(target_text="import ", fallback_manual=True)
    save_anywhere(code, generated)
    worked, errors = run_file(generated)
    if not worked:
        print("Code failed. Copying errors and asking Codex/ChatGPT for a fix.")
        error_prompt = f"This code failed with the following errors. Please fix and return the corrected full script (code only, no explanation):\n\n{code}\n\nERRORS:\n{errors}"
        open_browser(CODEX_URL, wait=8)
        time.sleep(2)
        pyautogui.typewrite(error_prompt, interval=0.02)
        pyautogui.press('enter')
        print("Let Odie auto-copy or manually copy the fixed code, then press ENTER here.")
        time.sleep(12)
        fixed_code = copy_anything(target_text="import ", fallback_manual=True)
        save_anywhere(fixed_code, generated)
        run_file(generated)

    push_to_github()

# ====== MAIN LOOP ======
if __name__ == "__main__":
    ensure_gitignore_and_remove_env()
    ensure_git_repo()
    task = get_task()
    print(f"ODIE STEE TASK: {task}")
    self_upgrade_cycle(task)
