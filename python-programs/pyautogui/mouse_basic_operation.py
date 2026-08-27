import pyautogui
import time

pyautogui.FAILSAFE = True


pyautogui.click(250, 250)  # Move the mouse to (250, 250) and click
time.sleep(1)  # Wait for 1 second
pyautogui.moveTo(500, 500, duration=1)  # Move the mouse to (500, 500) over 1 second


pyautogui.dragTo(600, 600, duration=1)  # Drag the mouse to (600, 600) over 1 second

pyautogui.scroll(500)  # Scroll up 500 units
time.sleep(2)  # Wait for 2 seconds
pyautogui.scroll(-500)  # Scroll down 500 units
time.sleep(2)  # Wait for 2 seconds

pyautogui.doubleClick(500, 500)  # Double click at (500, 500)

time.sleep(2)  # Wait for 2 seconds

pyautogui.rightClick(800, 500)  # Right click at (800, 500)