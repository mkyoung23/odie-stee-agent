import os
import time
import pyautogui
import subprocess

# Open Microsoft Edge and go to openai.com
subprocess.Popen('start msedge "https://openai.com"', shell=True)
time.sleep(3)

# Open Spotify Desktop
subprocess.Popen('start spotify', shell=True)
time.sleep(5)

# Bring Spotify to front and play Kanye West
pyautogui.hotkey('ctrl', 'l')
time.sleep(1)
pyautogui.typewrite('Kanye West', interval=0.1)
time.sleep(1)
pyautogui.press('enter')
time.sleep(3)
pyautogui.press('tab', presses=4, interval=0.2)
pyautogui.press('enter')  # Play the first result
time.sleep(2)

# Open Notepad and create hello.txt on Desktop
subprocess.Popen('notepad')
time.sleep(2)
pyautogui.typewrite('Hello!', interval=0.1)
time.sleep(1)
pyautogui.hotkey('ctrl', 's')
time.sleep(1)
desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
pyautogui.typewrite(os.path.join(desktop, 'hello.txt'), interval=0.1)
time.sleep(1)
pyautogui.press('enter')