from utils.board import Board
from copy import deepcopy

def minimax(position: Board, depth: int, alpha: int, beta: int, isMaximizingPlayer: bool) -> int:
    '''Implements Minimax with alpha-beta pruning to determine next best move'''
    
    # Check for if game over return heuristic value of node
    if depth == 0 or position.is_game_over() is True:
        if isMaximizingPlayer:
            return position.evaluate_board(Board.BLACK)
        else:
            return position.evaluate_board(Board.WHITE)
    
    # maximising player means playing as black
    if isMaximizingPlayer:
        maxEval = float('-inf')
        legal_moves = position.all_legal_moves(Board.BLACK)
        for row, col in legal_moves:
            if position.board[row, col] == Board.EMPTY:

                position_deepcopy = deepcopy(position) 
                position_deepcopy.make_move(row, col, Board.BLACK)

                opponents_moves = position_deepcopy.all_legal_moves(Board.WHITE)
                eval = minimax(position_deepcopy, depth - 1, alpha, beta, opponents_moves == set())
                maxEval = max(maxEval, eval)

                alpha = max(alpha, eval)
                if beta <= alpha:
                    break

        return maxEval

    # else minimizing player's turn (playing as white)
    minEval = float('+inf')
    legal_moves = position.all_legal_moves(Board.WHITE)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) 
            position_deepcopy.make_move(row, col, Board.WHITE)

            opponents_moves = position_deepcopy.all_legal_moves(Board.BLACK)
            eval = minimax(position_deepcopy, depth - 1, alpha, beta, opponents_moves != set())
            minEval = min(minEval, eval)

            beta = min(beta, eval)
            if beta <= alpha:
                break

    return minEval

def minimax_simple(position, depth, isMaximizingPlayer):
    '''Simple Minimax without alpha-beta pruning'''
    
    # Check for if game over return heuristic value of node
    if depth == 0 or position.is_game_over() is True:
        if isMaximizingPlayer:
            return position.evaluate_board(Board.BLACK)
        else:
            return position.evaluate_board(Board.WHITE)

    if isMaximizingPlayer:
        maxEval = float('-inf')
        legal_moves = position.all_legal_moves(Board.BLACK)
        for row, col in legal_moves:
            if position.board[row, col] == Board.EMPTY:
                position_deepcopy = deepcopy(position) 
                position_deepcopy.make_move(row, col, Board.BLACK)

                opponents_moves = position_deepcopy.all_legal_moves(Board.WHITE)
                eval = minimax_simple(position_deepcopy, depth - 1, opponents_moves == set())
                maxEval = max(maxEval, eval)

        return maxEval

    else:  # minimizing player's turn
        minEval = float('+inf')
        legal_moves = position.all_legal_moves(Board.WHITE)
        for row, col in legal_moves:
            if position.board[row, col] == Board.EMPTY:
                position_deepcopy = deepcopy(position) 
                position_deepcopy.make_move(row, col, Board.WHITE)

                opponents_moves = position_deepcopy.all_legal_moves(Board.BLACK)
                eval = minimax_simple(position_deepcopy, depth - 1, opponents_moves == set())
                minEval = min(minEval, eval)

        return minEval

def minimax_move(position: Board, player: int) -> tuple[int, int]:
    '''Uses minimax to return a move coord tuple for player'''
    bestMove = (None,None)
    
    if player == Board.WHITE:
        bestEval = float('+inf')
        opponent = Board.BLACK
    else:
        bestEval = float('-inf')
        opponent = Board.WHITE
    
    legal_moves = position.all_legal_moves(player)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) # create a deep copy of the board position
            position_deepcopy.make_move(row, col, player)

            #opponents_moves = position_deepcopy.all_legal_moves(opponent)
            
            # minimax call
            if player == Board.WHITE:
                currentEval = minimax(position_deepcopy, 2, float('-inf'), float('inf'), True)
            else:  # player == Board.BLACK
                currentEval = minimax(position_deepcopy, 2, float('-inf'), float('inf'), False)

            if player == Board.WHITE and currentEval <= bestEval: # minimised
                bestMove = (row, col)
                bestEval = currentEval # best eval for white
            elif player == Board.BLACK and currentEval >= bestEval: # maximised
                bestMove = (row, col)
                bestEval = currentEval # best eval for black

    return bestMove

def minimax_simple_move(position: Board, player: int) -> tuple[int, int]:
    '''Uses minimax simple to return a move coord tuple for player'''
    bestMove = (None,None)
    
    if player == Board.WHITE:
        bestEval = float('+inf')
    else:
        bestEval = float('-inf')
    
    legal_moves = position.all_legal_moves(player)
    for row, col in legal_moves:
        if position.board[row, col] == Board.EMPTY:

            position_deepcopy = deepcopy(position) # create a deep copy of the board position
            position_deepcopy.make_move(row, col, player)

            #opponents_moves = position_deepcopy.all_legal_moves(opponent)
            
            # minimax call
            if player == Board.WHITE: # minimising
                currentEval = minimax_simple(position_deepcopy, 2, True)
            else:  # minimising
                currentEval = minimax_simple(position_deepcopy, 2, False)

            if player == Board.WHITE and currentEval <= bestEval: # minimised
                bestMove = (row, col)
                bestEval = currentEval # best eval for white
            elif player == Board.BLACK and currentEval >= bestEval: # maximised
                bestMove = (row, col)
                bestEval = currentEval # best eval for black

    return bestMove