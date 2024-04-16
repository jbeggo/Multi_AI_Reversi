from multiprocessing import Pool
from utils.board import Board
from AI_Players.MCTS_AI import Node, monte_carlo_tree_search, mcts_move
from AI_Players.minimax_AI import minimax_move
from AI_Players.greedy_AI import greedy_move
from AI_Players.negamax_AI import negamax_move
from AI_Players.random_AI import random_move
from AI_Players.value_matrix_AI import value_matrix_move
import csv

# Initialise a list to store the results
results = []

# Initialise counters
black_wins = 0
white_wins = 0
draws = 0

TOTAL_GAMES = 1000
BATCH_SIZE = 16

def play_game(game_number):
    
    print(f'Starting game {game_number}')
    
    board = Board()
    
    player = Board.BLACK  # Black starts 
    
    while not board.is_game_over():
    
        if player == Board.BLACK:  # Negamax's turn
            row, col = negamax_move(board, Board.BLACK)
            if row is not None and col is not None:
                board.make_move(row, col, Board.BLACK)

        else:  # Random's turn
            row, col = random_move(board, Board.WHITE)
            if row is not None and col is not None:
                board.make_move(row, col, Board.WHITE)
        
        # Switch players
        player = Board.BLACK if player == Board.WHITE else Board.WHITE  
    
    print(f'Game {game_number} finished')
    return board.get_winner()

if __name__ == "__main__":
    with Pool() as p:
        results = p.map(play_game, range(16))

    black_wins = results.count('Black')
    white_wins = results.count('White')
    draws = results.count('Draw')

    # Write the results to a file...
    with open('results(Negamax-vs-Random).csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Negamax Wins", "Random Wins", "Draws"])
        writer.writerow([black_wins, white_wins, draws])