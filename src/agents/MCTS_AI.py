from utils.board import Board
import numpy as np
import random
import copy

class Node:
    def __init__(self, board: Board, player: int, depth: int, last_move=None, parent=None, simulated = False):
        # board is more generic state in other MCTS implementations
        self.board = board
        self.depth = depth
        self.simulated = simulated
        self.player = player
        self.last_move = last_move
        self.parent = parent
        self.children = []
        self.visit_count = 0
        self.wins = 0.0

def select(node):
    ''' Traverse tree of next board-states, selects node with best UCB score '''
    while node.children:
        # return node with highest UCB score
        node = max(node.children, key=ucb_score)
    selected = node.last_move
    if node.depth == 0:
        selected = 'root'
    print(f"Node {selected} selected, with visit count {node.visit_count}, UCT score {ucb_score(node)}")
    return node

def ucb_score(node):
    ''' (Upper-Confidence Bound) metric for selecting next node '''
    if node.visit_count == 0:
        return float('inf')
    
    # ------- UCB
    # average score of current node from visitation estimate
    avg_score = node.wins / node.visit_count
    if node.parent is not None: #avoids division by 0
        parent_visit_count = node.parent.visit_count
        # UCT = wins/visits + C + sqrt(log(parentvisits) / visits)
        exploration_score = (node.wins / node.visit_count) + np.sqrt(2) * (np.sqrt(np.log(parent_visit_count) / node.visit_count))
    else:
        exploration_score = 0
    
    return avg_score + exploration_score

def expand(node) -> Node:
    ''' Return next board-state nodes for given node '''
    possible_moves = node.board.all_legal_moves(node.player)
    for row, col in possible_moves:
        new_board = copy.deepcopy(node.board)  
        new_board.make_move(row, col, node.player)
        new_node = Node(new_board, (node.player * -1), node.depth+1,last_move=(row,col), parent=node)
        node.children.append(new_node)
    expanded = node.last_move
    if expanded == None:
        expanded = 'root'
    #print(f"Node {expanded} with parent {node.parent} expanded to {possible_moves}")
    return random.choice(node.children) if possible_moves else node

def backpropagate(node, winner):
    ''' Traverse back through the tree from outcome, updating score as we go '''
    
    if winner == 'Black':
        winner = 1
    elif winner == 'White':
        winner = -1
    else:
        winner = 0

    while node:
        id = node.last_move if node.parent else 'root'
        parent = node.parent.last_move if node.parent else 'root'
        if parent == None:
            parent = 'root'
        node.visit_count += 1
        if winner == node.player:
            node.wins += 1
            #print(f"BP Node {id} of player type: {node.player} node won - visits: {node.visit_count} wins: {node.wins}")
        elif winner == 0:# node drew
            node.wins += 0.5
            #print(f"BP Node {id} of player type: {node.player} node lost - visits: {node.visit_count} wins: {node.wins}")
        #else:
            #print(f"BP Node {id} of player type: {node.player} draw - visits: {node.visit_count} wins: {node.wins}")
        node = node.parent

def simulate(node) -> int:
    ''' Simulate a random rollout to end of game and return the result '''
    board = copy.deepcopy(node.board)
    #original_player = node.player
    player = node.player
    while not board.is_game_over():
        legal_moves = board.all_legal_moves(player)
        if not legal_moves:  # If the player has no legal moves, switch to the other player
            player *= -1
            continue
        row , col = random.choice(legal_moves)
        board.make_move(row, col, player)
        player *= -1 # Switch players after making a move
    node.simulated = True
    #print(f"Simulated from {node.last_move} of player type {original_player} to result {board.get_winner()}")
    return board.get_winner()

def monte_carlo_tree_search(root, num_iterations):
    ''' Main MCTS steps to return best next move '''
    for _ in range(num_iterations):
        # start from root and select nodes until leaf reached
        node = select(root)
        #print(f"Node: {node} selected")
        # expand out moves from root node & choose child random C
        node = expand(node)
        #print(f"Child {node} expanded")
        # rollout phase, play one game randomly from child node C, get 1 for win -1 for loss or 0
        winner = simulate(node)
        #print(f"Simulation from C ends in: {score}")
        # update scores from end to root based on simulation outcome
        backpropagate(node, winner)

    if root.children: #is not empty
        best_child = max(root.children, key=lambda node: node.visit_count)
        #for child in root.children:
            #for child in child.children:
                #print(f"Child children {child.last_move} Visit count: {node.visit_count} Wins: {node.wins}")
            #print(f"Available choice {child.last_move} Visit count: {child.visit_count} Wins: {child.wins}")
        #print(f"Node chosen {best_child.last_move} Visit count: {best_child.visit_count} Wins: {best_child.wins}")
        return best_child
    else:
        return (None, None)

def mcts_move(board: Board, player_color: int, iterations: int) -> tuple[int, int]:
    ''' Return best move for given player using MCTS '''
    root = Node(board, player_color, 0)
    move = monte_carlo_tree_search(root, iterations)
    if move == (None, None): #if player cannot move
        return (None, None)
    else: 
        return move.last_move
