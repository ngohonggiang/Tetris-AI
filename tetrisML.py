from att import *

BOARDHEIGHT = 25
NUM_INPUTS = 8

HIDINGMARGIN = 102
XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5 + HIDINGMARGIN

PIECES_ONEHOT = {'None': np.array([1, 0, 0, 0, 0, 0, 0, 0]),
                 'S': np.array([0, 1, 0, 0, 0, 0, 0, 0]),
                 'Z': np.array([0, 0, 1, 0, 0, 0, 0, 0]),
                 'J': np.array([0, 0, 0, 1, 0, 0, 0, 0]),
                 'L': np.array([0, 0, 0, 0, 1, 0, 0, 0]),
                 'I': np.array([0, 0, 0, 0, 0, 1, 0, 0]),
                 'O': np.array([0, 0, 0, 0, 0, 0, 1, 0]),
                 'T': np.array([0, 0, 0, 0, 0, 0, 0, 1])}

ONEHOT = [np.array([1, 0, 0, 0, 0, 0, 0, 0]),
          np.array([0, 1, 0, 0, 0, 0, 0, 0]),
          np.array([0, 0, 1, 0, 0, 0, 0, 0]),
          np.array([0, 0, 0, 1, 0, 0, 0, 0]),
          np.array([0, 0, 0, 0, 1, 0, 0, 0]),
          np.array([0, 0, 0, 0, 0, 1, 0, 0]),
          np.array([0, 0, 0, 0, 0, 0, 1, 0]),
          np.array([0, 0, 0, 0, 0, 0, 0, 1])]


class Bag:
    def __init__(self):
        self.bag = []
        self.nextpiece = self.getPieceOld()

    def newBag(self):
        self.bag = [n for n in range(1, len(SHAPES))]
        random.shuffle(self.bag)

    def getPiece(self):
        if len(self.bag) == 0:
            self.newBag()
        index = random.choice(self.bag)
        self.bag.remove(index)

        rpiece = self.nextpiece
        self.nextpiece = SHAPES[index]
        return rpiece

    def getPieceOld(self):
        if len(self.bag) == 0:
            self.newBag()
        index = random.choice(self.bag)
        self.bag.remove(index)
        return SHAPES[index]


def checkForTSpin(piece, board, lastSuccessfulMovement):
    # check if T
    if piece['shape'] != 'T':
        return ""

    # check if the last succesfull movement was a rotation
    if lastSuccessfulMovement != "rotate":
        return ""

    # return "T" if 3 or more diagonals are obstructed
    diagonalsObstructed = 0
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            if T_SPIN_CHECK_TEMPLATE[y][x] == BLANK:
                continue
            try:
                if board[x + piece['x']][y + piece['y']] != BLANK:
                    diagonalsObstructed += 1
            except IndexError:
                diagonalsObstructed += 1

    if diagonalsObstructed >= 3:
        return "T"
    else:
        return ""


def rotatePiece(piece, rotation, board):
    initialRotation = piece['rotation']
    desiredRotation = (piece['rotation'] + rotation) % len(PIECES[piece['shape']])
    if piece['shape'] == 'I':
        for x, y in WALL_KICK_DATA_I[str(initialRotation) + str(desiredRotation)]:
            piece['rotation'] = desiredRotation
            piece['x'] = piece['x'] + x
            piece['y'] = piece['y'] - y
            if isValidPosition(board, piece):
                return True
            else:
                piece['rotation'] = initialRotation
                piece['x'] = piece['x'] - x
                piece['y'] = piece['y'] + y
    elif piece['shape'] == 'O':
        return False
    else:
        for x, y in WALL_KICK_DATA[str(initialRotation) + str(desiredRotation)]:
            piece['rotation'] = desiredRotation
            piece['x'] = piece['x'] + x
            piece['y'] = piece['y'] - y
            if isValidPosition(board, piece):
                return True
            else:
                piece['rotation'] = initialRotation
                piece['x'] = piece['x'] - x
                piece['y'] = piece['y'] + y


def makeTextObjs(text, font, draw_color):
    surf = font.render(text, True, draw_color)
    return surf, surf.get_rect()


