import pygame
from pygame.locals import *
import string
import ConfigParser

#--------------------------------------------------------
#  Constants
#--------------------------------------------------------

AI = "ai"
HUMAN = "human"
FIXED = "fixed"
MANUAL = "manual"

#game phases
STACKING = "stacking"
PLACEMENT = "placement"
DVONN_PLACEMENT = "dvonn placement"

#Space image ids
EMPTY = "empty"
BLACK = "Black"
WHITE = "White"
RED = "red"
HIGHLIGHT = "highlight"
BUTTON = "button"
PUSHED_BUTTON = "pushed button"
DVONN = "dvonn"
TARGET = "target"

#DIRECTIONS
LEFT=1
UP_LEFT=2
UP_RIGHT=3
RIGHT=4
DOWN_RIGHT=5
DOWN_LEFT=6
ALL_DIRECTIONS = (LEFT,UP_LEFT,UP_RIGHT,RIGHT,DOWN_RIGHT,DOWN_LEFT)
#MOUSE BUTTONS
M_LEFT=1
M_RIGHT=3

#--------------------------------------------------------
#  convenience methods
#--------------------------------------------------------

#converts a string with an unparenthisized tuple into a real tuple
# must contain only integers
def parse_tuple( s):
    ts = string.split(s,",")
    ints = []
    for t in ts:
        ints.append(string.atoi(t))
    return tuple(ints)

#--------------------------------------------------------
#  Configurable stuff
#--------------------------------------------------------

CONFIG_FILE = "dvonn.cfg"

CONFIG = ConfigParser.ConfigParser()
CONFIG.readfp(open(CONFIG_FILE))

TICK_TIME = CONFIG.getint("general","clock.tick")
AI_WAIT_TIME_PARTIAL= CONFIG.getint("general","ai.wait.time.partial")
AI_WAIT_TIME_COMPLETE= CONFIG.getint("general","ai.wait.time.complete")

FONT_SIZE = CONFIG.getint("font","size")
FONT_COLOR = parse_tuple( CONFIG.get("font","color"))
HIGHLIGHT_COLOR = parse_tuple( CONFIG.get("font","highlight.color"))
OFF_COLOR = parse_tuple( CONFIG.get("font","off.color"))
FONT_FILE =CONFIG.get("font","filename")
ANTIALIAS = CONFIG.getboolean("font","antialias")
FONT = None

#contains (filename,transparent)
IMAGE_LOOKUP = { EMPTY:( CONFIG.get("bitmaps","empty"),0),
                 BLACK:( CONFIG.get("bitmaps","black"),0),
                 WHITE:( CONFIG.get("bitmaps","white"),0),
                 RED:( CONFIG.get("bitmaps","red"),0),
                 HIGHLIGHT:( CONFIG.get("bitmaps","highlight"),1),
                 DVONN:( CONFIG.get("bitmaps","dvonn"),1),
                 TARGET:( CONFIG.get("bitmaps","target"),1),
                 BUTTON:( CONFIG.get("bitmaps","button"),0),
                 PUSHED_BUTTON:( CONFIG.get("bitmaps","pushed.button"),0),
                 "icon":( CONFIG.get("bitmaps","icon"),0)}



#this has to be done after pygame has initializes
def initialize():
    global FONT
    global IMAGE_STORE
    FONT = pygame.font.Font(FONT_FILE,FONT_SIZE)
    IMAGE_STORE = load_all_images()

def render_font(text,color=FONT_COLOR):
    return FONT.render(text,ANTIALIAS,color)

def load_image(file, transparent):
    "loads an image, prepares it for play"
    try:
        surface = pygame.image.load(file)
    except pygame.error:
        raise SystemExit, 'Could not load image "%s" %s'%(file, pygame.get_error())
    if transparent:
        corner = surface.get_at((0, 0))
        surface.set_colorkey(corner, RLEACCEL)
    return surface.convert()

def get_image(key):
    global IMAGE_STORE
    return IMAGE_STORE[key]

def lookup_image(key):
    return load_image(IMAGE_LOOKUP[key][0], IMAGE_LOOKUP[key][1])

def load_all_images():
    images  = {}
    for key in IMAGE_LOOKUP.keys():
        images[key] = lookup_image(key)
    return images

