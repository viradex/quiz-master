# Quiz Master

Play quizzes against your friends to learn in a competitive and engaging way!

Run this command before running the program for the first time:

```
pip install -r requirements.txt
```

To run the program:

```
python main.py
```

## Demo Mode

To run this app in Demo Mode, set `DEMO_MODE` in `core/config/constants.py` to `True`. Useful for public showcases of the app :)

In Demo Mode, the app will:

- Display a small watermark on the main menu.
- Disable the regular Exit button on the main menu.
- Disable and pre-fill the server IP address on the client setup screen.

## Architecture Guide

The application contains three high-level parts:

- Game Client
- Game Server
- Quiz Editor

If you are a developer or interested in understanding how the code works high-level, see `ARCHITECTURE.md`.
