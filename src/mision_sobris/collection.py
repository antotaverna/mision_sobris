"""Each player's collection of dinosaur fossils, kept between games."""

import json
import sys
from pathlib import Path

WEB = sys.platform == "emscripten"
STORAGE_KEY = "mision_sobris_fossils"  # browser localStorage key
SAVE_PATH = Path.home() / ".mision_sobris.json"  # desktop save file


class Collection:
    def __init__(self):
        # player name -> {"fossils": species found, "rewards": rewards won, "medals": collections completed}
        self.found = self._load()

    def _load(self):
        try:
            if WEB:
                import platform  # pygbag's platform module exposes the browser window

                raw = platform.window.localStorage.getItem(STORAGE_KEY)
            else:
                raw = SAVE_PATH.read_text() if SAVE_PATH.exists() else None
            data = json.loads(raw) if raw else {}
            found = {}
            for name, entry in data.items():
                if isinstance(entry, list):  # older saves only listed the fossils
                    entry = {"fossils": entry}
                found[name] = {"fossils": list(entry.get("fossils", [])), "rewards": list(entry.get("rewards", [])),
                               "medals": int(entry.get("medals", 0))}
            return found
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

    def fossils(self, name):
        return self.found.get(name, {}).get("fossils", [])

    def rewards(self, name):
        return self.found.get(name, {}).get("rewards", [])

    def medals(self, name):
        return self.found.get(name, {}).get("medals", 0)

    def _entry(self, name):
        return self.found.setdefault(name, {"fossils": [], "rewards": [], "medals": 0})

    def complete(self, name):
        """A full collection earns a medal and starts over empty."""
        entry = self._entry(name)
        entry["medals"] += 1
        entry["fossils"] = []
        self._save()

    def add(self, name, kind, item):
        """Record a fossil or reward (kind is "fossils" or "rewards"). Returns True if it was new."""
        entry = self._entry(name)
        if item in entry[kind]:
            return False
        entry[kind].append(item)
        self._save()
        return True
