import numpy as np
import copy
import random
from collections import deque
from utils.board import Board
import tensorflow as tf
import keras.models as models
from keras.layers import Input, Dense
from keras.optimizers import Adam
from keras.callbacks import TensorBoard
import datetime
from agents.random import random_move
from keras.initializers import RandomUniform

# Define the weight initializer
initializer = RandomUniform(minval=-0.5, maxval=0.5)

NN = models.Sequential([
        Dense(64, activation='linear', input_shape=(64,), kernel_initializer=initializer),
        Dense(60, activation='sigmoid', kernel_initializer=initializer),
        Dense(64, activation='sigmoid', kernel_initializer=initializer)
    ])
NN.compile(optimizer=Adam(learning_rate=0.001), loss='mse')

# Target network, cloned from the online network
TARGET_NN = models.clone_model(NN)
TARGET_NN.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
TARGET_NN.set_weights(NN.get_weights())  # Initialize target network weights

class QLearningPlayer:
    def __init__(self, player_id = 'black'):
        self.player_id = player_id
        self.discount_factor = 1.0
        self.num_games_played = 0
        self.num_wins = 0

        self.replay_memory = deque(maxlen=1000)  # Replay memory
        self.batch_size = 64  # Batch size for replay

        self.epsilon = 1.0
        self.min_epsilon = 0.01
        self.decay = 0.996

        # set neural network
        self.nn = NN

        # Create unique log directories or tags for each player
        log_dir = f"logs/{player_id}/{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
        self.summary_writer = tf.summary.create_file_writer(log_dir)
        self.tensorboard = TensorBoard(log_dir=log_dir, histogram_freq=1, write_graph=True)
    
    
    
    def decay_epsilon(self):
        # Multiply epsilon by decay factor
        self.epsilon *= self.decay
        self.epsilon = max(self.epsilon, self.min_epsilon)  # Ensure epsilon does not go below min_epsilon

    def save_model(self):
        file_path = f'models/model_{self.player_id}_{datetime.datetime.now().strftime("%Y%m%d-%H%M%S")}.keras'
        self.nn.save(file_path)
        print(f"Model saved to {file_path}")

    def load_model(self, file_path):
        # Load the model correctly using the load_model function
        self.nn = models.load_model(file_path)
        print(f"Model loaded from {file_path}")
    
    def convert_to_index(self, move):
        # Assuming a move is a tuple (row, col), convert it to an index based on the board size
        row, col = move
        return row * 8 + col  # Adjust this based on board dimensions if necessary
    
    def log_q_values(self, state, step):
        q_values = self.nn.predict(state.reshape(1, -1), verbose=0).flatten()
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
        q_values = self.nn.predict(state,verbose=0).flatten()
        
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

        # get valid moves from s
        legal_indices = [self.convert_to_index(move) for move in legal_moves]
        #print(f"Q-values shape: {q_values.shape}, Legal Indices: {legal_indices}")  # Debugging output

        # either explore 
        if np.random.rand() < self.epsilon:
            chosen_move = random.choice(legal_moves)
            print("Explore", "Chosen Move:", chosen_move)

        # or exploit
        else:
            legal_q_values = [q_values[index] for index in legal_indices]
            max_index = np.argmax(legal_q_values)  # index of maximum Q-value in legal_q_values
            chosen_move = legal_moves[max_index]  # pick the corresponding move from legal_moves
            print("Exploit", "Chosen Move:", chosen_move, "with Q-value", q_values[legal_indices[max_index]])

        # just logging exploration
        with self.summary_writer.as_default():
            tf.summary.scalar('epsilon', self.epsilon, step=step)
            tf.summary.flush()

        return chosen_move
    
    def learn_from_replay(self, step):
        if len(self.replay_memory) >= self.batch_size:
            # Sample a mini-batch from replay memory
            batch = random.sample(self.replay_memory, self.batch_size)
            #print(batch)
            states = []
            targets = []
            for state, action, reward, next_state, done in batch:
                target = reward
                if not done:
                    next_q_values = self.nn.predict(next_state, verbose=0).flatten()
                    target += self.discount_factor * np.max(next_q_values)

                current_q_values = self.nn.predict(state, verbose=0).flatten()
                action_index = self.convert_to_index(action) if isinstance(action, tuple) else action
                current_q_values[action_index] = target
                #print(current_q_values)
                states.append(state.squeeze())
                targets.append(current_q_values)

            # Convert lists to numpy arrays for training
            states = np.array(states)
            targets = np.array(targets)

            print(states)
            print(targets)

            # Train the model on the mini-batch
            history = self.nn.fit(states, targets, epochs=1, verbose=1, batch_size=self.batch_size, callbacks=[self.tensorboard])

            # Log training loss
            with self.summary_writer.as_default():
                tf.summary.scalar('training_loss', np.average(history.history['loss']), step)
                self.summary_writer.flush()
    
    def remember(self, state, action, reward, next_state, done):
        # Store the experience in replay memory
        self.replay_memory.append((state, action, reward, next_state, done))


    def increment_game_count(self):
        self.num_games_played += 1

