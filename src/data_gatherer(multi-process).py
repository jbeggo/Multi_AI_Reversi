from multiprocessing import Pool
from utils.board import Board
from AI_Players.MCTS_AI import Node, monte_carlo_tree_search, mcts_move
from AI_Players.minimax_AI import minimax_move, minimax_noprune_move
from AI_Players.greedy_AI import greedy_move
from AI_Players.negamax_AI import negamax_move
from AI_Players.random_AI import random_move
from AI_Players.value_matrix_AI import value_matrix_move
import csv


#from DQN import QLearningPlayer
#agent  = QLearningPlayer(1)
#agent.load_model('models/model_1_20240419-235943.keras')

# Initialise a list to store the results
results = []

# Initialise counters
black_wins = 0
white_wins = 0
draws = 0

TOTAL_GAMES = 100
BATCH_SIZE = 3

def play_game(game_number):
    #try: 
        print(f'Start Game: {game_number+1}')
        
        board = Board()
        
        player = Board.BLACK  # Black starts 
        
        while not board.is_game_over():
        
            if player == Board.BLACK:  # Random AI's turn
                row, col = mcts_move(board, Board.BLACK, 250)
                if row is not None and col is not None:
                    board.make_move(row, col, Board.BLACK)

            else:  # Minimax's turn
                row, col = greedy_move(board, Board.WHITE)
                if row is not None and col is not None:
                    board.make_move(row, col, Board.WHITE)
            
            # Switch players
            player = Board.BLACK if player == Board.WHITE else Board.WHITE  
        
        print(f'Game {game_number+1} finish')
        print(f'Winner: {board.get_winner()}')
        return board.get_winner()
    
    #except Exception as e:
        #print(f'Error in game {game_number}: {e}')
        #return None

if __name__ == "__main__":
    with Pool() as p:
        for i in range(0, TOTAL_GAMES, BATCH_SIZE):
            batch_number = i // BATCH_SIZE + 1
            print(f'///////////Starting batch {batch_number} of {TOTAL_GAMES // BATCH_SIZE}')

            batch_results = []
            jobs = [p.apply_async(play_game, (j,)) for j in range(i, i + BATCH_SIZE)]
            for job in jobs:
                try:
                    result = job.get(timeout=1000)
                    batch_results.append(result)
                except TimeoutError:
                    print(f'Timeout in game {job}')
                    job.terminate()
                    continue

            results.extend(batch_results)

            print(f'///////////Finished batch {batch_number} of {TOTAL_GAMES // BATCH_SIZE}\n')

    black_wins = results.count('Black')
    white_wins = results.count('White')
    draws = results.count('Draw')

    # Write the results to a file...
    with open('results(MCTS[250]-vs-Greedy).csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["MCTS", "Greedy", "Draws"])
        writer.writerow([black_wins, white_wins, draws])