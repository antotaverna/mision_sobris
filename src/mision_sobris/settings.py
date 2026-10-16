WIDTH = 960
HEIGHT = 540
FPS = 60
TITLE = "Cookie eats cookies"

BG_COLOR = (250, 236, 214)
TEXT_COLOR = (90, 55, 30)
HIGHLIGHT_COLOR = (200, 90, 40)
OVERLAY_COLOR = (250, 236, 214, 210)

# Cookie palettes: (edge, dough, chips)
COOKIE_COLORS = ((160, 105, 50), (214, 160, 90), (70, 40, 20))
BURNT_COLORS = ((30, 20, 15), (65, 42, 28), (20, 12, 8))
CHASER_COLORS = ((120, 60, 30), (175, 95, 50), (60, 25, 10))

PLAYER_RADIUS = 28
PLAYER_MIN_RADIUS = 16
PLAYER_MAX_RADIUS = 80
PLAYER_GROWTH = 1.5  # radius gained per cookie eaten
PLAYER_SPEED = 300  # pixels per second

COOKIE_RADIUS = 12
COOKIE_COUNT = 8  # cookies on screen at once

BURNT_COUNT = 3
BURNT_SHRINK = 6  # radius lost per burnt cookie eaten

# Challenge mode
CHALLENGE_TIME = 20  # seconds
CHASER_RADIUS = 34
CHASER_SPEEDS = (70, 115)  # pixels per second; one chaser per entry
CHASER_SPAWN_DISTANCE = 300  # minimum distance from the player when spawning
