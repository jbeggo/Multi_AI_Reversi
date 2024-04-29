import numpy as np

class Board:
    
    WHITE = -1
    BLACK =  1
    EMPTY =  0

    DIRECTIONS = (  ( 1, 0),    # right
                    (-1, 0),    # left
                    ( 0, 1),    # down
                    (-1, 1),    # down left
                    ( 1, 1),    # down right
                    ( 0,-1),    # up
                    (-1,-1),    # up left
                    ( 1,-1),    # up right
                )

    def __init__(self) -> None:
        '''Initialise board as a 8x8 2D numpy array (matrix)'''
        self.board = np.zeros((8, 8), dtype=np.int8)
        self.black_disk_count = self.white_disk_count = 0
                
        # centre squares in middle of board
        self.board[3, 3] = self.board[4,4] = Board.WHITE
        self.board[3, 4] = self.board[4,3] = Board.BLACK

        self.update_counts()
    
    def update_counts(self):
        self.black_disk_count = np.sum(self.board == Board.BLACK)
        self.white_disk_count = np.sum(self.board == Board.WHITE)

    def reset(self) -> None:
        self.__init__()

    def get_winner(self):
        '''Returns the winner of the game'''

        # Count the number of pieces for each player
        black_pieces = np.sum(self.board == Board.BLACK)
        white_pieces = np.sum(self.board == Board.WHITE)

        # Determine the winner
        if black_pieces > white_pieces:
            return 'Black'
        elif white_pieces > black_pieces:
            return 'White'
        else:
            return 'Draw'
    
    @staticmethod
    def is_valid_cell(x: int, y: int) -> bool:
        '''Returns true if given coords correspond to valid cell in an 8x8 matrix'''

        return 0 <= x < 8 and 0 <= y < 8

    def all_legal_moves(self, player: int) -> list:
        '''Return all legal moves for the player'''

        legal_moves = set()
        for r in range(8):
            for c in range(8):
                if self.board[r, c] == player:
                    moves = self.legal_moves(r, c, player)
                    legal_moves.update(moves)
        return list(legal_moves)

    def legal_moves(self, r, c, player):
        '''Return legal moves from a particular cell and player'''
        opponent = -player
        valid_moves = set()
        
        for dx, dy in Board.DIRECTIONS:
            x, y = r + dx, c + dy
            
            if self.is_valid_cell(x, y) and self.board[x, y] == opponent:
                # Move in the direction while it is opponent's piece
                x += dx
                y += dy
                while self.is_valid_cell(x, y) and self.board[x, y] == opponent:
                    x += dx
                    y += dy
                    if not self.is_valid_cell(x, y) or self.board[x, y] != opponent:
                        break
                # Place piece if the chain ends in an empty square
                if self.is_valid_cell(x, y) and self.board[x, y] == Board.EMPTY:
                    valid_moves.add((x, y))
        
        return valid_moves

    def print_board(self) -> None:
        '''Print the current state of the board in a readable format'''

        print() # leave a gap
        for row in self.board:
            for cell in row:
                if cell == Board.WHITE:
                    print("W", end=" ")
                elif cell == Board.BLACK:
                    print("B", end=" ")
                else:
                    print(".", end=" ")
            print()

    def print_score(self) -> str:
        ''' Return the current score in the form of "White: x, Black: x" '''
        print(f"White: {self.white_disk_count}, Black: {self.black_disk_count}")

    def flip_disks(self, start_row, start_col, player, dx, dy):
        '''Flip opponent's disks following the rules of reversi'''
        row, col = start_row + dx, start_col + dy
        while self.is_valid_cell(row, col) and self.board[row, col] == -player:
            self.board[row, col] = player
            row += dx
            col += dy

    def make_move(self, row, col, player):
        '''Make a move for the player at specified row and column, updating the board'''
        if (row, col) not in self.all_legal_moves(player):
            raise ValueError("Move is not allowed")

        self.board[row, col] = player
        for dx, dy in Board.DIRECTIONS:
            if self.capture_pieces(row, col, player, dx, dy):
                self.flip_disks(row, col, player, dx, dy)

        self.update_counts()
    
    def capture_pieces(self, start_row, start_col, player, dx, dy):
        '''Check if placing a piece captures opponent's pieces'''
        row, col = start_row + dx, start_col + dy
        pieces_to_flip = []
        while self.is_valid_cell(row, col) and self.board[row, col] == -player:
            pieces_to_flip.append((row, col))
            row += dx
            col += dy

        if self.is_valid_cell(row, col) and self.board[row, col] == player:
            return pieces_to_flip
        return []

    def is_game_over(self):
        '''Check if the game is over by looking for available moves for both players'''
        black_moves = len(self.all_legal_moves(Board.BLACK))
        white_moves = len(self.all_legal_moves(Board.WHITE))
        return black_moves == 0 and white_moves == 0

    def evaluate_board(self, player) -> int:
        '''Evaluate the board as per coin parity, mobility & corner value heuristics.'''

        # coin parity heuristic - difference in number of disks for player
        total_on_board = self.black_disk_count + self.white_disk_count
        
        if player == Board.BLACK:
            coin_dif = self.black_disk_count - self.white_disk_count
            coin_parity = 100 * (coin_dif) / (total_on_board)
        else:
            coin_dif = self.white_disk_count - self.black_disk_count
            coin_parity = 100 * (coin_dif) / (total_on_board)
        
        # mobility heuristic - number of empty spaces a player could move into
        black_mobility = len(self.all_legal_moves(Board.BLACK))
        white_mobility = len(self.all_legal_moves(Board.WHITE))
        total_mobility = black_mobility + white_mobility
        if black_mobility == white_mobility:
            actual_mobility = 0
        else:
            # evaluate for given player
            if player == Board.BLACK:
                mob_dif = black_mobility - white_mobility
                actual_mobility = 100 * (mob_dif) / (total_mobility)
            else:
                mob_dif = white_mobility - black_mobility
                actual_mobility = 100 * (mob_dif) / (total_mobility)
        
        # corner heuristic - corners cannot be flipped once set
        corners = (self.board[0, 0], self.board[0,7], self.board[7, 0], self.board[7, 7])

        player_corners = sum(+25 for coin in corners if coin == player)
        opponent_corners = sum(-25 for coin in corners if coin == player*-1)

        corner_dif = player_corners - opponent_corners
        corner_total = player_corners + opponent_corners

        if player_corners + opponent_corners == 0: corner_value = 0
        else: corner_value = 100 * (corner_dif) / (corner_total)

        return coin_parity + actual_mobility + corner_value
    
    def evaluate_nn(self, player) -> int:
        '''Evaluate the board as per coin parity, mobility & corner value heuristics.'''

        # coin parity heuristic - difference in number of disks for player
        total_on_board = self.black_disk_count + self.white_disk_count
        
        if player == Board.BLACK:
            coin_dif = self.black_disk_count - self.white_disk_count
            coin_parity = 100 * (coin_dif) / (total_on_board)
        else:
            coin_dif = self.white_disk_count - self.black_disk_count
            coin_parity = 100 * (coin_dif) / (total_on_board)
        
        # mobility heuristic - number of empty spaces a player could move into
        black_mobility = len(self.all_legal_moves(Board.BLACK))
        white_mobility = len(self.all_legal_moves(Board.WHITE))
        total_mobility = black_mobility + white_mobility
        if black_mobility == white_mobility:
            actual_mobility = 0
        else:
            # evaluate for given player
            if player == Board.BLACK:
                mob_dif = black_mobility - white_mobility
                actual_mobility = 100 * (mob_dif) / (total_mobility)
            else:
                mob_dif = white_mobility - black_mobility
                actual_mobility = 100 * (mob_dif) / (total_mobility)
        
        # corner heuristic - corners cannot be flipped once set
        corners = (self.board[0, 0], self.board[0,7], self.board[7, 0], self.board[7, 7])

        player_corners = sum(+20 for coin in corners if coin == player)
        opponent_corners = sum(-20 for coin in corners if coin == player*-1)

        corner_dif = player_corners - opponent_corners
        corner_total = player_corners + opponent_corners

        if player_corners + opponent_corners == 0: corner_value = 0
        else: corner_value = 100 * (corner_dif) / (corner_total)

        # stability heuristic - possessing unflippable pieces on edges and corners conveys an advantage
        stable_pieces = 0
        stable_pieces_opp = 0

        for x, y in corners:
            # Determine the owner of the corner
            corner_owner = self.board[x][y]
            
            # Define adjacent positions based on the corner
            if x == 0 and y == 0:  # Top-Left
                adjacent = [(0, 1), (1, 0), (1, 1)]
            elif x == 0 and y == 7:  # Top-Right
                adjacent = [(0, 6), (1, 6), (1, 7)]
            elif x == 7 and y == 0:  # Bottom-Left
                adjacent = [(6, 0), (6, 1), (7, 1)]
            elif x == 7 and y == 7:  # Bottom-Right
                adjacent = [(6, 7), (7, 6), (6, 6)]

            # Check stability based on the corner owner
            for adj_x, adj_y in adjacent:
                if corner_owner == player:
                    if self.board[adj_x][adj_y] == player:
                        stable_pieces += 1
                elif corner_owner == player * -1:
                    if self.board[adj_x][adj_y] == player * -1:
                        stable_pieces_opp += 1

        # Calculate the stability value
        stable_total = stable_pieces + stable_pieces_opp
        if stable_total == 0:
            stability_value = 0
        else:
            stability_value = (stable_pieces - stable_pieces_opp) / stable_total * 100

        # return the evaluation score
        return coin_parity + actual_mobility + corner_value + stability_value
    