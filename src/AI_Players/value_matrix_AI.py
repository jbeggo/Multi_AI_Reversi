from utils.board import Board
import numpy as np
import copy

# matrix derived from FryLiZheng "Using Reinforcement Learning to Play Othello"
frylizheng = np.array([
    [3.2125, 1.775,  1.875,  1.975,  1.975,  1.875,  1.775,  3.2125],
    [0.15,   2.3,    0.6625, 1.8375, 1.8375, 0.6625, 2.3,    0.15],
    [3.525,  0.85,   2.675,  0.175,  0.175,  2.675,  0.85,   3.525],
    [1.125,  1.95,   0.15,   0,      0,      0.15,   1.95,   1.125],
    [1.125,  1.95,   0.15,   0,      0,      0.15,   1.95,   1.125],
    [3.525,  0.85,   2.675,  0.175,  0.175,  2.675,  0.85,   3.525],
    [0.15,   2.3,    0.6625, 1.8375, 1.8375, 0.6625, 2.3,    0.15],
    [3.2125, 1.775,  1.875,  1.975,  1.975,  1.875,  1.775,  3.2125]
])

# matrix derived from evolutionary strategy in evolutionary training
evolved_matrix = np.array([
    [3.2125, 1.7928, 1.875,  1.9948, 1.975,  1.8938, 1.7572, 3.2125],
    [0.15,   2.3228, 0.6625, 1.8375, 1.8375, 0.6624, 2.3,    0.1515],
    [3.525,  0.85,   2.7017, 0.1768, 0.175,  2.675,  0.85,   3.525 ],
    [1.125,  1.9498, 0.15,   0.,     0.,     0.15,   1.9305, 1.125 ],
    [1.125,  1.9695, 0.1515, 0.,     0.,     0.1485, 1.9305, 1.125 ],
    [3.4898, 0.85,   2.675,  0.1732, 0.175,  2.6482, 0.8331, 3.5602],
    [0.15,   2.277,  0.6625, 1.8559, 1.8559, 0.6559, 2.3,    0.1515],
    [3.2125, 1.7571, 1.9127, 2.0147, 1.975,  1.8938, 1.775,  3.2125]
])

# matrix derived from Matthew Deucette - 1998 WipeOut Reversi Engine 
wipeout_matrix = np.array([
    [100, -20,  10,   5,   5,  10, -20, 100],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
    [  5,  -2,  -1,   0,   0,  -1,  -2,   5],
    [  5,  -2,  -1,   0,   0,  -1,  -2,   5],
    [ 10,  -2,  -1,  -1,  -1,  -1,  -2,  10],
    [-20, -50,  -2,  -2,  -2,  -2, -50, -20],
    [100, -20,  10,   5,   5,  10, -20, 100]
])

def end_game_close(board: Board) -> bool:
    '''Determine if the game is nearing an end from occupancy'''
    
    # if all corners occupied
    corners = (board.board[0, 0], board.board[0,7], board.board[7, 0], board.board[7, 7])
    corners_occupied = 0
    for corner in corners:
        if corner == -1 or corner == 1:
            corners_occupied += 1
    corners_full = (corners_occupied == 4)
    
    # or if most of board is occupied
    total_positions = 64
    occupied = np.count_nonzero(board.board)
    return occupied >= 0.8 * total_positions or corners_full

def early_score(board: Board, player: int, matrix: np.array) -> float:
    '''Calculate the positional score as for early game'''

    # early game score as described in Nees Jan van Eck, Michiel van Wezel
    player_eval = np.sum((board.board == player) * matrix)
    opp_eval = np.sum((board.board == -player) * matrix)
    return player_eval - opp_eval

def endgame_score(board: Board, player: int) -> int:
    '''Simple disk parity check during endgame as detailed in Wipeout'''
    player_count = np.sum(board.board == player)
    opponent_count = np.sum(board.board == -player)
    return player_count - opponent_count

def value_matrix_move(board: Board, player: int, matrix: np.array) -> tuple[int, int]:
    '''Calculate a best move for player from matrix, return (None,None) to skip'''
    
    # Generate all possible moves
    moves = board.all_legal_moves(player)

    # Initialize the score and move
    best_score = float('-inf')
    best_move = (None, None)
    
    # If the player has no legal moves -> skip
    if not moves:  
        return best_move
    
    for move in moves:
        row, col = move
        new_board = copy.deepcopy(board)
        new_board.make_move(row, col, player)

        # switch to parity play
        if end_game_close(new_board):
            score = endgame_score(new_board, player)
        # else play by matrix
        else:
            score = early_score(new_board, player, matrix)

        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move