from board import Board
from copy import deepcopy

def greedy_move(position: Board, player: int) -> tuple[int, int]:
    '''Makes use of the board heuristic to greedily select next move'''
    
    # initialise
    best_move = (None, None)
    best_eval = 0

    legal_moves = position.all_legal_moves(player)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:
            position_deepcopy = deepcopy(position)
            position_deepcopy.make_move(row, col, player)
            eval = position_deepcopy.evaluate_board(player) # heuristic valuation
            if eval >= best_eval:
                best_move = (row, col)
                best_eval = eval
    
    return best_move