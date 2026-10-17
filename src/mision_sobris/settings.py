# Portrait, since it's mostly played on phones.
WIDTH = 540
HEIGHT = 960
PANEL_HEIGHT = 222  # progress bar along the bottom during a round
PLAY_HEIGHT = HEIGHT - PANEL_HEIGHT  # where the cookies can be
HUD_HEIGHT = 90  # the score and menu button along the top of a round
FPS = 60
TITLE = "Misión Sobris"

BG_COLOR = (250, 236, 214)
TEXT_COLOR = (90, 55, 30)
HIGHLIGHT_COLOR = (200, 90, 40)
OVERLAY_COLOR = (250, 236, 214, 210)
CARD_COLOR = (255, 249, 238)  # solid background for signs and messages
PANEL_COLOR = (238, 218, 188)

# Cookie palettes: (edge, dough, chips)
COOKIE_COLORS = ((160, 105, 50), (214, 160, 90), (70, 40, 20))
BURNT_COLORS = ((30, 20, 15), (65, 42, 28), (20, 12, 8))
CHASER_COLORS = ((120, 60, 30), (175, 95, 50), (60, 25, 10))

# Playable characters, one per nephew/niece. accessory is one of:
# "cat_ears", "headphones", "crown", "spider", "spy_hat" (see entities.draw_accessory). The optional
# ride ("skateboard") is drawn under the cookie (see entities.draw_ride), and the optional
# hair ("curls" or "long", in hair_color) behind it (see entities.draw_hair). hard_finds makes the
# buried dinosaurs harder to find (see the HIDDEN_HARD_* settings).
CHARACTERS = [
    {"name": "Juani", "colors": ((205, 170, 110), (250, 228, 175), (90, 55, 25)),  # vanilla
     "accessory": "spider", "accent": (205, 25, 35), "hard_finds": True},
    {"name": "Lucha", "colors": ((150, 90, 40), (200, 135, 70), (105, 55, 20)),  # dulce de leche
     "accessory": "cat_ears", "accent": (60, 165, 80),
     "hair": "curls", "hair_color": (240, 195, 70)},  # golden
    {"name": "Male", "colors": ((120, 105, 170), (195, 185, 228), (60, 45, 125)),  # blueberry
     "accessory": "headphones", "accent": (130, 60, 190), "ride": "skateboard",
     "hard_finds": True},
    {"name": "Juli", "colors": ((200, 110, 130), (240, 170, 185), (175, 35, 65)),  # strawberry
     "accessory": "crown", "accent": (235, 185, 40),
     "hair": "curls", "hair_color": (190, 125, 70)},  # chestnut
]

# A secret extra player, peeking out of a corner of the character select.
SECRET_CHARACTER = {"name": "Anto", "colors": ((205, 175, 50), (250, 228, 120), (185, 135, 25)),  # lemon
                    "accessory": "spy_hat", "accent": (65, 65, 78), "hair": "long", "hair_color": (30, 25, 30),
                    "hard_finds": True}

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

# Hidden finds (Classic mode)
HIDDEN_FIND_DISTANCE = 30  # how close the player's center must get to dig something up
HIDDEN_HINT_DISTANCE = 130  # within this distance a few dirt specks start to show
# For characters with hard_finds: you have to walk right over it, and the hint shows up later.
HIDDEN_HARD_FIND_DISTANCE = 14
HIDDEN_HARD_HINT_DISTANCE = 60
# Some finds can only be dug up at a certain size: big (eat cookies) or small (eat burnt ones).
HIDDEN_BIG_RADIUS = 40  # about 8 cookies from the starting size
HIDDEN_SMALL_RADIUS = 18  # two burnt cookies from the starting size
FOSSIL_SCALE = 0.65  # size of a dug-up fossil on the floor
HIDDEN_DIG_TIME = 1.0  # seconds of flying dirt before the find shows up
HIDDEN_MESSAGE_TIME = 3.5  # seconds the "you found..." banner stays up
RARE_CHANCE = 0.2  # chance each new pair of finds comes with the rare Argentinosaurus too
REBURY_DELAY = 2.0  # seconds after both finds are dug up before two more get buried
EXPLORER_HAT_COLOR = (195, 160, 100)
# Accessories worn under the explorer hat; any other accessory is swapped for it.
ACCESSORIES_KEPT_UNDER_HAT = ("spider",)
