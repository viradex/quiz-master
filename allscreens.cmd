@echo off

REM Used for quick prototype testing for all screens
REM To switch to the next window, close the current window
REM The next window should open automatically

REM === MAIN SCREEN ===
python -m app

REM === CLIENT SCREENS ===
python -m client.setup
python -m client.lobby
python -m client.multi_question
python -m client.multi_result
python -m client.entry_question
python -m client.entry_result
python -m client.final_result
python -m client.disconnect

REM === SERVER SCREENS ===
python -m server.lobby
python -m server.multi_question
python -m server.multi_result
python -m server.entry_question
python -m server.entry_result
python -m server.final_result

REM === COMMON SCREENS ===
python -m common.about
python -m common.loading
