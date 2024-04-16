from utils.board import Board
import random

def random_move_older(position: Board) -> tuple[int, int]:

    legal_moves = position.all_legal_moves(Board.WHITE)

    random_move = random.choice(legal_moves)

    return random_move

def random_move_old(position: Board, player_colour: int) -> tuple[int, int]:

    # random player is white
    if player_colour == -1:

        legal_moves = position.all_legal_moves(Board.WHITE)

    # random player is black
    elif player_colour == 1:

        legal_moves = position.all_legal_moves(Board.BLACK)

    else: raise Exception("Random type player must be white or black")
    

    random_move = random.choice(list(legal_moves))

    return random_move

def random_move(position: Board, player_colour: int) -> tuple[int, int]:
    
    # check if game over
    if position.is_game_over() is True:
        return (None,None)


    legal_moves = position.all_legal_moves(player_colour)
    if legal_moves:
        random_move = random.choice(legal_moves)
        return random_move
    else: return (None,None)
    
    