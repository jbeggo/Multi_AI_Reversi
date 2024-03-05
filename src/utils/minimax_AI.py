from utils.board import Board
from copy import deepcopy

def minimax(position: Board, depth: int, alpha: int, beta: int, isMaximizingPlayer: bool) -> int:
    
    # Check for game over or no depth set
    if depth == 0 or position.is_game_over() is True:
        return position.evaluate_board()
    
    if isMaximizingPlayer:
        maxEval = float('-inf')
        legal_moves = position.all_legal_moves(Board.BLACK)
        for row, col in legal_moves:
            if position.board[row, col] == Board.EMPTY:

                position_deepcopy = deepcopy(position) 
                position_deepcopy.set_discs(row, col, Board.BLACK)

                opponents_moves = position_deepcopy.all_legal_moves(Board.WHITE)
                eval = minimax(position_deepcopy, depth - 1, alpha, beta, opponents_moves == set())
                maxEval = max(maxEval, eval)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break

        return maxEval

    # else minimizing player's turn
    minEval = float('+inf')
    legal_moves = position.all_legal_moves(Board.WHITE)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) 
            position_deepcopy.set_discs(row, col, Board.WHITE)

            opponents_moves = position_deepcopy.all_legal_moves(Board.BLACK)
            eval = minimax(position_deepcopy, depth - 1, alpha, beta, opponents_moves != set())
            minEval = min(minEval, eval)

            beta = min(beta, eval)
            if beta <= alpha:
                break

    return minEval

def minimax_move(position: Board) -> tuple[int, int]:

    bestMove = (20, 20)
    bestEval = float('+inf')

    legal_moves = position.all_legal_moves(Board.WHITE)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) # create a deep copy of the board position
            position_deepcopy.set_discs(row, col, Board.WHITE)

            opponents_moves = position_deepcopy.all_legal_moves(Board.BLACK)
            currentEval = minimax(position_deepcopy, 3, float('-inf'), float('inf'), opponents_moves != set())

            if currentEval <= bestEval:
                bestMove = (row, col)
                bestEval = currentEval
    return bestMove

