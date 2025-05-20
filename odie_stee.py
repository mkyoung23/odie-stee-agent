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
COPY_SCROLLS = 12

# <<-- USER: Save a screenshot of ChatGPT's "Copy code" button as copy_code_button.png in this folder! -->

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

def move_click_text(text, max_scrolls=10):
    for i in range(max_scrolls):
        results = ocr_screen()
        for bbox, found_text, conf in results:
            if text.lower() in found_text.lower():
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                center = ((x1 + x2)//2, (y1 + y2)//2)
                pyautogui.moveTo(center[0], center[1], duration=0.3)
                pyautogui.click()
                print(f"Clicked on '{text}' at {center}")
                return True
        pyautogui.scroll(-400)
        time.sleep(0.4)
    print(f"Text '{text}' not found on screen after scrolling.")
    return False

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

def select_and_copy_large_area(top_left, bottom_right):
    pyautogui.moveTo(top_left[0], top_left[1], duration=0.2)
    pyautogui.mouseDown()
    pyautogui.moveTo(bottom_right[0], bottom_right[1], duration=0.5)
    pyautogui.mouseUp()
    time.sleep(0.2)
    pyautogui.hotkey('ctrl', 'c')
    text = pyperclip.paste()
    print(f"Copied large block (first 100 chars): {text[:100]}")
    return text

def copy_by_image(image_path, max_scrolls=10, wait_for_seconds=15):
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

def universal_copy(target_text=None, image_path=None, select_area=None, fallback_manual=True):
    copied = None
    if image_path:
        copied = copy_by_image(image_path)
    if not copied and target_text:
        if move_click_text(target_text):
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'c')
            copied = pyperclip.paste()
    if not copied and select_area:
        copied = select_and_copy_large_area(*select_area)
    if not copied and fallback_manual:
        print("Please manually select/copy the section now, then press Enter.")
        input()
        copied = pyperclip.paste()
    return copied

def save_anywhere(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(data)
    print(f"Saved data to {filepath}")

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

    code = copy_by_image("copy_code_button.png", wait_for_seconds=16)
    code = clean_code_block(code)
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
        code = copy_by_image("copy_code_button.png", wait_for_seconds=16)
        code = clean_code_block(code)
        save_anywhere(code, generated)
        run_file(generated)

    push_to_github()

if __name__ == "__main__":
    ensure_gitignore_and_remove_env()
    ensure_git_repo()
    task = get_task()
    print(f"ODIE STEE TASK: {task}")
    self_upgrade_cycle(task)
