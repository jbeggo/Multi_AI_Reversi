from utils.board import Board
import random

def random_move(position: Board) -> tuple[int, int]:

    legal_moves = position.all_legal_moves(Board.WHITE)

    random_move = random.choice(list(legal_moves))

    return random_move

