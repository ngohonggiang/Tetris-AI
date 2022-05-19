from att import *

BOARDHEIGHT = 40
X_MARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOP_MARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5 + 400

SHAPES = ['I', 'J', 'L', 'O', 'S', 'T', 'Z']


class Bag:
    def __init__(self):
        self.bag = []

    def newBag(self):
        self.bag = [n for n in range(0, len(PIECES.keys()))] # chỉ số các mảnh ghép
        random.shuffle(self.bag) # hoán vị các chỉ số

    # Lấy 1 mảnh ngẫu nhiên
    def getPiece(self):
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
            if board[x + piece['x']][y + piece['y']] != BLANK:
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


# def terminate():
#     pygame.quit()
#     sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text, DISPLAYSURF, FPSCLOCK):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() is None:
        pygame.display.update()
        FPSCLOCK.tick(FPS)


def checkForQuit():
    for _ in pygame.event.get(QUIT):  # get all the QUIT events
        pygame.quit()
        sys.exit()  # terminate if any QUIT events are present
    # for event in pygame.event.get(KEYUP):  # get all the KEYUP events
    #     if event.key == K_ESCAPE:
    #         terminate()  # terminate if the KEYUP event was for the Esc key
    #     pygame.event.post(event)  # put the other KEYUP event objects back


def getNewPiece(BAG):
    # return a random new piece in a random rotation and color
    shape = BAG.getPiece()
    newPiece = {'shape': shape,
                'rotation': 0,
                'x': 3,
                'y': 18,  # start it above the board (i.e. 18 because board is 40 high)
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


def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True


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


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (X_MARGIN + (boxx * BOXSIZE)), (TOP_MARGIN - 400 + (boxy * BOXSIZE))


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
                     (X_MARGIN - 3, TOP_MARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)


def drawBoxToObscurePiece(DISPLAYSURF):
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (X_MARGIN, TOP_MARGIN - 10, BOXSIZE * BOARDWIDTH, -100))


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
                drawBox(None, None, piece['color'], DISPLAYSURF, pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE), ghost=True)


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


