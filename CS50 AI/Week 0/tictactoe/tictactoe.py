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
    return [[EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY], [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for row in board:
        for space in row:
            if space == EMPTY:
                count += 1
    if count % 2 == 1:
        return "X"
    else:
        return "O"


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    moves = set()
    for i, row in enumerate(board):
        for j, space in enumerate(row):
            if space == EMPTY:
                moves.add((i, j))
    return moves


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    action = list(action)  # Converting Set to List
    if not (
        0 <= action[0] <= 2
        and 0 <= action[1] <= 2
        and board[action[0]][action[1]] == EMPTY
    ):
        raise ValueError("Invalid move: out of bounds or spot already taken.")
    else:
        curr_player = player(board)
        new_board = copy.deepcopy(board)
        new_board[action[0]][action[1]] = curr_player
        return new_board


def check_left_right(board):
    for i in board:
        if i[0] == i[1] == i[2] != EMPTY:
            return i[0]
    return EMPTY


def check_up_down(board):
    for i in range(3):
        if board[0][i] == board[1][i] == board[2][i] != EMPTY:
            return board[0][i]
    return EMPTY


def check_diagonals(board):
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        return board[0][0]
    elif board[2][0] == board[1][1] == board[0][2] != EMPTY:
        return board[2][0]
    return EMPTY


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    player = check_left_right(board)
    if player != EMPTY:
        return player
    player = check_up_down(board)
    if player != EMPTY:
        return player
    player = check_diagonals(board)
    if player != EMPTY:
        return player
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    player = winner(board)
    if player == None:
        for row in board:
            for space in row:
                if space == EMPTY:
                    return False
        return True
    else:
        return True


def maximize(board):
    """
    Returns a tuple with most possible score at its first index and move at its second index
    """
    if terminal(board):
        return (utility(board), None)
    moves = actions(board)
    safe_move = 0  # Safest Move
    worst_move = 0  # Worst Move
    if len(moves) == 1:
        moves = list(moves)
        return (utility(result(board, moves[0])), moves[0])
    for move in moves:
        score, _ = minimize(result(board, move))  # Doing Cross Recursion kinda thing
        if score > 0:
            return score, move  # Alpha beta prunning here, skipping the calls ahead
        elif score == 0:
            safe_move = move
        else:
            worst_move = move
    # After All moves select the best move available
    if safe_move != 0:
        return 0, safe_move
    else:
        return -1, worst_move


def minimize(board):
    """
    Returns a tuple with the least possible score at its first index and move at its second index
    """
    if terminal(board):
        return (utility(board), None)
    moves = actions(board)
    if len(moves) == 1:
        moves = list(moves)
        return (utility(result(board, moves[0])), moves[0])
    safe_move = 0
    worst_move = 0
    for move in moves:
        score, _ = maximize(result(board, move))  # Doing Cross Recursion kinda thing
        if score < 0:
            return score, move  # Alpha beta prunning here, skipping the calls ahead
        elif score == 0:
            safe_move = move
        else:
            worst_move = move
    # After All moves select the best move available
    if safe_move != 0:
        return 0, safe_move
    else:
        return 1, worst_move


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    player = winner(board)
    if player == X:
        return 1
    elif player == O:
        return -1
    else:
        return 0


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # Simple Minimax Call
    curr_player = player(board)
    if curr_player == X:
        return maximize(board)[1]
    else:
        return minimize(board)[1]
