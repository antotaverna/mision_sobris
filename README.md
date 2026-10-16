# mision_sobris

Misión Sobris: a tiny 2D cookie game built with Python and [pygame-ce](https://pyga.me/).
Each nephew/niece picks their own cookie character, then moves it around to eat the small
cookies and grow. The in-game text is in Spanish.

## Setup

```bash
conda env create -f environment.yml
conda activate mision_sobris
```

## Run

```bash
mision_sobris        # or: python -m mision_sobris.main
```

First pick a character (Juani, Lucha, Male, or Juli; they're defined in `CHARACTERS` in
`settings.py`), then pick a mode from the menu (tap or click it, or use Up/Down + Enter, or press 1/2):

- **Classic**: eat cookies at your own pace. Touch a small cookie to eat it and grow;
  burnt (dark) cookies shrink you.
- **Challenge**: 20 seconds to eat as many as you can, with burnt cookies too, while
  big angry cookies chase you (one slow, one fast); if one catches you, the round ends.

Controls:
- **Keyboard**: arrow keys / WASD to move, Esc to go back to the menu (or quit from the menu).
- **Touch or mouse**: touch and hold (or click and hold) and the cookie moves toward your finger.
  Tap a mode to start it, and use the on-screen Menu / Play again buttons.

## Browser version

The game also runs in a web browser via [pygbag](https://github.com/pygame-web/pygbag),
which `src/main.py` is the entry point for.

```bash
cd src
python -m pygbag --title "Misión Sobris" .   # serves it at http://localhost:8000
python -m pygbag --build --title "Misión Sobris" .   # just build into src/build/web
```

Pushing to `main` rebuilds it and publishes it to GitHub Pages
(`.github/workflows/deploy-web.yml`). The page needs a click before the game starts (browsers block audio and focus until then).

## Layout

- `src/main.py`: entry point for the browser build
- `src/mision_sobris/main.py`: game loop, menu, and rounds
- `src/mision_sobris/entities.py`: player, cookies, and chasers
- `src/mision_sobris/settings.py`: window size, colors, speeds, challenge tuning
- `assets/`: images, sounds, fonts