def getNewPiece(BAG):
    # return a random new piece in a random rotation and color
    shape = BAG.getPiece()
    newPiece = {'shape': shape,
                'rotation': 0,
                'x': 3,
                'y': BOARDHEIGHT - 22,  # start it above the board (i.e. 18 because board is 40 high)
                'color': PIECES_COLORS[shape]}
    return newPiece


def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[x + piece['x']][y + piece['y']] = piece['color']


def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return 0 <= x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN - HIDINGMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, draw_color, DISPLAYSURF, pixelx=None, pixely=None, ghost=False):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if draw_color == BLANK:
        return
    if pixelx is None and pixely is None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[draw_color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    if ghost:
        pygame.draw.rect(DISPLAYSURF, [0, 0, 0], (pixelx + 3, pixely + 3, BOXSIZE - 5, BOXSIZE - 5))
    else:
        pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[draw_color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board, DISPLAYSURF):
    # fill the background of the board
    # pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y], DISPLAYSURF)

    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR,
                     (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)


def drawBoxToObscurePiece(DISPLAYSURF):
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN - 10, BOXSIZE * BOARDWIDTH, -100))


def drawStatus(score, level, DISPLAYSURF):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def getWidth(piece):
    return len(PIECES[piece['shape']][0][0])


def getHeight(piece):
    return len(PIECES[piece['shape']][0])


def drawPiece(piece, DISPLAYSURF, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx is None and pixely is None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], DISPLAYSURF, pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawGhostPiece(piece, ghostPieceYOffset, DISPLAYSURF):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'] + ghostPieceYOffset)

    # draw each of the boxes that make up the piece
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], DISPLAYSURF, pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE),
                        ghost=True)


def drawNextPieces(pieces, DISPLAYSURF):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" pieces
    for i, p in enumerate(pieces):
        drawPiece(p, DISPLAYSURF, pixelx=WINDOWWIDTH - 120, pixely=100 + 45 * i)


def drawHoldPiece(piece, DISPLAYSURF):
    # draw the "hold" text
    holdSurf = BASICFONT.render('Hold:', True, TEXTCOLOR)
    holdRect = holdSurf.get_rect()
    holdRect.topleft = (WINDOWWIDTH - 520, 80)
    DISPLAYSURF.blit(holdSurf, holdRect)
    # draw the "hold" piece
    if piece is not None:
        drawPiece(piece, DISPLAYSURF, pixelx=WINDOWWIDTH - 520, pixely=100)


def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    ret = True
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            ret = False
    return ret


def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1  # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][pullDownY] = board[x][pullDownY - 1]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        else:
            y -= 1  # move on to check next row up
    return numLinesRemoved


def getHeuristicBoard(board):
    heights = []
    holes = 0
    for x in range(BOARDWIDTH):
        lowest = 0
        for y in range(BOARDHEIGHT):  # Get the highest
            lowest = y
            if board[x][y] != BLANK:
                break
        heights.append(BOARDHEIGHT - lowest)

        roof = False
        for y in range(BOARDHEIGHT):  # Get the holes
            if board[x][y] == BLANK:
                if roof:
                    holes += 1
            else:
                roof = True

    bumps = [abs(j - i) for i, j in zip(heights[:-1], heights[1:])]

    height = sum(heights)
    bumpiness = sum(bumps)
    return height, holes, bumpiness

#XXXXXXXXXXX
def getHeuristicScore(board, lines):
    height, holes, bumpiness = getHeuristicBoard(board)
    return -0.51 * height + 0.76 * lines - 0.36 * holes - 0.18 * bumpiness


def getHeuristicBoardNP(board):
    heights = []
    holes = 0
    for x in range(BOARDWIDTH):
        lowest = 0
        for y in range(BOARDHEIGHT):  # Get the highest
            lowest = y
            if board[y, x] != 0:
                break
        heights.append(BOARDHEIGHT - lowest)

        roof = False
        for y in range(BOARDHEIGHT):  # Get the holes
            if board[y, x] == 0:
                if roof:
                    holes += 1
            else:
                roof = True

    bumps = [abs(j - i) for i, j in zip(heights[:-1], heights[1:])]

    height = sum(heights)
    bumpiness = sum(bumps)
    return height, holes, bumpiness


