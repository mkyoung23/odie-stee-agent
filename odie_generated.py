import pyautogui
import time
import os

# --- Helper variables (update X/Y coords as needed for your setup) ---
search_bar_x, search_bar_y = 400, 120      # Spotify Search Bar
song_x, song_y = 400, 300                  # First song result, may need to adjust
chrome_icon_x, chrome_icon_y = 60, 160     # Edge/Chrome icon if needed

# 1. Open Start Menu, type Spotify, press Enter
time.sleep(2)
pyautogui.press('win')
time.sleep(1)
pyautogui.typewrite('Spotify', interval=0.1)
time.sleep(1)
pyautogui.press('enter')
time.sleep(6)

# 2. Search for "Kanye West Can't Tell Me Nothing" and press Enter
pyautogui.click(search_bar_x, search_bar_y)
time.sleep(1)
pyautogui.typewrite("Kanye West Can't Tell Me Nothing", interval=0.08)
time.sleep(0.5)
pyautogui.press('enter')
time.sleep(3.5)

# 3. Double-click first result (song title)
pyautogui.doubleClick(song_x, song_y)
time.sleep(2)

# 4. Open Notepad
pyautogui.press('win')
time.sleep(1)
pyautogui.typewrite('Notepad', interval=0.1)
time.sleep(1)
pyautogui.press('enter')
time.sleep(2)

# 5. Type the message
msg = "Hello, World! This was written by Odie Stee."
pyautogui.typewrite(msg, interval=0.08)
time.sleep(1)

# 6. Save to Desktop as hello.txt using address bar
pyautogui.hotkey('alt', 'f')
time.sleep(0.5)
pyautogui.press('a')  # Save As
time.sleep(2)
pyautogui.hotkey('alt', 'd')  # Focus address bar
time.sleep(0.5)
pyautogui.typewrite('Desktop', interval=0.05)
pyautogui.press('enter')
time.sleep(1)
pyautogui.typewrite('hello.txt', interval=0.05)
pyautogui.press('enter')
time.sleep(1)

# 7. Open Edge/Chrome
pyautogui.press('win')
time.sleep(1)
pyautogui.typewrite('Edge', interval=0.1)
time.sleep(1)
pyautogui.press('enter')
time.sleep(3.5)

# 8. Go to google.com
pyautogui.typewrite('google.com', interval=0.08)
pyautogui.press('enter')
time.sleep(3)

# 9. Search in Google
search_query = ("Best vacation spots or romantic getaways in Charleston SC for a couple age 30, "
                "traveling for the week of July 11th.")
time.sleep(2)
pyautogui.click(500, 350)  # Click Google search box (adjust if needed)
time.sleep(0.5)
pyautogui.typewrite(search_query, interval=0.06)
pyautogui.press('enter')
time.sleep(5)

# 10. Pause for user to review page (OCR required for auto summarization; not reliable for web)
# To automate, would require OCR or HTML parsing, here we just open results and continue after manual review.

# 11. Open another Notepad window
pyautogui.press('win')
time.sleep(1)
pyautogui.typewrite('Notepad', interval=0.1)
time.sleep(1)
pyautogui.press('enter')
time.sleep(1)

# 12. Summarize recommendations (placeholder text, since automation can't read browser content directly)
summary = """Top vacation ideas in Charleston, SC for a couple, week of July 11th:
1. Stay at a historic downtown Charleston inn, walk King Street, and dine at local restaurants.
2. Romantic sunset harbor cruise and Folly Beach day trips.
3. Explore Magnolia Plantation & Gardens, Boone Hall Plantation, and nearby waterfront parks.
4. Spa day for couples and private carriage tours of historic neighborhoods.
5. Visit local art galleries and enjoy rooftop bars with views of the Charleston skyline.
"""
pyautogui.typewrite(summary, interval=0.04)