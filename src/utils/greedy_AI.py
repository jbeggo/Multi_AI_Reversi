from typing import final
from utils.board import Board
from copy import deepcopy

def greedy(position: Board) -> tuple[int, int]:
    
    # Check for game over
    if position.is_game_over():
        return position.evaluate_board()
    

    # else pick next move from simple greedy board evaluation

    highest_scoring_pos = 0
    final_move = (0,0)
    
    legal_moves = position.all_legal_moves(Board.WHITE)
    for row, col in legal_moves:
        
        if position.board[row, col] == Board.EMPTY:
            
            position_deepcopy = deepcopy(position) 
            position_deepcopy.set_discs(row, col, Board.WHITE)
            
            if position_deepcopy.evaluate_board > highest_scoring_pos:

                highest_scoring_pos = position_deepcopy.evaluate_board
                final_move = (row,col)
            
    return final_move