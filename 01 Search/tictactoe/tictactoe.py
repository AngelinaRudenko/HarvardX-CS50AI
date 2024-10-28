"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # In the initial game state, X gets the first move.
    # Any return value is acceptable if a terminal board is provided as input

    count = 0

    for row in board:
        for cell in row:
            if (cell != EMPTY):
                count += 1

    if (count % 2 == 0):
        return X     
    
    return O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Possible moves are any cells on the board that do not already have an X or an O in them.
    # Any return value is acceptable if a terminal board is provided as input.

    actions = []
    for i in range(len(board)): 
        for j in range(len(board)):
            if (board[i][j] == EMPTY):
                actions.append((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board
    without modifying the original board
    """
    # If action is not a valid action for the board, your program should raise an exception.

    i = action[0]
    j = action[1]

    if (board[i][j] != EMPTY):
        raise NameError('Invalid action')

    turn = player(board)
    newBoard = copy.deepcopy(board)
    newBoard[i][j] = turn

    return newBoard


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    # check by row
    for row in range(len(board)):
        if (board[row][0] == board[row][1] == board[row][2] != EMPTY):
            return board[row][0]
        
    # check by column
    for col in range(len(board)):
        if (board[0][col] == board[1][col] == board[2][col] != EMPTY):
            return board[0][col]
        
    # check diagonals
    if (board[0][0] == board[1][1] == board[2][2]): # \
        return board[1][1]
    
    if (board[0][2] == board[1][1] == board[2][0]): # /
        return board[1][1]

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """

    if (winner(board) != None):
        return True

    for i in range(len(board)): 
        for j in range(len(board)):
            if (board[i][j] == EMPTY):
                return False
            
    return True


# accept a terminal board as input 
def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if (win == X):
        return 1
    elif (win == O):
        return -1
    else:
        return 0

xDesiredScore = 1
oDesiredScore = -1

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """

    if (terminal(board)):
        return None

    turn = player(board)
    acts = actions(board)
    bestScoreActionId = 0

    bestScore = -math.inf       # initial value for X
    desiredScore = xDesiredScore
    if (turn == O):
        bestScore = math.inf    # initial value for O
        desiredScore = oDesiredScore
       
    for i in range(len(acts)): 
        newBoard = result(board, acts[i])

        if (turn == X):
            actScore = min_value(newBoard)
        else: # turn O
            actScore = max_value(newBoard)
            
        if ((turn == X and actScore > bestScore) or
            (turn == O and actScore < bestScore)):
                bestScore = actScore
                bestScoreActionId = i

                # Mini optimization - no need to search more, if we already found winning combination.
                # It will not find any better
                # Can be commented to make it more generic solution
                if (actScore == desiredScore): 
                    break

    return acts[bestScoreActionId]

# X turn - wants to maximize
def max_value(board):
    if (terminal(board)):
        return utility(board)

    score = -math.inf
    for act in actions(board): 
        newBoard = result(board, act)
        score = max(score, min_value(newBoard))

        # Mini optimization - no need to search more, if we already found winning combination.
        # It will not find any better
        # Can be commented to make it more generic solution
        if (score == xDesiredScore):
            break

    return score

# O turn - wants to minimize
def min_value(board):
    if (terminal(board)):
        return utility(board)

    score = math.inf
    for act in actions(board): 
        newBoard = result(board, act)
        score = min(score, max_value(newBoard))

        # Mini optimization - no need to search more, if we already found winning combination.
        # It will not find any better
        # Can be commented to make it more generic solution
        if (score == oDesiredScore):
            break

    return score