def getHeuristicScoreNP(board, lines):
    height, holes, bumpiness = getHeuristicBoardNP(board)
    return -0.51 * height + 0.76 * lines - 10.66 * holes - 1.38 * bumpiness


def isValidPositionNP(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[y + piece['y'] + adjY, x + piece['x'] + adjX] != 0:
                return False
    return True


def addToBoardNP(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(getWidth(piece)):
        for y in range(getHeight(piece)):
            if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                board[y + piece['y'], x + piece['x']] = 1


def rotatePieceNP(piece, rotation, board):
    initialRotation = piece['rotation']
    desiredRotation = (piece['rotation'] + rotation) % len(PIECES[piece['shape']])
    if piece['shape'] == 'I':
        for x, y in WALL_KICK_DATA_I[str(initialRotation) + str(desiredRotation)]:
            piece['rotation'] = desiredRotation
            piece['x'] = piece['x'] + x
            piece['y'] = piece['y'] - y
            if isValidPositionNP(board, piece):
                return True
            else:
                piece['rotation'] = initialRotation
                piece['x'] = piece['x'] - x
                piece['y'] = piece['y'] + y
    elif piece['shape'] == 'O':
        return False
    else:
        for x, y in WALL_KICK_DATA[str(initialRotation) + str(desiredRotation)]:
            piece['rotation'] = desiredRotation
            piece['x'] = piece['x'] + x
            piece['y'] = piece['y'] - y
            if isValidPositionNP(board, piece):
                return True
            else:
                piece['rotation'] = initialRotation
                piece['x'] = piece['x'] - x
                piece['y'] = piece['y'] + y


def moveLeft(board, piece):
    # moving the piece left
    if isValidPositionNP(board, piece, adjX=-1):
        piece['x'] -= 1


def moveRight(board, piece):
    # moving the piece right
    if isValidPositionNP(board, piece, adjX=1):
        piece['x'] += 1


def rotateRight(board, piece):
    # rotating the piece (if there is room to rotate)
    rotatePieceNP(piece, 1, board)


def rotateLeft(board, piece):
    # rotate the other direction
    rotatePieceNP(piece, -1, board)


def hardDrop(board, piece):
    # move the current piece all the way down
    for i in range(1, BOARDHEIGHT):
        if not isValidPositionNP(board, piece, adjY=i):
            piece['y'] += i - 1
            break


class TetrisGame:
    def __init__(self, name, field, hold, nextpieces, log=False):
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.BAG = Bag()
        self.FPSCLOCK = pygame.time.Clock()

        pygame.display.set_caption(name)

        # start music
        if SOUND:
            if random.randint(0, 1) == 0:
                pygame.mixer.music.load('music//tetrisb.mid')
            else:
                pygame.mixer.music.load('music//tetrisc.mid')
            pygame.mixer.music.play(-1, 0.0)

        # setup variables for the start of the game
        self.frame = 0
        self.board = getBlankBoard()
        self.BAG.newBag()
        self.lastFallTime = 0
        self.canUseHold = True
        self.lockTime = LOCKTIME
        self.lastPieceLock = None
        self.lastSuccessfulMovement = None
        self.ghostPieceYOffset = 0
        self.score = 0
        self.heuristic = 0
        self.lastScore = 0
        self.lastheuristic = 0
        self.combo = 0
        self.lines = 0
        self.linesCleared = 0
        self.moves = 0
        self.linesGoal = 5
        self.level = 1
        self.fallFreq = 1
        self.calculateLevelAndFallFreq()

        self.fallingPiece = getNewPiece(self.BAG)
        self.nextPieces = [getNewPiece(self.BAG) for _ in range(NEXTPIECES)]
        self.holdPiece = None

        self.num_actions = 41  # 4 * 10 + 1 Rotations Columns Hold
        self.num_features = BOARDHEIGHT * (BOARDWIDTH + 8) * self.num_actions  # 8 columns for the pieces
        self.featureShape = (self.num_actions, BOARDHEIGHT, BOARDWIDTH + 8)
        self.stateSize = BOARDHEIGHT * (BOARDWIDTH + 8)
        self.stateShape = (BOARDHEIGHT, BOARDWIDTH + 8)

        # Stats
        self.log = log
        self.scores = []
        self.gamelengths = []
        self.scoreChanges = []
        self.heuristicChanges = []

        # Features for the learning
        self.featureField = field
        self.featureHold = hold
        self.featureNext = nextpieces

    def reset(self):
        if self.log:
            self.scores.append(self.score)
            self.gamelengths.append(self.frame)

        self.frame = 0
        self.board = getBlankBoard()
        self.BAG.newBag()
        self.lastFallTime = 0
        self.canUseHold = True
        self.lockTime = LOCKTIME
        self.lastPieceLock = None
        self.lastSuccessfulMovement = None
        self.ghostPieceYOffset = 0
        self.score = 0
        self.heuristic = 0
        self.lastScore = 0
        self.lastheuristic = 0
        self.combo = 0
        self.lines = 0
        self.linesCleared = 0
        self.moves = 0
        self.linesGoal = 5
        self.level = 1
        self.fallFreq = 1
        self.calculateLevelAndFallFreq()

        self.fallingPiece = getNewPiece(self.BAG)
        self.nextPieces = [getNewPiece(self.BAG) for _ in range(NEXTPIECES)]
        self.holdPiece = None

        return self.getFeatures()

    def gameOver(self):
        self.reset()

    def runGame(self):
        # setup variables for the start of the game

        observation = self.reset()
        while True:  # game loop
            actions_value = self.getBestAction(observation)
            action = np.argmax(actions_value)
            if action == 40:  # Prevent it from using hold when not available
                action = np.argsort(actions_value)[-2]
            observation, reward = self.nextFrame(action)
            pygame.time.wait(500)
            checkForQuit()

    def getBestAction(self, f):
        features = np.reshape(f, [self.num_actions, self.stateShape[0], self.stateShape[1]])
        scores = []
        for state in features:
            scores.append(getHeuristicScoreNP(state[:, :BOARDWIDTH], self.linesCleared))
        return scores

    def generateAllStates(self, f):
        states = []

        # Generate states
        for action in range(self.num_actions):
            features = f.copy()
            board = features[:, :BOARDWIDTH]

            # (holdpiece, fallingpiece, nextpieces, canusehold, nextpiece4nextpieces)
            holdn = int(features[0, BOARDWIDTH])
            fallingn = int(features[1, BOARDWIDTH])
            fallingpiece = {'shape': SHAPES[fallingn],
                            'rotation': 0,
                            'x': 3,
                            'y': BOARDHEIGHT - 22}  # start it above the board (i.e. 18 because board is 40 high)

            nextn = [int(features[2 + i, BOARDWIDTH]) for i in range(NEXTPIECES)]
            canusehold = int(features[2 + NEXTPIECES, BOARDWIDTH])
            nextern = int(features[3 + NEXTPIECES, BOARDWIDTH])

            # Handle action
            if action < 40:
                # 10 columns, 4 rotations, 40 actions
                # action range from 0 to 39
                # column 0 to 9
                column = int(np.floor(action / 4))
                # rotation 0 to 3
                rotation = int(np.remainder(action, 4))

                # rotate right n times
                for n in range(rotation):
                    rotateRight(board, fallingpiece)

                # move to column
                movement = column - 4
                if movement < 0:
                    for n in range(0 - movement):
                        moveLeft(board, fallingpiece)
                else:
                    for n in range(movement):
                        moveRight(board, fallingpiece)

                # hard drop
                hardDrop(board, fallingpiece)
                addToBoardNP(board, fallingpiece)

                fallingn = 0
            else:
                # action is hold
                if canusehold:
                    h = holdn
                    holdn = fallingn
                    fallingn = h
                    canusehold = 0

            if fallingn == 0:
                fallingn = nextn.pop(0)
                nextn.append(nextern)

            # Generate features
            # Concatenate all the pieces info together
            # (holdpiece, fallingpiece, nextpieces, canusehold)
            if self.featureHold:
                pieces = [ONEHOT[holdn], ONEHOT[fallingn]]
            else:
                pieces = [ONEHOT[0], ONEHOT[fallingn]]

            for i, n in enumerate(nextn):
                if i < self.featureNext:
                    pieces.append(ONEHOT[n])
                else:
                    pieces.append(ONEHOT[0])

            pieces.append(ONEHOT[canusehold])

            # Add zeros to have the height match with the board
            pieces = np.vstack(pieces)

            zeros = np.zeros((BOARDHEIGHT - NEXTPIECES - 3, 8))
            pieces = np.concatenate((pieces, zeros), axis=0)

            if not self.featureField:
                board = np.zeros([BOARDHEIGHT, BOARDWIDTH])

            board = np.concatenate((board, pieces), axis=1)

            state = np.reshape(board, self.stateSize)
            states.append(state)

        return np.vstack(states)

    def getFeatures(self):
        # get board
        board = np.zeros([BOARDHEIGHT, BOARDWIDTH])
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.board[x][y] != BLANK:
                    board[y, x] = 1

        # Concatenate all the pieces info together
        # (holdpiece, fallingpiece, nextpieces, canusehold, nextpiece4nextpieces)
        pieces = []

        if self.holdPiece is not None:
            pieces.append(SHAPE_TO_NUMBER[self.holdPiece['shape']])
        else:
            pieces.append(SHAPE_TO_NUMBER['None'])

        if self.fallingPiece is not None:
            pieces.append(SHAPE_TO_NUMBER[self.fallingPiece['shape']])
        else:
            pieces.append(SHAPE_TO_NUMBER['None'])

        for piece in self.nextPieces:
            pieces.append(SHAPE_TO_NUMBER[piece['shape']])

        if self.canUseHold:
            pieces.append(SHAPE_TO_NUMBER['S'])
        else:
            pieces.append(SHAPE_TO_NUMBER['None'])

        pieces.append(SHAPE_TO_NUMBER[self.BAG.nextpiece])

        # Add zeros to have the height match with the board
        pieces = np.vstack(pieces)
        zeros = np.zeros((BOARDHEIGHT - len(self.nextPieces) - 4, 1))
        pieces = np.concatenate((pieces, zeros), axis=0)

        board = np.concatenate((board, pieces), axis=1)

        allstates = self.generateAllStates(board)

        return allstates.reshape(self.num_features)

    def getFeaturesOld(self):
        # get board
        board = np.zeros([BOARDHEIGHT, BOARDWIDTH])
        for x in range(BOARDWIDTH):
            for y in range(BOARDHEIGHT):
                if self.board[x][y] != BLANK:
                    board[y, x] = 1

        # Concatenate all the pieces info together
        # (holdpiece, fallingpiece, nextpieces, canusehold, nextpiece4nextpieces)
        pieces = []

        if self.holdPiece is not None:
            pieces.append(PIECES_ONEHOT[self.holdPiece['shape']])
        else:
            pieces.append(PIECES_ONEHOT['None'])

        if self.fallingPiece is not None:
            pieces.append(PIECES_ONEHOT[self.fallingPiece['shape']])
        else:
            pieces.append(PIECES_ONEHOT['None'])

        for piece in self.nextPieces:
            pieces.append(PIECES_ONEHOT[piece['shape']])

        if self.canUseHold:
            pieces.append(PIECES_ONEHOT['S'])
        else:
            pieces.append(PIECES_ONEHOT['None'])

        pieces.append(PIECES_ONEHOT[self.BAG.nextpiece])

        # Add zeros to have the height match with the board
        pieces = np.vstack(pieces)
        zeros = np.zeros((BOARDHEIGHT - len(self.nextPieces) - 4, 8))
        pieces = np.concatenate((pieces, zeros), axis=0)

        board = np.concatenate((board, pieces), axis=1)
        features = board.reshape(self.num_features)

        return features

    def nextFrame(self, action=0):
        if action < 40:
            # 10 columns, 4 rotations, 40 actions
            # action range from 0 to 39
            # column 0 to 9
            column = int(np.floor(action / 4))
            # rotation 0 to 3
            rotation = int(np.remainder(action, 4))

            # rotate right n times
            for n in range(rotation):
                self.rotateRight()

            # move to column
            movement = column - 4
            if movement < 0:
                for n in range(0 - movement):
                    self.moveLeft()
            else:
                for n in range(movement):
                    self.moveRight()

            # hard drop
            self.hardDrop()

        else:
            # action is hold
            self.hold()

        # check if the falling piece is touching the ground
        if not isValidPosition(self.board, self.fallingPiece, adjY=1):
            self.lastFallTime = self.frame
            self.lockTime -= 1
            if self.lockTime < 0:
                if self.fallingPiece['y'] < BOARDHEIGHT - 21:
                    self.gameOver()  # lock out: a piece locked in above the screen
                    return self.getFeatures(), -100

                # check for T-spin
                tspin = checkForTSpin(self.fallingPiece, self.board, self.lastSuccessfulMovement)

                addToBoard(self.board, self.fallingPiece)
                linesCleared = removeCompleteLines(self.board)
                self.linesCleared += linesCleared

                # line values for variable-goal levels
                if linesCleared == 0:
                    self.combo = 0
                    if SOUND:
                        EFFECT_LOCK.play()
                elif linesCleared == 1:
                    self.score += 20 * self.combo * self.level
                    self.combo += 1
                    if SOUND:
                        EFFECT_CLEAR.play()
                else:
                    self.score += 50 * self.combo * self.level
                    self.combo += 1
                    if SOUND:
                        EFFECT_CLEAR.play()

                currentAction = str(linesCleared)
                currentAction = tspin + currentAction

                if currentAction == self.lastPieceLock:
                    currentAction = "B" + currentAction

                try:
                    self.lines += LINE_CLEAR_DATA[currentAction]
                except KeyError:
                    pass

                self.lastPieceLock = currentAction
                self.score += SCORING_DATA[currentAction] * self.level

                self.calculateLevelAndFallFreq()

                # No falling piece in play, so start a new piece at the top
                self.fallingPiece = self.nextPieces.pop(0)
                self.nextPieces.append(getNewPiece(self.BAG))
                self.lastFallTime = 0  # reset lastFallTime
                self.lockTime = LOCKTIME
                self.moves = 0
                self.canUseHold = True

                if not isValidPosition(self.board, self.fallingPiece):
                    self.gameOver()  # can't fit a new piece on the board, so game over
                    return self.getFeatures(), -100

        # let the piece fall if it is time to fall
        if self.frame - self.lastFallTime > self.fallFreq:
            self.lastFallTime = self.frame
            # see if the piece has landed
            if isValidPosition(self.board, self.fallingPiece, adjY=1):
                self.fallingPiece['y'] += 1
                self.lastSuccessfulMovement = "moveDown"

        # calculate the ghost piece
        if self.fallingPiece is not None:
            for i in range(1, BOARDHEIGHT):
                if not isValidPosition(self.board, self.fallingPiece, adjY=i):
                    self.ghostPieceYOffset = i - 1
                    break

        self.heuristic = getHeuristicScore(self.board, self.linesCleared)
        scoreChange = self.score - self.lastScore
        heuristicChange = self.heuristic - self.lastheuristic
        if action == 40:  # punishment for spamming hold
            heuristicChange = -3
        self.lastScore = self.score
        self.lastheuristic = self.heuristic

        if self.log:
            self.scoreChanges.append(scoreChange)
            self.heuristicChanges.append(heuristicChange)

        # drawing everything on the screen
        self.DISPLAYSURF.fill(BGCOLOR)
        drawStatus(np.round(self.heuristic, 1), self.level, self.DISPLAYSURF)
        drawNextPieces(self.nextPieces, self.DISPLAYSURF)
        drawHoldPiece(self.holdPiece, self.DISPLAYSURF)
        if self.fallingPiece is not None:
            # drawGhostPiece(self.fallingPiece, self.ghostPieceYOffset, self.DISPLAYSURF)
            drawPiece(self.fallingPiece, self.DISPLAYSURF)
        drawBoard(self.board, self.DISPLAYSURF)
        drawBoxToObscurePiece(self.DISPLAYSURF)

        self.frame += 1
        pygame.event.pump()
        pygame.display.update()

        return self.getFeatures(), heuristicChange

    def calculateLevelAndFallFreq(self):
        # Based on the score, return the level the player is on and
        # how many seconds pass until a falling piece falls one space.
        if self.lines >= self.linesGoal:
            self.level += 1
            self.linesGoal += 5 * self.level

        self.fallFreq = ((0.8 - ((self.level - 1) * 0.007)) ** (self.level - 1)) * FPS

    def hold(self):
        # hold piece
        if self.canUseHold:
            # swap hold and falling piece
            if SOUND:
                EFFECT_HOLD.play()
            oldHoldPiece = self.holdPiece
            self.holdPiece = self.fallingPiece
            self.fallingPiece = oldHoldPiece
            if self.fallingPiece is None:
                self.fallingPiece = self.nextPieces.pop(0)
                self.nextPieces.append(getNewPiece(self.BAG))

            self.lastFallTime = 0  # reset lastFallTime
            self.lockTime = LOCKTIME
            self.moves = 0

            self.holdPiece['rotation'] = 0
            self.holdPiece['x'] = 3
            self.holdPiece['y'] = BOARDHEIGHT - 22
            self.canUseHold = False

    def moveLeft(self):
        # moving the piece left
        if isValidPosition(self.board, self.fallingPiece, adjX=-1):
            self.fallingPiece['x'] -= 1
            self.lastSuccessfulMovement = "moveLeft"
            if SOUND:
                EFFECT_MOVE.play()
            if not self.lockTime == LOCKTIME and self.moves < 16:
                self.lockTime = LOCKTIME
                self.moves += 1

    def moveRight(self):
        # moving the piece right
        if isValidPosition(self.board, self.fallingPiece, adjX=1):
            self.fallingPiece['x'] += 1
            self.lastSuccessfulMovement = "moveRight"
            if SOUND:
                EFFECT_MOVE.play()
            if not self.lockTime == LOCKTIME and self.moves < 16:
                self.lockTime = LOCKTIME
                self.moves += 1

    def rotateRight(self):
        # rotating the piece (if there is room to rotate)
        if rotatePiece(self.fallingPiece, 1, self.board):
            self.lastSuccessfulMovement = "rotate"
            if SOUND:
                EFFECT_ROTATE.play()
            if not self.lockTime == LOCKTIME and self.moves < 16:
                self.lockTime = LOCKTIME
                self.moves += 1

    def rotateLeft(self):
        # rotate the other direction
        if rotatePiece(self.fallingPiece, -1, self.board):
            self.lastSuccessfulMovement = "rotate"
            if SOUND:
                EFFECT_ROTATE.play()
            if not self.lockTime == LOCKTIME and self.moves < 16:
                self.lockTime = LOCKTIME
                self.moves += 1

    def softDrop(self):
        # making the piece fall faster with the down key
        if isValidPosition(self.board, self.fallingPiece, adjY=1):
            self.fallingPiece['y'] += 1
            self.score += 1
            self.lastSuccessfulMovement = "moveDown"

    def hardDrop(self):
        # move the current piece all the way down
        self.lockTime = -1
        for i in range(1, BOARDHEIGHT):
            if not isValidPosition(self.board, self.fallingPiece, adjY=i):
                self.fallingPiece['y'] += i - 1
                self.score += 2 * (i - 1)
                self.lastSuccessfulMovement = "moveDown"
                break

def checkForQuit():
    for _ in pygame.event.get(QUIT):  # get all the QUIT events
        pygame.quit()
        sys.exit()

if __name__ == '__main__':
    tetris = TetrisGame("Tetris", True, True, 3)
    tetris.runGame()
