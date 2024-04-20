import numpy as np
import copy
from utils.board import Board
import tensorflow as tf
import keras.models as models
from keras.layers import Input, Dense
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
import datetime

class QLearningPlayer:
    def __init__(self, player_id, learning_rate=0.1, discount_factor=1.0):
        self.player_id = player_id
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.num_games_played = 0

        self.epsilon = 1.0
        self.min_epsilon = 0.01
        self.decay = 0.996

        # Adjusted constants for faster temperature decay
        self.temp_constants = {'a': 1.0, 'b': 0.9997, 'c': 0.002}

        # Create unique log directories or tags for each player
        log_dir = f"logs/{player_id}/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.summary_writer = tf.summary.create_file_writer(log_dir)
        
        # Define the model
        self.model = self.build_model()
        self.tensorboard_callback = TensorBoard(log_dir=log_dir, histogram_freq=1, write_graph=True)
    
    def update_epsilon(self):
        # Multiply epsilon by decay factor
        self.epsilon *= self.decay
        self.epsilon = max(self.epsilon, self.min_epsilon)  # Ensure epsilon does not go below min_epsilon

    def save_model(self):
        file_path = f'models/model_{self.player_id}_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.keras'
        self.model.save(file_path)
        print(f"Model saved to {file_path}")

    def load_model(self, file_path):
        # Load the model correctly using the load_model function
        self.model = models.load_model(file_path)
        print(f"Model loaded from {file_path}")

    def build_model(self):
        model = models.Sequential([
            Input(shape=(64,)),  # Define the input shape explicitly here
            Dense(44, activation='tanh'),
            Dense(64, activation='tanh')
        ])
        model.compile(optimizer=Adam(learning_rate=0.01), loss='mse')
        return model
    
    def convert_to_index(self, move):
        # Assuming a move is a tuple (row, col), convert it to an index based on the board size
        row, col = move
        return row * 8 + col  # Adjust this based on board dimensions if necessary
    
    def log_q_values(self, state, step):
        q_values = self.model.predict(state.reshape(1, -1)).flatten()
        avg_q_value = np.mean(q_values)
        with self.summary_writer.as_default():
            tf.summary.scalar('Average_Q_value', avg_q_value, step=step)
        self.summary_writer.flush()
    
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
    
    def select_action(self, state, legal_moves, step):
        if not legal_moves:
            print("No legal moves available")
            return None

        q_values = self.model.predict(state.reshape(1, -1)).flatten()
        #print("Q-values:", q_values)

        with self.summary_writer.as_default():
            tf.summary.scalar('epsilon', self.epsilon, step=step)
            tf.summary.flush()

        legal_indices = [self.convert_to_index(move) for move in legal_moves]
        #print("Indices of Legal Moves:", indices)

        if np.random.rand() < self.epsilon:
            # Exploration: Choose a random action
            chosen_index = np.random.choice(len(legal_moves))
            #print("Chosen Index (Random):", chosen_index)
        else:
            # Exploitation: Choose the best action based on Q-values
            chosen_index = np.argmax([q_values[index] for index in legal_indices])
            #print("Chosen Index (Greedy):", chosen_index)

        return legal_moves[chosen_index]
    
    def learn(self, state, action, reward, next_state, done, step):
        target = reward
        
        #if not done:
            #next_q_values = self.model.predict(next_state.reshape(1, -1)).flatten()
            #target += self.discount_factor * np.max(next_q_values)

        current_q_values = self.model.predict(state.reshape(1, -1)).flatten()
        ##print("Current Q-values:", current_q_values)

        # Convert action to index if it's not already
        action_index = self.convert_to_index(action) if isinstance(action, tuple) else action
        current_q_values[action_index] = target
        #print("Updated Q-values:", current_q_values)

        history = self.model.fit(state.reshape(1, -1), current_q_values.reshape(1, -1), epochs=1, verbose=0,
                                 callbacks=[self.tensorboard_callback])
        #print("Training Loss:", history.history['loss'])

        with self.summary_writer.as_default():
            tf.summary.scalar('training_loss', np.average(history.history['loss']), step=step)
            self.summary_writer.flush()

    
    def update_game_count(self):
        self.num_games_played += 1

class Q_env:
    def __init__(self):
        self.board = Board()
        self.player1 = QLearningPlayer(1)
        self.player2 = QLearningPlayer(2)  # Assuming player2 is another learning agent or a static policy opponent
        self.current_player = self.player1
        self.player_color = Board.BLACK  # Starting player
        self.global_step = 0

    def reset_game(self):
        self.board = Board()
        self.current_player = self.player1
        self.player_color = Board.BLACK

    def switch_player(self):
        self.current_player = self.player2 if self.current_player == self.player1 else self.player1
        self.player_color = Board.WHITE if self.player_color == Board.BLACK else Board.BLACK

    def play_game(self):
        while not self.board.is_game_over():
            state = self.board.board.flatten()
            legal_moves = self.board.all_legal_moves(self.player_color)
            
            if legal_moves:
                action = self.current_player.select_action(state, legal_moves, self.global_step)
                if action:
                    self.board.make_move(*action, self.player_color)
            self.switch_player()

        # Determine the winner and assign rewards
        winner = self.board.get_winner()
        #print(winner)
        reward_player1 = 1 if winner == 'Black' else -1 if winner == 'White' else 0
        reward_player2 = -reward_player1

        # Learn from the final state of the game
        self.player1.learn(state, action, reward_player1, None, True, self.global_step)  # No next state at the end of the game
        self.player1.log_q_values(state, self.global_step)  
        self.player2.learn(state, action, reward_player2, None, True, self.global_step)  # Assume symmetric update for player2
        self.player2.log_q_values(state, self.global_step)

        self.player1.update_epsilon()
        self.player2.update_epsilon()

    def train(self, episodes):
        for game in range(episodes):
            self.reset_game()

            #state = self.board.board.flatten()  # Capture the initial state right after reset
            #self.current_player.log_q_values(state, self.global_step)  # Log Q-values for the initial state

            self.play_game()
            
            # After each game, increment the global step
            self.global_step += 1
            
            self.player1.update_game_count()
            self.player2.update_game_count()

            if (game+1) % 100 == 0:
                self.player1.save_model()
                self.player2.save_model()


# Example usage
#environment = Q_env()
#environment.train(1000)  # Train over x games