import numpy as np
import copy
from utils.board import Board
import tensorflow as tf
import keras.models as models
from keras.layers import Input, Dense
from keras.optimizers import Adam

class Qagent:
    def __init__(self):
        # Define the model
        self.model = self.build_model()

    def load_model(self, file_path):
        # Load the model correctly using the load_model function
        self.model = models.load_model(file_path)
        print(f"Model loaded from {file_path}")

    def build_model(self):
        model = models.Sequential([
            Input(shape=(64,)),  # Define the input shape explicitly here
            Dense(256, activation='tanh'),
            Dense(64, activation='tanh')
        ])
        model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
        return model
    
    def convert_to_index(self, move):
        # Assuming a move is a tuple (row, col), convert it to an index based on the board size
        row, col = move
        return row * 8 + col  # Adjust this based on board dimensions if necessary
    
    def dqn_move(self, board: Board, player: int):
        
        state = copy.deepcopy(board.board)
        
        legal_moves = board.all_legal_moves(player)

        if not legal_moves: return (None,None) 

        # Reshape the state to be compatible with the model's expected input
        state = np.array(state).reshape(1, -1)
        
        # Predict the Q-values for all possible actions
        q_values = self.model.predict(state,verbose=False).flatten()
        
        legal_indices = [self.convert_to_index(move) for move in legal_moves]
        # Filter out the Q-values for illegal moves by setting them to a very high negative value
        illegal_moves_mask = ~np.isin(np.arange(len(q_values)), legal_indices)
        q_values[illegal_moves_mask] = np.NINF  # Use negative infinity to ensure these are not chosen

        # Find the index of the highest Q-value among legal moves
        best_action_index = np.argmax(q_values[legal_indices])

        # Select the best action using the index of the highest legal Q-value
        best_action = legal_moves[best_action_index]  # Directly use the correct index from legal_moves
        
        return best_action
    
    