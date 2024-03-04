from utils.board import Board
from copy import deepcopy
import random

def random_move(position: Board) -> tuple[int, int]:

    bestMove = (20, 20)
    bestEval = float('+inf')

    legal_moves = position.all_legal_moves(Board.WHITE)

    random_move = random.choice(list(legal_moves))

    return random_move

