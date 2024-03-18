from board import Board
from MCTS_AI import Node, monte_carlo_tree_search
from minimax_AI import minimax_move
from greedy_AI import greedy_move
from random_AI import random_move

board = Board()  # Initialize a new game board

player = Board.BLACK  # Black starts 

for _ in range(1000):  # Play x turns
    
    if board.is_game_over():
        break

    if player == Board.BLACK:  # AI's turn
        
        # MCTS testing
        '''root = Node(board, Board.BLACK)
        best_next_move = monte_carlo_tree_search(root, num_iterations=500)
        board = best_next_move.board'''
        
        row, col = random_move(board, Board.BLACK)
        if row is not None and col is not None:
            board.make_move(row, col, Board.BLACK)
        else:
            print("Random player has no legal moves. Skipping turn.")

    else:  # other player's turn
        row, col = minimax_move(board)
        if row is not None and col is not None:
            board.make_move(row, col, Board.WHITE)
        else:
            print("Minimax player has no legal moves. Skipping turn.")

    player = Board.BLACK if player == Board.WHITE else Board.WHITE  # Switch players
    board.print_board()  # Print the board

# Print the final scores
board.print_score()