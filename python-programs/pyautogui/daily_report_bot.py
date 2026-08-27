from datetime import datetime

import pyautogui
import time

pyautogui.FAILSAFE = True

#Open chrome browser
pyautogui.press('win')
time.sleep(1)
pyautogui.write('chrome')
time.sleep(1)
pyautogui.press('enter')

#go to indianexpress.com
time.sleep(5)
pyautogui.write('https://indianexpress.com/')
time.sleep(1)
pyautogui.press('enter')

#copy the data from the website
time.sleep(5)
pyautogui.hotkey('ctrl', 'a')  # Select all
pyautogui.hotkey('ctrl', 'c')  # Copy the selected text

#create a new excel file with name date and time
time.sleep(2)
pyautogui.press('win')
time.sleep(1)
pyautogui.write('excel')
time.sleep(1)
pyautogui.press('enter')

#create three rows and 1st row with date and time
time.sleep(5)
now = datetime.now()
pyautogui.write(now.strftime("%Y-%m-%d %H:%M:%S"))
pyautogui.press('enter')
pyautogui.hotkey('ctrl', 'v')  # Paste the copied text
pyautogui.press('enter')
pyautogui.write('Done by Dinesh Kumar')

pyautogui.hotkey('ctrl', 's')  # Save the file
pyautogui.write('Daily_Report_' + now.strftime("%Y-%m-%d_%H-%M-%S") + '.xlsx')
pyautogui.press('enter')

#screenshot of the excel file
time.sleep(5)
pyautogui.screenshot('daily_report.png')

