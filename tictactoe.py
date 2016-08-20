# coding: utf-8
"""Tic-tac-toe model. AI assumes AI_SYMBOL. """
import copy
import random

AI_SYMBOL = "X"
OPPONENT_SYMBOL = "O"
BLANK_SYMBOL = "_"

def check_win(board, symbol):
    """Returns True if the symbol appears in the board in a fashion that would mean a "win" for that symbol
    in standard Tic-Tac-Toe."""
    winConditions = [board[0], # rows
                    board[1],
                    board[2],
                    [board[0][0],board[1][0],board[2][0]], # columns
                    [board[0][1],board[1][1],board[2][1]],
                    [board[0][2],board[1][2],board[2][2]],
                    [board[0][0],board[1][1],board[2][2]], # diagonals
                    [board[0][2],board[1][1],board[2][0]]]
    for winCondition in winConditions:
        if winCondition == [symbol] * 3:
            return True
    full = True
    for row in board:
        for square in row:
            if square == BLANK_SYMBOL:
                full = False
    if full:
        return 0

    return False

class GameState(object):
    """Represents the state of the board at any given turn.

    self.board is a two-dimensional list containing lists of AI_SYMBOLs or OPPONENT_SYMBOLs.

    self.points is a value dependent on the 'win-state' of the board. X winning
    makes the board worth 10 points, O winning makes the board worth -10 points, and
    all other states (including draws) are worth 0 points.

    self.nextStates is a list of references to other GameState objects, created by calling GameState.iterate().

    self.prevState is a reference to the GameState which created the current instance. In the case of a blank board,
    prevState is equal to None.
    """

    def __init__(self, last_state, board, symbol):
        self.board = board
        self.points = self.check_points()
        self.nextStates = []
        self.prevState = last_state

    def __str__(self):
        rows = []
        rows.append("+-------+")
        for row in self.board:
            temp = row[::]
            temp.insert(0,"|")
            temp.append("|")
            rows.append(" ".join(temp))
        rows.append("+-------+")
        return "\n".join(rows)

    def check_points(self):
        """Sets the point value of the current state to either -10, 0, or 10."""
        if check_win(self.board,AI_SYMBOL):
            return 10
        elif check_win(self.board,OPPONENT_SYMBOL):
            return -10
        else:
            return 0

    def iterate(self, symbol):
        if symbol == AI_SYMBOL:
            nSymbol = OPPONENT_SYMBOL
        else:
            nSymbol = AI_SYMBOL
        r = 0
        c = 0
        for row in self.board:
            for square in row:
                if square == BLANK_SYMBOL:
                    temp = copy.deepcopy(self.board)
                    temp[r][c] = AI_SYMBOL
                    self.nextStates.append(GameState(self,temp,nSymbol))
                c+= 1
            r+= 1
            c = 0
        if self.nextStates == []:
            self.nextStates = None

class BeginningState(GameState):
    """Represents the initial state of the board. self.board is all BLANK_SYMBOL, points is 0, and prevState is None. """
    def __init__(self):
        self.board = [[BLANK_SYMBOL,BLANK_SYMBOL,BLANK_SYMBOL],[BLANK_SYMBOL,BLANK_SYMBOL,BLANK_SYMBOL],[BLANK_SYMBOL,BLANK_SYMBOL,BLANK_SYMBOL]]
        self.points = 0
        self.prevState = None
        self.nextStates = []

