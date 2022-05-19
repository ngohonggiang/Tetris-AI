import random, pygame, sys
from pygame.locals import *
import numpy as np

SOUND = True
FPS = 60
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10
NEXTPIECES = 3  # 6
BLANK = '.'

MOVESIDEWAYSFREQ = 0.05 * FPS
MOVESIDEWAYSDELAY = 0.2 * FPS
MOVEDOWNFREQ = 0.05 * FPS
LOCKTIME = 0.5 * FPS

# #       R    G    B
WHITE = (255, 255, 255)
GRAY = (185, 185, 185)
BLACK = (0, 0, 0)
RED = (155, 0, 0)
LIGHTRED = (175, 20, 20)
GREEN = (0, 155, 0)
LIGHTGREEN = (20, 175, 20)
BLUE = (20, 20, 175)
LIGHTBLUE = (40, 40, 195)
CYAN = (27, 226, 216)
LIGHTCYAN = (28, 255, 243)
YELLOW = (235, 230, 0)
LIGHTYELLOW = (255, 250, 20)
ORANGE = (234, 137, 82)
LIGHTORANGE = (255, 140, 0)
PURPLE = (136, 17, 173)
LIGHTPURPLE = (160, 30, 200)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS = (GREEN, RED, BLUE, ORANGE, CYAN, YELLOW, PURPLE)
LIGHTCOLORS = (LIGHTGREEN, LIGHTRED, LIGHTBLUE, LIGHTORANGE, LIGHTCYAN, LIGHTYELLOW, LIGHTPURPLE)
assert len(COLORS) == len(LIGHTCOLORS)  # each color must have light color

SHAPES = ['None',
          'S',
          'Z',
          'J',
          'L',
          'I',
          'O',
          'T']

SHAPE_TO_NUMBER = {'None': 0,
                   'S': 1,
                   'Z': 2,
                   'J': 3,
                   'L': 4,
                   'I': 5,
                   'O': 6,
                   'T': 7}

S_SHAPE_TEMPLATE = [['.OO',
                     'OO.',
                     '...'],
                    ['.O.',
                     '.OO',
                     '..O'],
                    ['...',
                     '.OO',
                     'OO.'],
                    ['O..',
                     'OO.',
                     '.O.', ]]

Z_SHAPE_TEMPLATE = [['OO.',
                     '.OO',
                     '...'],
                    ['..O',
                     '.OO',
                     '.O.'],
                    ['...',
                     'OO.',
                     '.OO'],
                    ['.O.',
                     'OO.',
                     'O..']]

I_SHAPE_TEMPLATE = [['....',
                     'OOOO',
                     '....',
                     '....'],
                    ['..O.',
                     '..O.',
                     '..O.',
                     '..O.'],
                    ['....',
                     '....',
                     'OOOO',
                     '....'],
                    ['.O..',
                     '.O..',
                     '.O..',
                     '.O..']]

O_SHAPE_TEMPLATE = [['.OO.',
                     '.OO.',
                     '....'],
                    ['.OO.',
                     '.OO.',
                     '....'],
                    ['.OO.',
                     '.OO.',
                     '....'],
                    ['.OO.',
                     '.OO.',
                     '....']]

J_SHAPE_TEMPLATE = [['O..',
                     'OOO',
                     '...'],
                    ['.OO',
                     '.O.',
                     '.O.'],
                    ['OOO',
                     '..O',
                     '...'],
                    ['.O.',
                     '.O.',
                     'OO.']]

L_SHAPE_TEMPLATE = [['..O',
                     'OOO',
                     '...'],
                    ['.O.',
                     '.O.',
                     '.OO'],
                    ['...',
                     'OOO',
                     'O..'],
                    ['OO.',
                     '.O.',
                     '.O.']]

T_SHAPE_TEMPLATE = [['.O.',
                     'OOO',
                     '...'],
                    ['.O.',
                     '.OO',
                     '.O.'],
                    ['...',
                     'OOO',
                     '.O.'],
                    ['.O.',
                     'OO.',
                     '.O.']]

T_SPIN_CHECK_TEMPLATE = ['O.O',
                         '...',
                         'O.O']

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}

PIECES_COLORS = {'S': 0,
                 'Z': 1,
                 'J': 2,
                 'L': 3,
                 'I': 4,
                 'O': 5,
                 'T': 6}

WALL_KICK_DATA = {'01': [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
                  '10': [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                  '12': [(0, 0), (1, 0), (1, -1), (0, 2), (1, 2)],
                  '21': [(0, 0), (-1, 0), (-1, 1), (0, -2), (-1, -2)],
                  '23': [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)],
                  '32': [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
                  '30': [(0, 0), (-1, 0), (-1, -1), (0, 2), (-1, 2)],
                  '03': [(0, 0), (1, 0), (1, 1), (0, -2), (1, -2)]}

WALL_KICK_DATA_I = {'01': [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
                    '10': [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
                    '12': [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)],
                    '21': [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
                    '23': [(0, 0), (2, 0), (-1, 0), (2, 1), (-1, -2)],
                    '32': [(0, 0), (-2, 0), (1, 0), (-2, -1), (1, 2)],
                    '30': [(0, 0), (1, 0), (-2, 0), (1, -2), (-2, 1)],
                    '03': [(0, 0), (-1, 0), (2, 0), (-1, 2), (2, -1)]}

SCORING_DATA = {'0': 0,
                'B0': 0,
                '1': 100,
                'B1': 100,
                'MT0': 100,
                'MT1': 200,
                'BMT1': 200,
                '2': 300,
                'B2': 300,
                'T0': 400,
                'BT0': 400,
                '3': 500,
                'B3': 500,
                '4': 800,
                'T1': 800,
                'BMT0': 150,
                'BT1': 1200,
                'B4': 1200,
                'T2': 1200,
                'T3': 1600,
                'BT2': 1800,
                'BT3': 2400}

LINE_CLEAR_DATA = {'0': 0,
                   '1': 1,
                   '2': 3,
                   'T0': 1,
                   '3': 5,
                   '4': 8,
                   'B4': 12,
                   'T1': 3,
                   'T2': 7,
                   'T3': 6}

pygame.init()

if SOUND:
    pygame.mixer.pre_init(48000, 16, 2, 4096)
    EFFECT_MOVE = pygame.mixer.Sound('music//move.wav')
    EFFECT_ROTATE = pygame.mixer.Sound('music//rotate.wav')
    EFFECT_HOLD = pygame.mixer.Sound('music//hold.wav')
    EFFECT_LOCK = pygame.mixer.Sound('music//lock.wav')
    EFFECT_CLEAR = pygame.mixer.Sound('music//clear.wav')

BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
