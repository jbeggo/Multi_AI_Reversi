import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import matplotlib.pyplot as plt
import random
from utils.board import Board
from AI_Players.random_AI import random_move

# Define the neural network architecture
class ReversiNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(ReversiNN, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# Function to convert board state to input vector
def board_state_to_input(board: Board):
    input_vector = np.array(board.board).flatten()
    input_vector = np.where(input_vector == 1, 1, 0)  # Convert black pieces to 1, white pieces to 0
    input_vector = np.where(input_vector == -1, 1, 0)  # Convert white pieces to 1, black pieces to 0
    return input_vector

# Function to train the neural network
def train_nn(num_episodes, learning_rate, discount_factor, epsilon, print_interval=10):
    
    input_size = 64  # Size of input vector (8x8 board)
    hidden_size = 128  # Number of neurons in the hidden layer
    output_size = 64  # Size of output vector (8x8 board)

    # Initialize the neural network
    model = ReversiNN(input_size, hidden_size, output_size)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)

    loss_history = []

    for episode in range(num_episodes):
        board = Board()  # Initialize new board for each episode
        player = 1  # Start with black player

        while not board.is_game_over():
            # Convert board state to input vector
            input_vector = board_state_to_input(board)
            input_tensor = torch.tensor(input_vector, dtype=torch.float32)

            # Predict the value for each possible move
            output = model(input_tensor)
            legal_moves = board.all_legal_moves(player)
            valid_outputs = [output[move[0]*8 + move[1]].item() for move in legal_moves]

            # Select the move with the highest predicted value if legal moves are available
            if legal_moves:
                if random.random() < epsilon:
                    # Choose a random move if the random number is less than epsilon
                    best_move = random.choice(legal_moves)
                else:
                    # Choose the move with the highest predicted value
                    best_move_index = np.argmax(valid_outputs)
                    best_move = legal_moves[best_move_index]
            else:
                # If there are no legal moves available, skip the move
                #print("No legal moves available. Skipping turn.")
                player *= -1  # Switch to the next player and continue to the next iteration
                continue

            # Apply the move to the board
            board.make_move(best_move[0], best_move[1], player)

            # Calculate reward (for simplicity, assume 1 for winning, -1 for losing, 0 for draw)
            reward = 1 if board.get_winner() == 'Black' else -1 if board.get_winner() == 'White' else 0

            # Convert the next board state to input vector
            next_input_vector = board_state_to_input(board)
            next_input_tensor = torch.tensor(next_input_vector, dtype=torch.float32)

            # Predict the value of the next state
            next_output = model(next_input_tensor)
            next_max_value = torch.max(next_output).item()

            # Calculate target value using Bellman equation
            target_value = reward + discount_factor * next_max_value

            # Backpropagation and optimization step
            target_tensor = torch.tensor([target_value], dtype=torch.float32)
            target_tensor = target_tensor.view(-1)  # Reshape the target tensor to have the same size as the input tensor
            loss = criterion(output[best_move[0]*8 + best_move[1]], target_tensor)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            # Append loss to history
            loss_history.append(loss.item())

            # Switch players
            player *= -1
        
        # Print loss value at regular intervals
        if (episode + 1) % print_interval == 0:
            print(f'Episode [{episode + 1}/{num_episodes}], Loss: {loss.item()}')

        # Save the model
        torch.save(model.state_dict(), 'model-reversi.pth')
    
    # Plot loss curve
    plt.plot(loss_history)
    plt.xlabel('Episode')
    plt.ylabel('Loss')
    plt.title('Training Loss Curve')
    plt.show()

    # Load the model state dictionary before returning
    model.load_state_dict(torch.load('model-reversi.pth'))
    return model, loss_history

# Training parameters
num_episodes = 1000
learning_rate = 0.001
discount_factor = 0.99  # Discount factor for future rewards

# Train the neural network
train_nn(num_episodes, learning_rate, discount_factor)