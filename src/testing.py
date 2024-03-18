from board import Board
from MCTS_AI import Node, monte_carlo_tree_search
from random_AI import random_move
import random

board = Board()  # Initialize a new game board
player = Board.BLACK  # The AI will play as black

for _ in range(3):  # Play 100 turns
    if board.is_game_over():
        break

    if player == Board.BLACK:  # AI's turn
        root = Node(board, Board.BLACK)
        best_next_move = monte_carlo_tree_search(root, num_iterations=500)
        board = best_next_move.board
    else:  # Random player's turn
        row, col = random_move(board, Board.WHITE)
        board.make_move(row, col, Board.WHITE)

    player = Board.BLACK if player == Board.WHITE else Board.WHITE  # Switch players
    board.print_board()  # Print the board

# Print the final scores
board.print_score()