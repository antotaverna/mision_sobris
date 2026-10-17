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
`settings.py`; a secret fifth one, `SECRET_CHARACTER`, peeks out of the bottom-right corner, or press 5),
then pick a mode from the menu (tap or click it, or use Up/Down + Enter, or press 1/2):

- **Classic**: eat cookies at your own pace. Touch a small cookie to eat it and grow;
  burnt (dark) cookies shrink you. Two dinosaur fossils (picked at random from a T. rex, a
  Triceratops, a Brontosaurus, and a Stegosaurus) are buried in the floor: walk over one to dig it up. One gives an explorer hat, the other a magnifying glass (a few dirt
  specks show up when you get close). For Juani and Male, each one can only
  be dug up when the cookie is big enough (eat cookies) or small enough (eat burnt ones); stepping on one
  at the wrong size marks the spot and says what's needed. Once both are dug up, two more get buried. Now and then a rare Argentinosaurus is buried too,
  and digging it up earns the Argentine medal. Dinosaurs a player is still missing get buried first, and
  completing all four earns a medal and starts the collection over. Each player's fossils,
  prizes, and medals are shown in a bar along the bottom of the screen, along with how the others are doing, and kept
  between games (the small "Borrar mi progreso" button on each player's menu clears theirs, after asking) (in `~/.mision_sobris.json` on desktop, in the browser's
  local storage on the web).
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
