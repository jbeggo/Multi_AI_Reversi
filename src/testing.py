from board import Board
from MCTS_AI import Node, monte_carlo_tree_search, mcts_move
from minimax_AI import minimax_move
from greedy_AI import greedy_move
from random_AI import random_move

board = Board()  # Initialize a new game board

player = Board.BLACK  # Black starts 

for _ in range(1000):  # Play until game end
    
    if board.is_game_over():
        break

    if player == Board.BLACK:  # MCTS's turn
        
        row, col = mcts_move(board, Board.BLACK)
        if row is not None and col is not None:
            board.make_move(row, col, Board.BLACK)
        else:
            print("MCTS player has no legal moves. Skipping turn.")

    else:  # Minimax's turn
        row, col = minimax_move(board, Board.WHITE)
        if row is not None and col is not None:
            board.make_move(row, col, Board.WHITE)
        else:
            print("Minimax player has no legal moves. Skipping turn.")

    player = Board.BLACK if player == Board.WHITE else Board.WHITE  # Switch players
    board.print_board()  # Print the board after every turn

# Print the final scores
board.print_score()