class SelfIteratingState(GameState):
    """Like GameState, but this version calls self.iterate()upon creation, so it'll create all
    valid game positions from its current state automatically. May take some time."""

    def __init__(self, last_state, board, symbol):
        self.board = board
        self.points = self.check_points()
        self.nextStates = []
        self.prevState = last_state
        self.symbol = symbol
        self.iterate(symbol)

    def check_points(self):
        """Sets the point value of the current state to either -10, 0, or 10."""
        if check_win(self.board,AI_SYMBOL):
            return 10
        elif check_win(self.board,OPPONENT_SYMBOL):
            return -10
        elif check_win(self.board,OPPONENT_SYMBOL) == 0:
            return 0
        elif check_win(self.board,AI_SYMBOL) == 0:
            return 0
        else:
            return None

    def mini_max(self):
        if self.points is not None:
            return self.points
        print self
        print "mini-max: " + str(self.points)
        scores = []
        for nextState in self.nextStates:
            scores.append(nextState.mini_max())
        scores.sort()
        if self.symbol == AI_SYMBOL:
            self.points = scores.pop()
        elif self.symbol == OPPONENT_SYMBOL:
            self.points = scores[0]

    """
    def sum_points(self):
        sum = 0
        if self.points is not None:
            return self.points
        else:
            for state in self.nextStates:
                if self.symbol == AI_SYMBOL:
                    sum += state.sum_points()
                elif self.symbol == OPPONENT_SYMBOL:
                    sum -= state.sum_points()
            return sum
    """
    def iterate(self, symbol):
        if symbol == AI_SYMBOL:
            nSymbol = OPPONENT_SYMBOL
        else:
            nSymbol = AI_SYMBOL
        r = 0
        c = 0
        for row in self.board:
            for square in row:
                if square == BLANK_SYMBOL:
                    temp = copy.deepcopy(self.board)
                    temp[r][c] = symbol
                    self.nextStates.append(SelfIteratingState(self,temp,nSymbol))
                c+= 1
            r+= 1
            c = 0

class AIPlayer(object):
    """Represents an AI player that decides the optimal move for any given
    position in a game of tic-tac-toe."""

    def __init__(self):
        self.symbol = AI_SYMBOL

    def random_move(self, game_board):
        """Makes a random valid move on the board."""
        game_board.iterate(self.symbol)
        return random.choice(game_board.nextStates)

    def move(self, game_board):
        """Accepts a GameState, then returns one with the optimal move for the
        AI made."""
        moveTree = self.predict(game_board)
        bestMove = moveTree.nextStates[0]
        bestScore = -100
        for state in moveTree.nextStates:
            state.mini_max()
            if state.points >= bestScore:
                print "Points: " + str(state.points)
                bestScore = state.points
                bestMove = state
        print bestScore
        return bestMove


    def predict(self, game_board):
        """Accepts a GameState, then returns a SelfIteratingState with all
        possible states placed in the GameState tree."""
        return SelfIteratingState(None,game_board.board,self.symbol)


def test():
    b = BeginningState()
    b.board[0][0] = "X"
    b.board[2][2] = "O"
    opponent = AIPlayer()
    b = opponent.move(b)
    print b

    b = opponent.move(b)
    print b

    b = opponent.move(b)
    print b

def parse():
    msg = raw_input("Your move: ")
    e = True
    while e:
        try:
            if msg == "game":
                return msg
            coords = msg.split(" ")
            coords[0] = int(coords[0])
            coords[1] = int(coords[1])
            assert coords[0] in range(0,3)
            assert coords[1] in range(0,3)
            return [coords[0],coords[1]]
        except Exception:
            print "Invalid move!"
            msg = raw_input("Your move: ")
            continue

def play():
    game = BeginningState()
    ai = AIPlayer()
    print "You move first. It's not like you're going to win."
    print game
    invalid = True
    coords = parse()
    game.board[coords[0]][coords[1]] = OPPONENT_SYMBOL
    print game
    print "Now, my move."
    game = ai.random_move(game)
    print game
    print "Your turn."

    while True:
        invalidInput = True
        coords = parse()
        while invalidInput:
            if coords == "game":
                print "Current state: "
                print game
                coords = parse()
            elif game.board[coords[0]][coords[1]] == BLANK_SYMBOL:
                game.board[coords[0]][coords[1]] = OPPONENT_SYMBOL
                invalid = False
                break
            else:
                print "Not there, you imbecile!"
                coords = parse()

        if check_win(game.board,OPPONENT_SYMBOL):
            print "What?! How?!"
            print game
            break
        elif game.nextStates is None:
            print "It's a draw, then."
            print game
            break

        print game
        print "Now, my move..."
        game = ai.move(game)
        print game

        if check_win(game.board,AI_SYMBOL):
            print "Hah! See, I knew I'd win!"
            break

        print "Your turn."
    print "GAME OVER"

play()
# test()
