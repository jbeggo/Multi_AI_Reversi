from utils.board import Board
from copy import deepcopy

def negamax(position: Board, depth: int, alpha: int, beta: int, player: int) -> int:
    '''Implements Negamax with alpha-beta pruning to determine next best move'''
    
    # Check for game over or no depth set
    if depth == 0 or position.is_game_over() is True:
        return position.evaluate_board(Board.WHITE)
    
    
    max_eval = float('-inf')
    legal_moves = position.all_legal_moves(player)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) 
            position_deepcopy.make_move(row, col, player)

            # switch the player
            opponents_player = Board.BLACK if player == Board.WHITE else Board.WHITE
            eval = -negamax(position_deepcopy, depth - 1, -beta, -alpha, opponents_player)
            max_eval = max(max_eval, eval)

            alpha = max(alpha, eval)
            if alpha >= beta:
                break

    return max_eval

def negamax_move(position: Board, player: int) -> tuple[int, int]:
    '''Uses negamax to return a move coord tuple for player'''
    
    bestMove = (None,None)
    bestEval = float('-inf') if player == Board.BLACK else float('inf')
    
    legal_moves = position.all_legal_moves(player)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) # create a deep copy of the board position
            position_deepcopy.make_move(row, col, player)

            currentEval = -negamax(position_deepcopy, 2, float('-inf'), float('inf'), Board.BLACK if player == Board.WHITE else Board.WHITE)

            if (player == Board.WHITE and currentEval < bestEval) or (player == Board.BLACK and currentEval > bestEval):
                bestMove = (row, col)
                bestEval = currentEval

    return bestMove
