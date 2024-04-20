from utils.board import Board
import numpy as np
from AI_Players.random_AI import random_move

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

# Initialize value matrix
random_matrix = np.round(np.random.rand(8, 8) * 5, 1)
# Set the center 4 cells to 0
random_matrix[3:5, 3:5] = 0

# Define exploration strategy (e.g., epsilon-greedy)
epsilon = 0.01  # Exploration rate

# Training loop
num_episodes = 1000
learning_rate = 0.1  # Learning rate

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

def reward(board: Board, player: int):
    # Count the number of black and white pieces
    black_count = np.sum(board.board == 1)
    white_count = np.sum(board.board == -1)
    
    # Calculate the difference
    if player == 1:
        difference = black_count - white_count
    else:
        difference = white_count - black_count
    
    # Normalize the difference
    normalized_difference = difference / 64.0  # Assuming an 8x8 board
    
    # Assign rewards based on the difference
    if normalized_difference > 0:
        reward = 1  # Positive reward for increasing advantage
    elif normalized_difference < 0:
        reward = -1  # Negative reward for decreasing advantage
    else:
        reward = 0  # No reward for maintaining advantage
    
    return reward

def train(matrix, num_episodes, learning_rate, epsilon):
    '''Train the value matrix in the epsilon greedy style'''
    
    for episode in range(num_episodes):
        
        print("/////////////////////// Starting Episode:", episode)
        
        board = Board()  # Initialize new board for each episode
        player = 1  # Start with black player

        # Game loop
        while not board.is_game_over():
            
            # Check if the current player can make a move
            legal_moves = board.all_legal_moves(player)
            if not legal_moves:  # No legal moves available for the current player
                print("Player", player, "cannot make a move. Skipping turn.")
                # Switch to the next player and continue to the next iteration
                player *= -1
                continue
            
            # Select action using exploration strategy
            if np.random.rand() < epsilon:
                action = random_move(board, player)  # Random move
                print("Exploring")
            else:
                action = value_matrix_move(board, player, matrix)  # Greedy move based on value matrix
                print("Not exploring")
            
            # Apply action to the board
            board.make_move(action[0],action[1], player)
            
            # Calculate reward
            reward_value = reward(board, player) 
            
            # Update value matrix
            next_state_value = np.min(matrix)
            for move in board.all_legal_moves(player):
                row, col = move
                next_state_value = max(next_state_value, matrix[row, col])
            
            current_state_value = matrix[action[0], action[1]]
            td_target = reward_value + next_state_value
            td_error = td_target - current_state_value
            matrix[action[0], action[1]] += learning_rate * td_error

            # switch players
            player *= -1
        
        print("/////////////////////// Finishing Episode:", episode)
        
    return matrix


#print(value_matrix)
new_matrix = train(value_matrix_frylizheng, num_episodes, learning_rate, epsilon)
final_matrix = np.round(new_matrix,1)
print(final_matrix)