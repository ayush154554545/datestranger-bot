"""
Root entrypoint wrapper for DateStranger bot.
Allows running via either `python bot.py` or `python bot/bot.py`.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_DIR = os.path.join(BASE_DIR, "bot")
if BOT_DIR not in sys.path:
    sys.path.insert(0, BOT_DIR)

if __name__ == "__main__":
    import runpy
    runpy.run_path(os.path.join(BOT_DIR, "bot.py"), run_name="__main__")
