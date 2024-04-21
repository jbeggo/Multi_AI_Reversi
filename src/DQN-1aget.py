import numpy as np
import copy
import random
from collections import deque
from utils.board import Board
import tensorflow as tf
from tensorboard.plugins.hparams import api as hp
import keras.models as models
from keras.layers import Input, Dense
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
import datetime

class QLearningPlayer:
    def __init__(self):
        self.learning_rate = 0.01
        self.discount_factor = 1.0
        self.num_games_played = 0

        self.replay_memory = deque(maxlen=1000)  # Replay memory
        self.batch_size = 64  # Batch size for replay

        self.epsilon = 1.0
        self.min_epsilon = 0.01
        self.decay = 0.996

        # Create unique log directories or tags for each player
        log_dir = f"logs/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.summary_writer = tf.summary.create_file_writer(log_dir)
        
        # Define the model
        self.model = models.Sequential([
            Input(shape=(64,)),  # Define the input shape explicitly here
            Dense(44, activation='tanh'),
            Dense(64, activation='tanh')
        ])
        self.model.compile(optimizer=Adam(learning_rate=self.learning_rate), loss='mse')
        
        self.tensorboard = TensorBoard(log_dir=log_dir, histogram_freq=1, write_graph=True)
    
    def update_epsilon(self):
        # Multiply epsilon by decay factor
        self.epsilon *= self.decay
        self.epsilon = max(self.epsilon, self.min_epsilon)  # Ensure epsilon does not go below min_epsilon

    def save_model(self):
        file_path = f'models/model(single)_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.keras'
        self.model.save(file_path)
        print(f"Model saved to {file_path}")

    def load_model(self, file_path):
        # Load the model correctly using the load_model function
        self.model = models.load_model(file_path)
        print(f"Model loaded from {file_path}")
    
    def convert_to_index(self, move):
        # Assuming a move is a tuple (row, col), convert it to an index based on the board size
        row, col = move
        return row * 8 + col  # Adjust this based on board dimensions if necessary
    
    def log_q_values(self, state, step):
        q_values = self.model.predict(state.reshape(1, -1), verbose=0).flatten()
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
        q_values = self.model.predict(state,verbose=0).flatten()
        
        legal_indices = [self.convert_to_index(move) for move in legal_moves]
        # Filter out the Q-values for illegal moves by setting them to a very high negative value
        illegal_moves_mask = ~np.isin(np.arange(len(q_values)), legal_indices)
        q_values[illegal_moves_mask] = np.NINF  # Use negative infinity to ensure these are not chosen

        # Find the index of the highest Q-value among legal moves
        best_action_index = np.argmax(q_values[legal_indices])

        # Select the best action using the index of the highest legal Q-value
        best_action = legal_moves[best_action_index]  # Directly use the correct index from legal_moves
        
        return best_action
    
    def select_action(self, q_values, legal_moves, step):
        
        # skip if no moves
        if not legal_moves:
            print("No legal moves available")
            return None

        # just logging exploration
        with self.summary_writer.as_default():
            tf.summary.scalar('epsilon', self.epsilon, step=step)
            tf.summary.flush()

        # get valid moves from s
        legal_indices = [self.convert_to_index(move) for move in legal_moves]
        #print("Indices of Legal Moves:", indices)

        # either explore 
        if np.random.rand() < self.epsilon:
            chosen_index = np.random.choice(len(legal_moves))
            #print("Chosen Index (Random):", chosen_index)

        # or exploit
        else:
            chosen_index = np.argmax([q_values[index] for index in legal_indices])
            #print("Chosen Index (Greedy):", chosen_index)

        return legal_moves[chosen_index]
    
    def learn_from_replay(self, step):
        # Sample a mini-batch from replay memory
        batch = random.sample(self.replay_memory, self.batch_size)
        #print(batch)
        states = []
        targets = []
        for state, action, reward, next_state, done in batch:
            target = reward
            if not done:
                next_q_values = self.model.predict(next_state.reshape(1, -1), verbose=0).flatten()
                target += self.discount_factor * np.max(next_q_values)

            current_q_values = self.model.predict(state.reshape(1, -1), verbose=0).flatten()
            action_index = self.convert_to_index(action) if isinstance(action, tuple) else action
            current_q_values[action_index] = target
            #print(current_q_values)
            states.append(state.flatten())
            targets.append(current_q_values)

        # Convert lists to numpy arrays
        states = np.array(states)
        targets = np.array(targets)

        # Train the model on the mini-batch
        history = self.model.fit(states, targets, epochs=1, verbose=0,batch_size=self.batch_size, callbacks=[self.tensorboard])

        # Log training loss
        with self.summary_writer.as_default():
            tf.summary.scalar('training_loss', np.average(history.history['loss']), step)
            self.summary_writer.flush()
    
    def learn(self, state, action, reward, next_state, done, step):
        # Store the experience in replay memory
        self.replay_memory.append((state, action, reward, next_state, done))

        # Learn from the replay memory
        if len(self.replay_memory) >= self.batch_size:
            print("Learning from replay")
            self.learn_from_replay(step)

    
    def update_game_count(self):
        self.num_games_played += 1

class Q_env:
    def __init__(self):
        self.board = Board()
        self.player = QLearningPlayer()
        self.turn = Board.BLACK  # Starting player
        self.global_step = 0

    def reset_game(self):
        self.board.reset()
        self.turn = Board.BLACK

    def switch_turn(self):
        self.turn = Board.WHITE if self.turn == Board.BLACK else Board.BLACK

    def play_game(self):
        while not self.board.is_game_over():
            # observe current state s
            state = self.board.board.flatten()

            # select action a, epsilon-greedy
            legal_moves = self.board.all_legal_moves(self.turn)
            if legal_moves:
                # predict from state s
                current_q_values = self.player.model.predict(state.reshape(1, -1), verbose=0).flatten()
                action = self.player.select_action(current_q_values, legal_moves, self.global_step)
                if action:
                    # execute action a
                    self.board.make_move(*action, self.turn)
                    self.board.print_board()
                    next_state = self.board.board.flatten()
                    self.player.learn(state, action, 0, next_state, False, self.global_step)
            
            self.switch_turn()

        # Determine the winner and assign rewards
        winner = self.board.get_winner()
        # can be confusing - based on last move if turn is white, then black won
        reward = 1 if (winner == 'Black' and self.turn == Board.WHITE) \
            or (winner == 'White' and self.turn == Board.BLACK) else -1 if winner else 0

        # Learn from the final state of the game
        self.player.learn(state, action, reward, None, True, self.global_step)  # No next state at the end of the game
        self.player.log_q_values(state, self.global_step)
        self.player.update_epsilon()

    def train(self, episodes):
        for game in range(episodes):
            self.reset_game()

            self.play_game()
        
            self.global_step += 1
            
            self.player.update_game_count()

            if (game+1) % 100 == 0:
                self.player.save_model()
            print(f"Game {game+1} completed")


# Example usage
environment = Q_env()
environment.train(1000)  # Train over x games