from utils.board import Board
from agents.mcts import Node, monte_carlo_tree_search, mcts_move
from agents.minimax import minimax_move, minimax_noprune_move
from agents.greedy import greedy_move, greedy_move_nondet
from agents.negamax import negamax_move
from agents.random import random_move
from agents.value_matrix import evolutionary_matrix_move, wipeout_matrix_move
#from DQN import QLearningPlayer
import csv


#agent  = QLearningPlayer(1)
#agent.load_model('models/model_black_20240423-040934.keras')

# Initialize a list to store the results
results = []

black_wins = 0
white_wins = 0
draws = 0

for _ in range(1):  # Play until game end
    
    #print("Playing game number: ", _+1)

    board = Board()  # Initialize a new game board
    player = Board.BLACK  # Black starts 
    
    while not board.is_game_over():

        if player == Board.BLACK:  # Data Gatherer turn
            #row, col = qagent.choose_action(board.board, board.all_legal_moves(Board.BLACK))
            #row, col = agent.dqn_move(board, Board.BLACK)
            row, col = mcts_move(board, Board.BLACK, 500)
            
            if row is not None and col is not None:
                board.make_move(row, col, Board.BLACK)
                print("MCTS Move: ", (row,col))
                board.print_board()
            else:
                print("MCTS player has no legal moves. Skipping turn.")

        else:  # Agent 2
            row, col = random_move(board, Board.WHITE)
            if row is not None and col is not None:
                board.make_move(row, col, Board.WHITE)
                print("Random Move: ", (row,col))
                board.print_board()
            else:
                print("Random player has no legal moves. Skipping turn.")

        player = Board.BLACK if player == Board.WHITE else Board.WHITE  # Switch players
    
    # Record the result
    winner = board.get_winner()
    print("Winner: ", winner)
    if winner == 'Black':
        black_wins += 1
    elif winner == 'White':
        white_wins += 1
    else:
        draws += 1

    #print ("Minimax Wins: ", white_wins)
    # Write the results to a file
    with open('results/MCTS [100] vs Random (100).csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["MCTS Wins", "Random Wins", "Draws"])
        writer.writerow([black_wins, white_wins, draws])