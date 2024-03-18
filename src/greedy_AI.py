from board import Board
from copy import deepcopy

def greedy_move(position: Board, player_color: int) -> tuple[int, int]:
    
    # initialise
    best_move = (None, None)
    best_eval = 0

    legal_moves = position.all_legal_moves(player_color)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:
            position_deepcopy = deepcopy(position)
            position_deepcopy.make_move(row, col, player_color)
            eval = position_deepcopy.evaluate_board(player_color)
            if eval >= best_eval:
                best_move = (row, col)
                best_eval = eval
    
    return best_move