class TetrisGame:
    def __init__(self):
        self.DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
        self.BAG = Bag()
        self.FPSCLOCK = pygame.time.Clock()

        pygame.display.set_caption('Tetris')
        showTextScreen('Tetris', self.DISPLAYSURF, self.FPSCLOCK)

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
        self.lastMoveDownTime = self.frame
        self.lastMoveSidewaysTime = self.frame
        self.lastMoveSidewaysInput = self.frame
        self.lastFallTime = 0
        self.movingDown = False  # note: there is no movingUp variable
        self.movingLeft = False
        self.movingRight = False
        self.canUseHold = True
        self.lockTime = LOCKTIME
        self.lastPieceLock = None
        self.lastSuccessfulMovement = None
        self.ghostPieceYOffset = 0
        self.score = 0
        self.combo = 0
        self.lines = 0
        self.moves = 0
        self.linesGoal = 5
        self.level = 1
        self.fallFreq = 1
        self.calculateLevelAndFallFreq()

        self.fallingPiece = getNewPiece(self.BAG)
        self.nextPieces = [getNewPiece(self.BAG) for _ in range(NEXTPIECES)]
        self.holdPiece = None

    def resetGame(self):
        # start music
        if SOUND:
            if random.randint(0, 1) == 0:
                pygame.mixer.music.load('music//tetrisb.mid')
            else:
                pygame.mixer.music.load('music//tetrisc.mid')
        pygame.mixer.music.play(-1, 0.0)

        self.frame = 0
        self.board = getBlankBoard()
        self.BAG.newBag()
        self.lastMoveDownTime = self.frame
        self.lastMoveSidewaysTime = self.frame
        self.lastMoveSidewaysInput = self.frame
        self.lastFallTime = 0
        self.movingDown = False  # note: there is no movingUp variable
        self.movingLeft = False
        self.movingRight = False
        self.canUseHold = True
        self.lockTime = LOCKTIME
        self.lastPieceLock = None
        self.lastSuccessfulMovement = None
        self.ghostPieceYOffset = 0
        self.score = 0
        self.combo = 0
        self.lines = 0
        self.moves = 0
        self.linesGoal = 5
        self.level = 1
        self.fallFreq = 1
        self.calculateLevelAndFallFreq()

        self.fallingPiece = getNewPiece(self.BAG)
        self.nextPieces = [getNewPiece(self.BAG) for _ in range(NEXTPIECES)]
        self.holdPiece = None

    def endGame(self):
        pygame.mixer.music.stop()
        showTextScreen('Game Over', self.DISPLAYSURF, self.FPSCLOCK)

    def gameOver(self):
        self.endGame()
        self.resetGame()

    def runGame(self):
        # setup variables for the start of the game

        while True:  # game loop
            self.nextFrame()
            self.FPSCLOCK.tick(FPS)

    def nextFrame(self):
        if self.fallingPiece is None:
            # No falling piece in play, so start a new piece at the top
            self.fallingPiece = self.nextPieces.pop(0)
            self.nextPieces.append(getNewPiece(self.BAG))
            self.lastFallTime = 0  # reset lastFallTime
            self.lockTime = LOCKTIME
            self.moves = 0
            self.canUseHold = True

            if not isValidPosition(self.board, self.fallingPiece):
                self.gameOver()  # can't fit a new piece on the board, so game over
                return

        checkForQuit()
        for event in pygame.event.get():  # event handling loop
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    # Pausing the game
                    self.DISPLAYSURF.fill(BGCOLOR)
                    pygame.mixer.music.stop()
                    showTextScreen('Paused', self.DISPLAYSURF, self.FPSCLOCK)  # pause until a key press
                    pygame.mixer.music.play(-1, 0.0)
                    self.lastFallTime = self.frame
                    self.lastMoveDownTime = self.frame
                    self.lastMoveSidewaysTime = self.frame
                elif event.key == K_LEFT or event.key == K_a:
                    self.movingLeft = False
                elif event.key == K_RIGHT or event.key == K_d:
                    self.movingRight = False
                elif event.key == K_DOWN or event.key == K_s:
                    self.movingDown = False

            elif event.type == KEYDOWN:
                # moving the piece sideways
                if (event.key == K_LEFT or event.key == K_a) and isValidPosition(self.board, self.fallingPiece, adjX=-1):
                    self.fallingPiece['x'] -= 1
                    self.movingLeft = True
                    self.movingRight = False
                    self.lastMoveSidewaysTime = self.frame
                    self.lastMoveSidewaysInput = self.frame
                    self.lastSuccessfulMovement = "moveLeft"
                    EFFECT_MOVE.play()
                    if not self.lockTime == LOCKTIME and self.moves < 16:
                        self.lockTime = LOCKTIME
                        self.moves += 1

                elif (event.key == K_RIGHT or event.key == K_d) and isValidPosition(self.board, self.fallingPiece, adjX=1):
                    self.fallingPiece['x'] += 1
                    self.movingRight = True
                    self.movingLeft = False
                    self.lastMoveSidewaysTime = self.frame
                    self.lastMoveSidewaysInput = self.frame
                    self.lastSuccessfulMovement = "moveRight"
                    EFFECT_MOVE.play()
                    if not self.lockTime == LOCKTIME and self.moves < 16:
                        self.lockTime = LOCKTIME
                        self.moves += 1

                # rotating the piece (if there is room to rotate)
                elif event.key == K_UP or event.key == K_x:
                    if rotatePiece(self.fallingPiece, 1, self.board):
                        self.lastSuccessfulMovement = "rotate"
                        EFFECT_ROTATE.play()
                        if not self.lockTime == LOCKTIME and self.moves < 16:
                            self.lockTime = LOCKTIME
                            self.moves += 1
                elif event.key == K_z:  # rotate the other direction
                    if rotatePiece(self.fallingPiece, -1, self.board):
                        self.lastSuccessfulMovement = "rotate"
                        EFFECT_ROTATE.play()
                        if not self.lockTime == LOCKTIME and self.moves < 16:
                            self.lockTime = LOCKTIME
                            self.moves += 1

                # making the piece fall faster with the down key
                elif event.key == K_DOWN or event.key == K_s:
                    self.movingDown = True
                    if isValidPosition(self.board, self.fallingPiece, adjY=1):
                        self.fallingPiece['y'] += 1
                        self.score += 1
                        self.lastSuccessfulMovement = "moveDown"
                        self.lastMoveDownTime = self.frame

                # move the current piece all the way down
                elif event.key == K_SPACE:
                    self.movingDown = False
                    self.movingLeft = False
                    self.movingRight = False
                    self.lockTime = -1
                    for i in range(1, BOARDHEIGHT):
                        if not isValidPosition(self.board, self.fallingPiece, adjY=i):
                            self.fallingPiece['y'] += i - 1
                            self.score += 2 * (i - 1)
                            self.lastSuccessfulMovement = "moveDown"
                            break

                # hold piece
                elif (event.key == K_c) and self.canUseHold:
                    # swap hold and falling piece
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
                    self.holdPiece['y'] = 18
                    self.canUseHold = False

        # handle moving the piece because of user input
        if (self.movingLeft or self.movingRight) and self.frame - self.lastMoveSidewaysTime > MOVESIDEWAYSFREQ and self.frame - self.lastMoveSidewaysInput > MOVESIDEWAYSDELAY:
            if self.movingLeft and isValidPosition(self.board, self.fallingPiece, adjX=-1):
                self.fallingPiece['x'] -= 1
                self.lastSuccessfulMovement = "moveLeft"
                EFFECT_MOVE.play()
            elif self.movingRight and isValidPosition(self.board, self.fallingPiece, adjX=1):
                self.fallingPiece['x'] += 1
                self.lastSuccessfulMovement = "moveRight"
                EFFECT_MOVE.play()
            self.lastMoveSidewaysTime = self.frame

        if self.movingDown and self.frame - self.lastMoveDownTime > MOVEDOWNFREQ:
            if isValidPosition(self.board, self.fallingPiece, adjY=1):
                self.fallingPiece['y'] += 1
                self.score += 1
                self.lastSuccessfulMovement = "moveDown"
                self.lastMoveDownTime = self.frame

        if not isValidPosition(self.board, self.fallingPiece, adjY=1):
            self.lastFallTime = self.frame
            self.lockTime -= 1
            if self.lockTime < 0:
                if self.fallingPiece['y'] < 19:
                    self.gameOver()  # lock out: a piece locked in above the screen
                    return

                # check for T-spin
                tspin = checkForTSpin(self.fallingPiece, self.board, self.lastSuccessfulMovement)

                addToBoard(self.board, self.fallingPiece)
                linesCleared = removeCompleteLines(self.board)

                # line values for variable-goal levels
                if linesCleared == 0:
                    self.combo = 0
                    EFFECT_LOCK.play()
                elif linesCleared == 1:
                    self.score += 20 * self.combo * self.level
                    self.combo += 1
                    EFFECT_CLEAR.play()
                else:
                    self.score += 50 * self.combo * self.level
                    self.combo += 1
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
                self.fallingPiece = None

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

        # drawing everything on the screen
        self.DISPLAYSURF.fill(BGCOLOR)
        drawStatus(self.score, self.level, self.DISPLAYSURF)
        drawNextPieces(self.nextPieces, self.DISPLAYSURF)
        drawHoldPiece(self.holdPiece, self.DISPLAYSURF)
        if self.fallingPiece is not None:
            drawGhostPiece(self.fallingPiece, self.ghostPieceYOffset, self.DISPLAYSURF)
            drawPiece(self.fallingPiece, self.DISPLAYSURF)
        drawBoard(self.board, self.DISPLAYSURF)
        drawBoxToObscurePiece(self.DISPLAYSURF)

        self.frame += 1
        pygame.display.update()

    def calculateLevelAndFallFreq(self):
        # Based on the score, return the level the player is on and
        # how many seconds pass until a falling piece falls one space.
        if self.lines >= self.linesGoal:
            self.level += 1
            self.linesGoal += 5 * self.level

        self.fallFreq = ((0.8 - ((self.level - 1) * 0.007)) ** (self.level - 1)) * FPS


if __name__ == '__main__':
    tetris = TetrisGame()
    tetris.runGame()