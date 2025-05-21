import pyautogui
import time
import os

# Helper to wait for window/app to appear (basic delay here for demo)
def wait(seconds=3):
    time.sleep(seconds)

# 1. Open Google Cloud Console (open default browser to Vertex AI page)
os.system('start chrome "https://console.cloud.google.com/ai/platform/vertex-ai/overview?project=lifelapse-27e17"')
wait(7)

# 2. Enable Vertex AI API (user manual step, automate browser only if extension/UI automation available)
# Attempt to search for "Vertex AI API" and enable (simulate CTRL+F, typing, clicks)
pyautogui.hotkey('ctrl', 'f')
wait(1)
pyautogui.typewrite('Vertex AI API')
wait(1)
pyautogui.press('esc')
wait(1)

# 3. Open Firebase Console and go to AI section
os.system('start chrome "https://console.firebase.google.com/project/lifelapse-27e17/ai"')
wait(7)

# (User may need to click "Enable Vertex AI" button if not enabled)
# Simulate TAB and ENTER in case the button is available
pyautogui.press('tab', presses=10, interval=0.2)
pyautogui.press('enter')
wait(3)

# 4. Open Remote Config in Firebase
os.system('start chrome "https://console.firebase.google.com/project/lifelapse-27e17/config"')
wait(7)

# 5. Add/update parameter: gemini_prompt_template: "Tell me about: %INPUT_TEXT%"
# Simulate tabbing and typing (may need fine-tuning based on actual UI position)
pyautogui.press('tab', presses=15, interval=0.2)
pyautogui.typewrite('gemini_prompt_template')
wait(0.5)
pyautogui.press('tab')
pyautogui.typewrite('Tell me about: %INPUT_TEXT%')
wait(0.5)
pyautogui.press('enter')  # Save/add

# Done