@echo off

REM Used for quick prototype testing for all screens
REM To switch to the next window, close the current window
REM The next window should open automatically

REM === MAIN SCREEN ===
python ./app.py

REM === CLIENT SCREENS ===
python ./client/setup.py
python ./client/lobby.py
python ./client/multi_question.py
python ./client/multi_result.py
python ./client/entry_question.py
python ./client/entry_result.py

REM === COMMON SCREENS ===
python ./common/about.py
