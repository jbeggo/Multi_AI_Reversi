from utils.board import Board
import random

def random_move_old(position: Board) -> tuple[int, int]:

    legal_moves = position.all_legal_moves(Board.WHITE)

    random_move = random.choice(list(legal_moves))

    return random_move

def random_move(position: Board, colour: int) -> tuple[int, int]:

    # random player is white
    if colour is -1:

        legal_moves = position.all_legal_moves(Board.WHITE)

    # random player is black
    elif colour is 1:

        legal_moves = position.all_legal_moves(Board.BLACK)

    else: raise Exception("Random type player must be white or black")
    

    random_move = random.choice(list(legal_moves))

    return random_move
