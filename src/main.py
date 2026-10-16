# Entry point for the browser build (pygbag looks for a top-level main.py).
# On desktop, run the game with the `mision_sobris` command instead.
import asyncio

# pygbag only loads packages it sees imported here, so pygame must be imported
# directly even though only mision_sobris.main uses it.
import pygame  # noqa: F401

from mision_sobris.main import run

asyncio.run(run())
