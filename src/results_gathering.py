from board import Board
from MCTS_AI import Node, monte_carlo_tree_search, mcts_move
from minimax_AI import minimax_move
from greedy_AI import greedy_move
from random_AI import random_move
from value_matrix_AI import value_matrix_move
import csv

# Initialize a list to store the results
results = []

black_wins = 0
white_wins = 0
draws = 0

for _ in range(1000):  # Play until game end
    
    print("Playing game number: ", _+1)
    
    board = Board()  # Initialize a new game board
    player = Board.BLACK  # Black starts 
    
    while not board.is_game_over():
    
        if player == Board.BLACK:  # VM's turn
            row, col = value_matrix_move(board, Board.BLACK)
            if row is not None and col is not None:
                board.make_move(row, col, Board.BLACK)
            #else:
                #print("VM player has no legal moves. Skipping turn.")

        else:  # Random's turn
            row, col = random_move(board, Board.WHITE)
            if row is not None and col is not None:
                board.make_move(row, col, Board.WHITE)
            #else:
                #print("Random player has no legal moves. Skipping turn.")

        player = Board.BLACK if player == Board.WHITE else Board.WHITE  # Switch players
    
   # Record the result
    winner = board.get_winner()
    if winner == 'Black':
        black_wins += 1
    elif winner == 'White':
        white_wins += 1
    else:
        draws += 1

# Write the results to a file
with open('results.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["VM Wins", "Random Wins", "Draws"])
    writer.writerow([black_wins, white_wins, draws])