import os
import time
import pyautogui
import pyperclip
import easyocr
import numpy as np
import subprocess
import openai
import re
from dotenv import load_dotenv

TASK_FILE = "task.txt"
GITHUB_URL = "https://github.com/"
CODEX_URL = "https://chat.openai.com/"
REPO_NAME = "odie-stee-agent"

# == ChatGPT Copy Button Screenshot (crop tightly and name as below)
COPY_BUTTON_IMAGE = "copy_code_button.png"

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("No OPENAI_API_KEY found in .env. Exiting.")
    exit(1)

client = openai.OpenAI(api_key=OPENAI_API_KEY)
reader = easyocr.Reader(['en'], gpu=False)

def ensure_gitignore_and_remove_env():
    if not os.path.exists('.gitignore'):
        with open('.gitignore', 'w') as f:
            f.write('.env\n')
    else:
        with open('.gitignore', 'r+') as f:
            lines = f.readlines()
            if '.env\n' not in lines and '.env' not in [line.strip() for line in lines]:
                f.write('.env\n')
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

def ocr_screen(delay=0):
    if delay > 0:
        time.sleep(delay)
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    results = reader.readtext(screenshot_np)
    return results

def open_app_by_search(app_name, fallback_coords=(30, 1060)):
    print(f"Trying to open {app_name} using Start menu...")
    found_start = False
    results = ocr_screen()
    for bbox, text, conf in results:
        if "start" in text.lower():
            x1, y1 = bbox[0]
            x2, y2 = bbox[2]
            center = ((x1 + x2)//2, (y1 + y2)//2)
            pyautogui.moveTo(center[0], center[1], duration=0.2)
            pyautogui.click()
            found_start = True
            print("Clicked Start by OCR.")
            break
    if not found_start:
        pyautogui.moveTo(*fallback_coords, duration=0.2)
        pyautogui.click()
        print("Clicked Start by fallback position.")
    time.sleep(1)
    for _ in range(3):
        pyautogui.press('backspace')
    pyautogui.write(app_name, interval=0.1)
    time.sleep(1)
    pyautogui.press('enter')
    print(f"Typed {app_name} and hit Enter.")
    time.sleep(5)

def open_browser(url, wait=6):
    print(f"Opening browser to {url}")
    if os.name == 'nt':
        os.system(f'start {url}')
    elif os.name == 'posix':
        subprocess.call(['open', url])
    else:
        subprocess.call(['xdg-open', url])
    time.sleep(wait)

def clean_code_block(code):
    code = re.sub(r"^```(python)?", "", code, flags=re.MULTILINE)
    code = re.sub(r"```$", "", code, flags=re.MULTILINE)
    cleaned_lines = []
    for line in code.splitlines():
        line_strip = line.strip()
        if line_strip.startswith("python ") or line_strip.startswith("$"):
            continue
        if re.match(r'^[\w\-_.]+\.(py|sh|bat|exe)', line_strip):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()

def copy_by_image(image_path, wait_for_seconds=16, max_scrolls=10):
    print(f"Waiting {wait_for_seconds} seconds for ChatGPT to finish writing code...")
    time.sleep(wait_for_seconds)
    print("Looking for 'Copy code' button...")
    for attempt in range(max_scrolls):
        location = pyautogui.locateCenterOnScreen(image_path, confidence=0.85)
        if location:
            pyautogui.moveTo(location[0], location[1], duration=0.2)
            pyautogui.click()
            print(f"Clicked 'Copy code' at {location}")
            time.sleep(0.3)
            code = pyperclip.paste()
            print(f"Copied full code block (first 100 chars): {code[:100]}")
            return code
        pyautogui.scroll(-200)
        time.sleep(0.5)
    print("Failed to find 'Copy code' button. Please copy manually and press ENTER.")
    input()
    return pyperclip.paste()

def save_anywhere(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"Saved data to {filepath}")

def run_file(filename):
    print(f"Running {filename} ...")
    result = subprocess.run(["python", filename], capture_output=True, text=True)
    print("--- STDOUT ---\n", result.stdout)
    print("--- STDERR ---\n", result.stderr)
    return result.returncode == 0, result.stderr, result.stdout

def get_task():
    if not os.path.exists(TASK_FILE):
        print(f"Put your request in {TASK_FILE}, then run again.")
        exit(1)
    with open(TASK_FILE, "r", encoding="utf-8") as f:
        return f.read().strip()

def self_fix_code(original_code, error_msg, task, generated="odie_generated.py"):
    # 1. Open browser and ask for a fix, paste full code and error
    open_browser(CODEX_URL, wait=8)
    fix_prompt = f"This code failed with the following error. Please fix it for this task, and return only the corrected, complete script (no explanations):\n\nTASK:\n{task}\n\nCODE:\n{original_code}\n\nERROR:\n{error_msg}\n"
    pyautogui.typewrite(fix_prompt, interval=0.02)
    pyautogui.press('enter')
    print("Prompted ChatGPT/Codex for code fix, now copying new code block...")
    fixed_code = copy_by_image(COPY_BUTTON_IMAGE, wait_for_seconds=18)
    fixed_code = clean_code_block(fixed_code)
    save_anywhere(fixed_code, generated)
    print("Re-running the fixed code...")
    return run_file(generated)

def self_upgrade_cycle(task, generated="odie_generated.py"):
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

    # Detect any "open" app command in task and open it visually
    task_lower = task.lower()
    open_targets = ["open ", "launch ", "start "]
    for ot in open_targets:
        idx = task_lower.find(ot)
        if idx != -1:
            app = task_lower[idx + len(ot):].split()[0].capitalize()
            open_app_by_search(app)
            break

    # Ask Codex/ChatGPT for code to do the task
    code_prompt = f"Write a pure Python script to do this task on Windows. Use pyautogui, OCR, file I/O, and os as needed. No explanation, only code:\n{task}"
    open_browser(CODEX_URL, wait=8)
    time.sleep(2)
    pyautogui.typewrite(code_prompt, interval=0.02)
    pyautogui.press('enter')
    print("Prompt submitted to Codex/ChatGPT. Wait for code to finish generating...")
    print("Odie will now look for 'Copy code' button and click it to copy the entire code block.")

    code = copy_by_image(COPY_BUTTON_IMAGE, wait_for_seconds=18)
    code = clean_code_block(code)
    save_anywhere(code, generated)
    worked, errors, std_out = run_file(generated)
    loop_count = 0
    # AUTO-RETRY LOOP!
    while not worked and loop_count < 5:
        print(f"Auto-fix attempt #{loop_count+1}")
        worked, errors, std_out = self_fix_code(code, errors, task, generated)
        code = open(generated, encoding="utf-8").read()
        loop_count += 1

    if worked:
        print("Task completed and code fixed successfully!")
    else:
        print("Auto-fix failed after 5 attempts. Manual intervention required.")
        save_anywhere(errors, "odie_error.log")

    push_to_github()

if __name__ == "__main__":
    ensure_gitignore_and_remove_env()
    ensure_git_repo()
    task = get_task()
    print(f"ODIE STEE TASK: {task}")
    self_upgrade_cycle(task)
