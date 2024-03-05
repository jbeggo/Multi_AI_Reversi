from utils.board import Board
import copy

class Node:
    def __init__(self, board, parent=None):
        # board is more generic state in other MCTS implementations
        self.board = copy.deepcopy(board)
        self.parent = parent
        self.children = []
        self.visit_count = 0
        self.total_score = 0.0

def select(node):
    ''' Traverse tree of next game-states, selects node with best USB score '''
    while node.children:
        node = max(node.children, key=ucb_score)
    return node

def ucb_score(node):
    ''' (Upper-Confidence Bound) metric for selecting next node '''
    if node.visit_count == 0:
        return float('inf')
    
    # ------- UCB
    # average score of current node from visitation estimate
    avg_score = node.total_score / node.visit_count
    
    # exploration score from balancing infrequently visited nodes & frequently
    exploration_score = sqrt(2 * log(node.parent.visit_count) / node.visit_count)
    
    # combine
    return avg_score + exploration_score

def expand(node):
    ''' Return next game-state nodes for given node '''
    possible_moves = node.board.all_legal_moves()
    for move in possible_moves:
        new_board = copy.deepcopy(node.board)  
        new_board.make_move(move)
        new_node = Node(new_board, parent=node)
        node.children.append(new_node)

def backpropagate(node, score):
    ''' Traverse back through the tree from outcome, updating score as we go '''
    while node:
        node.visit_count += 1
        node.total_score += score
        node = node.parent

def monte_carlo_tree_search(root, num_iterations):
    ''' Main function following MTCS steps to return best next move '''
    for _ in range(num_iterations):
        node = select(root)
        expand(node)
        score = simulate(node)
        backpropagate(node, score)
    return max(root.children, key=lambda n: n.visit_count)
