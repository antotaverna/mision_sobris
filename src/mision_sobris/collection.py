"""Each player's collection of dinosaur fossils, kept between games."""

import json
import sys
from pathlib import Path

WEB = sys.platform == "emscripten"
STORAGE_KEY = "mision_sobris_fossils"  # browser localStorage key
SAVE_PATH = Path.home() / ".mision_sobris.json"  # desktop save file


class Collection:
    def __init__(self):
        self.found = self._load()  # player name -> species found, in the order found

    def _load(self):
        try:
            if WEB:
                import platform  # pygbag's platform module exposes the browser window

                raw = platform.window.localStorage.getItem(STORAGE_KEY)
            else:
                raw = SAVE_PATH.read_text() if SAVE_PATH.exists() else None
            data = json.loads(raw) if raw else {}
            return {name: list(species) for name, species in data.items()}
        except Exception:
            # An unreadable save just means starting a fresh collection.
            return {}

    def _save(self):
        raw = json.dumps(self.found, ensure_ascii=False)
        try:
            if WEB:
                import platform

                platform.window.localStorage.setItem(STORAGE_KEY, raw)
            else:
                SAVE_PATH.write_text(raw)
        except Exception:
            pass  # not being able to save shouldn't stop the game

    def of(self, name):
        return self.found.get(name, [])

    def add(self, name, species):
        """Record a find. Returns True if it was new for this player."""
        found = self.found.setdefault(name, [])
        if species in found:
            return False
        found.append(species)
        self._save()
        return True
