from multiprocessing import Pool
from utils.board import Board
from agents.MCTS_AI import Node, monte_carlo_tree_search, mcts_move
from agents.minimax_AI import minimax_move
from agents.greedy_AI import greedy_move, greedy_move_nondet
from agents.negamax_AI import negamax_move
from agents.random_AI import random_move
from agents.value_matrix_AI import evolutionary_matrix_move, wipeout_matrix_move
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
BATCH_SIZE = 4

def play_game(game_number):
    #try: 
        print(f'Start Game: {game_number+1}')
        
        board = Board()
        
        player = Board.BLACK  # Black starts 
        
        while not board.is_game_over():
        
            if player == Board.BLACK:  # Agent 1
                row, col = mcts_move(board, Board.BLACK, 100)
                
                if row is not None and col is not None:
                    board.make_move(row, col, Board.BLACK)

            else:  # Agent 2
                
                row, col = greedy_move(board, Board.WHITE)
                if row is not None and col is not None:
                    board.make_move(row, col, Board.WHITE)
            
            # Switch players
            player = Board.BLACK if player == Board.WHITE else Board.WHITE  
        
        winner = board.get_winner()
        print(f'Game {game_number+1} finish')
        print(f'///////////////////////////////////////Winner: {winner}')
        return winner
    
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
            with open('results/MCTS [50] vs Greedy[nondet] (100).csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["MCTS [50]", "Greedy", "Draws"])
                writer.writerow([black_wins, white_wins, draws])