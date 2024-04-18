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

def calculate_score(board: Board, player: int, matrix: np.array) -> float:
    '''Calculate the score of a given board for a given player'''
    
    board_state = board.board
    score = (board_state == player) * matrix
    return np.sum(score)

def value_matrix_move(board, player) -> tuple[int, int]:
    '''Calculate a best move for player from matrix, return (None,None) to skip'''
    
    # Generate all possible moves
    moves = board.all_legal_moves(player)

    # Initialize the best score and move
    best_score = 0
    best_move = (None, None)
    
    # If the player has no legal moves -> skip
    if not moves:  
        return best_move
    
    for move in moves:
        # apply move to board copy
        row, col = move
        new_board = copy.deepcopy(board)
        new_board.make_move(row, col, player)
        
        # get score of such move
        score = calculate_score(new_board, player, evolved_matrix)

        # update for best move found on matrix
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move