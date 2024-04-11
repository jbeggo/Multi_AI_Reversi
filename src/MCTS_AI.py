from board import Board
import numpy as np
import random
import copy

class Node:
    def __init__(self, board, player,last_move=None, parent=None):
        # board is more generic state in other MCTS implementations
        self.board = copy.deepcopy(board)
        self.player = player
        self.last_move = last_move
        self.parent = parent
        self.children = []
        self.visit_count = 0
        self.total_score = 0.0

def select(node):
    ''' Traverse tree of next board-states, selects node with best UCB score '''
    while node.children:
        # return node with highest UCB score
        node = max(node.children, key=ucb_score)
    return node

def ucb_score(node):
    ''' (Upper-Confidence Bound) metric for selecting next node '''
    if node.visit_count == 0:
        return float('inf')
    
    # ------- UCB
    # average score of current node from visitation estimate
    avg_score = node.total_score / node.visit_count
    
    # exploration score from balancing infrequently visited nodes & frequent
    exploration_score = np.sqrt(2 * np.log(node.parent.visit_count) / node.visit_count)
    
    # combine
    return avg_score + exploration_score

def expand(node):
    ''' Return next board-state nodes for given node '''
    possible_moves = node.board.all_legal_moves(node.player)
    for row, col in possible_moves:
        new_board = copy.deepcopy(node.board)  
        new_board.make_move(row, col, node.player)
        new_node = Node(new_board, (-1 * node.player),last_move=(row,col), parent=node)
        node.children.append(new_node)

def backpropagate(node, score):
    ''' Traverse back through the tree from outcome, updating score as we go '''
    while node:
        node.visit_count += 1
        node.total_score += score
        node = node.parent

def simulate(node):
    ''' Simulate a random play and return the result '''
    board = copy.deepcopy(node.board)
    player = node.player
    while not board.is_game_over():
        legal_moves = board.all_legal_moves(player)
        if not legal_moves:  # If the player has no legal moves, switch to the other player
            player = Board.BLACK if player == Board.WHITE else Board.WHITE
            continue
        row , col = random.choice(legal_moves)
        board.make_move(row, col, player)
        player = Board.BLACK if player == Board.WHITE else Board.WHITE  # Switch players after making a move
    return board.evaluate_board(player)  # or Board.WHITE, depending on how you define the score

def monte_carlo_tree_search(root, num_iterations):
    ''' Main MCTS steps to return best next move '''
    for _ in range(num_iterations):
        node = select(root)
        expand(node)
        score = simulate(node)
        backpropagate(node, score)
    if root.children: #is not empty
        return max(root.children, key=lambda n: n.visit_count)
    else:
        return [None, None]

def mcts_move(board: Board, player_color: int) -> tuple[int, int]:
    ''' Return best move for given player using MCTS '''
    root = Node(board, player_color)
    best_next_state = monte_carlo_tree_search(root, num_iterations=250)
    if best_next_state == [None, None]: #if player cannot move
        return [None, None]
    else: 
        return best_next_state.last_move
