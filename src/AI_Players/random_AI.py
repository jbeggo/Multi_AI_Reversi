from utils.board import Board
import random

def random_move(position: Board, player_colour: int) -> tuple[int, int]:
    
    # check if game over
    if position.is_game_over() is True:
        return (None,None)


    legal_moves = position.all_legal_moves(player_colour)
    if legal_moves:
        random_move = random.choice(legal_moves)
        return random_move
    else: return (None,None)
    
    