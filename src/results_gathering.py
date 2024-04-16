from utils.board import Board
from AI_Players.MCTS_AI import Node, monte_carlo_tree_search, mcts_move
from AI_Players.minimax_AI import minimax_move
from AI_Players.greedy_AI import greedy_move
from AI_Players.negamax_AI import negamax_move
from AI_Players.random_AI import random_move
from AI_Players.value_matrix_AI import value_matrix_move
import csv

# Initialize a list to store the results
results = []

black_wins = 0
white_wins = 0
draws = 0

for _ in range(100):  # Play until game end
    
    print("Playing game number: ", _+1)

    board = Board()  # Initialize a new game board
    player = Board.BLACK  # Black starts 
    
    while not board.is_game_over():
    
        if player == Board.BLACK:  # Negamax's turn
            row, col = negamax_move(board, Board.BLACK)
            if row is not None and col is not None:
                board.make_move(row, col, Board.BLACK)
            #else:
                #print("Negamax player has no legal moves. Skipping turn.")

        else:  # Random's turn
            row, col = random_move(board, Board.WHITE)
            if row is not None and col is not None:
                board.make_move(row, col, Board.WHITE)
            #else:
                #print("Random player has no legal moves. Skipping turn.")

        #board.print_board()
        #print(board.all_legal_moves(Board.BLACK))
        #print(board.all_legal_moves(Board.WHITE))
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
with open('results(Negamax-vs-Random).csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Negamax Wins", "Random Wins", "Draws"])
    writer.writerow([black_wins, white_wins, draws])