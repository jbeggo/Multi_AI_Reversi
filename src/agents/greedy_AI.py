from utils.board import Board
import random
from copy import deepcopy

def greedy_move(board: Board, player: int) -> tuple[int, int]:
    '''Makes use of the board heuristic to greedily select next move'''
    
    # initialise
    best_move = (None, None)
    best_eval = float('-inf')

    legal_moves = board.all_legal_moves(player)
    if legal_moves: # if there are legal moves
        for row, col in legal_moves:
            if board.board[row, col] == Board.EMPTY:
                board_copy = deepcopy(board)
                board_copy.make_move(row, col, player)
                eval = board_copy.evaluate_board(player) # heuristic valuation
                if eval >= best_eval:
                    best_move = (row, col)
                    best_eval = eval
    
    return best_move

def greedy_move_nondet(board: Board, player: int, epsilon = 0.1) -> tuple[int, int]:
    '''Makes use of the board heuristic to greedily select next move non-deterministically with exploration''' 
    
    # initialise
    best_move = (None, None)
    best_eval = float('-inf')

    legal_moves = board.all_legal_moves(player)
    if legal_moves: # if there are legal moves
        for row, col in legal_moves:
            if board.board[row, col] == Board.EMPTY:
                board_copy = deepcopy(board)
                board_copy.make_move(row, col, player)
                eval = board_copy.evaluate_board(player) # heuristic valuation
                if eval >= best_eval:
                    best_move = (row, col)
                    best_eval = eval
    
    if random.random() < epsilon:
        return random.choice(legal_moves)
    
    return best_move