from utils.board import Board
import numpy as np
from agents.random_AI import random_move

# example matrix derived from FryLiZheng "Using Reinforcement Learning to Play Othello"
value_matrix_frylizheng = np.array([
    [3.2125, 1.775,  1.875,  1.975,  1.975,  1.875,  1.775,  3.2125],
    [0.15,   2.3,    0.6625, 1.8375, 1.8375, 0.6625, 2.3,    0.15],
    [3.525,  0.85,   2.675,  0.175,  0.175,  2.675,  0.85,   3.525],
    [1.125,  1.95,   0.15,   0,      0,      0.15,   1.95,   1.125],
    [1.125,  1.95,   0.15,   0,      0,      0.15,   1.95,   1.125],
    [3.525,  0.85,   2.675,  0.175,  0.175,  2.675,  0.85,   3.525],
    [0.15,   2.3,    0.6625, 1.8375, 1.8375, 0.6625, 2.3,    0.15],
    [3.2125, 1.775,  1.875,  1.975,  1.975,  1.875,  1.775,  3.2125]
])

new = np.array([
    [3.2125, 1.7928, 1.875,  1.9948, 1.975,  1.8938, 1.7572, 3.2125],
    [0.15,   2.3228, 0.6625, 1.8375, 1.8375, 0.6624, 2.3,    0.1515],
    [3.525,  0.85,   2.7017, 0.1768, 0.175,  2.675,  0.85,   3.525 ],
    [1.125,  1.9498, 0.15,   0.,     0.,     0.15,   1.9305, 1.125 ],
    [1.125,  1.9695, 0.1515, 0.,     0.,     0.1485, 1.9305, 1.125 ],
    [3.4898, 0.85,   2.675,  0.1732, 0.175,  2.6482, 0.8331, 3.5602],
    [0.15,   2.277,  0.6625, 1.8559, 1.8559, 0.6559, 2.3,    0.1515],
    [3.2125, 1.7571, 1.9127, 2.0147, 1.975,  1.8938, 1.775,  3.2125]
])

# Initialize value matrix
random_matrix = np.round(np.random.rand(8, 8) * 5, 4)
# Set the center 4 cells to 0
random_matrix[3:5, 3:5] = 0

# Define exploration strategy (e.g., epsilon-greedy)
epsilon = 0.01  # Exploration rate

# Training loop
num_episodes = 1000
learning_rate = 0.1  # Learning rate

def evolve_matrix(matrix: np.array) -> np.array:
    
    # Copy the matrix to avoid modifying the original
    matrix = matrix.copy()

    # Select two random values
    chosen_values = np.random.choice(matrix.size, 2, replace=False)
    chosen_values = np.unravel_index(chosen_values, matrix.shape)

    # Adjust the selected values by a small factor (1%)
    for index in zip(*chosen_values):
        matrix[index] *= np.random.choice([0.99, 1.01])

    return matrix

def value_matrix_move(board, player, given_matrix) -> tuple[int, int]:
    '''Calculate a best move for player from matrix, return (None,None) to skip'''
    
    # Generate all possible moves
    moves = board.all_legal_moves(player)
    # Initialize the best score and move
    best_score = -np.inf
    best_move = (None, None)
    
    # If the player has no legal moves -> skip
    if not moves:  
        return best_move
    
    for move in moves:
        # apply move to board copy
        row, col = move
        score = given_matrix[row, col]
        #print("Move:", move, "Score:", score)
        
        # update for best move found on matrix
        if score > best_score:
            best_score = score
            best_move = move
    
    return best_move

def evolutionary_train(starting_matrix: np.array, episodes: int) -> np.array:
    '''Train the value matrix in the epsilon greedy style'''
    
    # Copy the matrix to avoid modifying the original
    starting_matrix = starting_matrix.copy()
    #print(starting_matrix)

    for _ in range(episodes):
        
        # Evolve the matrix
        evolved_matrix = evolve_matrix(starting_matrix)
        #print(evolved_matrix)
        
        print("Episode:", _+1)
        # Initialize the game
        board = Board()
        player = 1

        while not board.is_game_over():
            # Select the matrix to use for the current player
            current_matrix = starting_matrix if player == 1 else evolved_matrix

            # Select action using the current matrix
            action = value_matrix_move(board, player, current_matrix)

            # Check if the current player can make a move
            legal_moves = board.all_legal_moves(player)
            if not legal_moves:  # No legal moves available for the current player
                #print("Player", player, "cannot make a move. Skipping turn.")
                # Switch to the next player and continue to the next iteration
                player *= -1
                continue

            # Apply action to the board
            board.make_move(action[0], action[1], player)
            # Switch to the next player
            player *= -1

        # Update the win count for the winning matrix
        winner = 'original' if board.get_winner() == 'Black' else 'evolved'

        # Overwrite the original matrix if the evolved matrix won the game
        if winner == 'evolved':
            print("Evolving")
            starting_matrix = evolved_matrix

    return np.round(starting_matrix,4)

new = evolutionary_train(value_matrix_frylizheng, 100)
print(value_matrix_frylizheng)
print ("\n")
print(new)

board = Board()
player = 1

while not board.is_game_over():

    if player == 1:
        action = value_matrix_move(board, player, value_matrix_frylizheng)
    else:
        action = value_matrix_move(board, player, new)

    # Check if the current player can make a move
    legal_moves = board.all_legal_moves(player)
    if not legal_moves:  # No legal moves available for the current player
        #print("Player", player, "cannot make a move. Skipping turn.")
        # Switch to the next player and continue to the next iteration
        player *= -1
        continue

    # Apply action to the board
    board.make_move(action[0], action[1], player)
    # Switch to the next player
    player *= -1

print(board.get_winner())