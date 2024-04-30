from utils.board import Board
from copy import deepcopy

def minimax(board_state: Board, depth: int, alpha: int, beta: int, maximising: bool) -> int:
    '''Implements Minimax with alpha-beta pruning to determine next move up to set depth'''
    
    # Check for if game over return heuristic value of node
    if depth == 0 or board_state.is_game_over() is True:
        if maximising:
            return board_state.evaluate_board(Board.BLACK)
        else:
            return board_state.evaluate_board(Board.WHITE)
    
    # maximising player means playing as black in this case
    if maximising:
        maxEval = float('-inf')
        legal_moves = board_state.all_legal_moves(Board.BLACK)
        for row, col in legal_moves:
            if board_state.board[row, col] == Board.EMPTY:

                state_copy = deepcopy(board_state) 
                state_copy.make_move(row, col, Board.BLACK)

                opponents_moves = state_copy.all_legal_moves(Board.WHITE)
                # recursive call with depth -1 until starting state reached
                eval = minimax(state_copy, depth - 1, alpha, beta, not opponents_moves)

                # update best evaluation
                if eval >= maxEval:
                    maxEval = eval

                #update alpha
                if eval >= alpha:
                    alpha = eval
 
                if beta <= alpha:
                    break
        #print("Maximised: ", maxEval)              
        return maxEval

    # else minimizing player's turn (playing as white)
    minEval = float('+inf')
    legal_moves = board_state.all_legal_moves(Board.WHITE)
    for row, col in legal_moves:
        if board_state.board[row, col] == Board.EMPTY:

            state_copy = deepcopy(board_state) 
            state_copy.make_move(row, col, Board.WHITE)

            opponents_moves = state_copy.all_legal_moves(Board.BLACK)
            eval = minimax(state_copy, depth - 1, alpha, beta, opponents_moves)

            # update minimum evaluation
            if eval <= minEval:
                minEval = eval

            # update beta
            if eval <= beta:
                beta = eval

            if beta <= alpha:
                break
    #print("Minimised: ", minEval)
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

def minimax_move(board_state: Board, player: int, depth: int) -> tuple[int, int]:
    '''Uses minimax to return a move coord tuple for player'''
    #print("Playing as: ", player)
    bestMove = (None,None)
    
    if player == Board.WHITE:
        bestEval = float('+inf')
    else:
        bestEval = float('-inf')
    
    legal_moves = board_state.all_legal_moves(player)
    for row, col in legal_moves:
        pos = board_state.board[row, col]
        if pos == Board.EMPTY:

            state_copy = deepcopy(board_state) # create a deep copy of the board position
            state_copy.make_move(row, col, player)

            #opponents_moves = position_deepcopy.all_legal_moves(opponent)
            
            # minimax call
            if player == Board.WHITE:
                currentEval = minimax(state_copy, depth, float('-inf'), float('inf'), True)
            else:  # player == Board.BLACK
                currentEval = minimax(state_copy, depth, float('-inf'), float('inf'), False)

            if player == Board.WHITE and currentEval <= bestEval: # minimised
                bestMove = (row, col)
                bestEval = currentEval # best eval for white
            elif player == Board.BLACK and currentEval >= bestEval: # maximised
                bestMove = (row, col)
                bestEval = currentEval # best eval for black

            #print("Best eval: ", bestEval)

    return bestMove

def minimax_noprune_move(position: Board, player: int, depth: int) -> tuple[int, int]:
    '''Uses minimax without pruning to return a move coord tuple for player'''
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
                currentEval = minimax_simple(position_deepcopy, depth, True)
            else:  # minimising
                currentEval = minimax_simple(position_deepcopy, depth, False)

            if player == Board.WHITE and currentEval <= bestEval: # minimised
                bestMove = (row, col)
                bestEval = currentEval # best eval for white
            elif player == Board.BLACK and currentEval >= bestEval: # maximised
                bestMove = (row, col)
                bestEval = currentEval # best eval for black

    return bestMove