class Q_env:
    def __init__(self):
        self.board = Board()
        self.player = QLearningPlayer('black')
        self.turn = Board.BLACK  # Starting player
        self.global_step = 0
        self.best_winrate = 0

    def reshape_state(self, state):
        return (state.reshape(1, -1))

    def reset_game(self):
        self.board.reset()
        self.turn = Board.BLACK

    def switch_player(self):
        self.turn = Board.WHITE if self.turn == Board.BLACK else Board.BLACK

    def play_game(self):
        while not self.board.is_game_over():
            # observe current state s
            state = self.board.board
            state = self.reshape_state(state)
            # predict from state s
            current_q_values = self.player.nn.predict(state, verbose=0).flatten()

            # select action a, epsilon-greedy
            legal_moves = self.board.all_legal_moves(self.turn)
            if legal_moves:
                action = self.player.select_action(current_q_values, legal_moves, self.global_step)
                if action:
                    # execute action a
                    self.board.make_move(*action, self.turn)
                    #self.board.print_board()
                else:
                    print("Skip player")
            # switch to env
            self.switch_player()
            # env reacts
            legal_moves = self.board.all_legal_moves(self.turn)
            if legal_moves:
                oppaction = random.choice(legal_moves)
                if oppaction:
                    # execute action a
                    self.board.make_move(*oppaction, self.turn)
                    #self.board.print_board()
                else:
                    print("Skip env")

            # control back to player
            self.switch_player()
                
            next_state = self.board.board
            next_state = self.reshape_state(next_state)
            if self.board.is_game_over():
                print("game over")
                winner = self.board.get_winner()
                self.player.increment_game_count()
                reward = 1 if winner == 'Black' else -1 if winner == 'White' else 0
                self.player.remember(state, action, reward, next_state, True)
                print("Remember experience - Action: ", action, "Reward: ", reward, "Done?: ", True)
            else:
                self.player.remember(state, action, 0, next_state, False)
                print("Remember experience - Action: ", action, "Reward: ", 0, "Done?: ", False)

        # Determine the game outcome and update counts
        winner = self.board.get_winner()
        if winner == 'Black':
            self.player.num_wins += 1

        # Log the game outcome to TensorBoard
        with self.player.summary_writer.as_default():
            tf.summary.scalar('Win Rate', self.player.num_wins / self.player.num_games_played, step=self.global_step)

        self.player.log_q_values(state, self.global_step)

        self.player.decay_epsilon()

    def train(self, episodes):
        for game in range(episodes):
            self.reset_game()

            self.play_game()
            
            # After each game, increment the global step
            self.global_step += 1
            
            self.player.increment_game_count()

            if (game+1) % 100 == 0:
                self.player.save_model()
            # Learn after 10 games
            if (game+1) % 10 == 0:
                self.player.learn_from_replay(self.global_step)

                


# Example usage
environment = Q_env()
environment.train(1000)  # Train over x games