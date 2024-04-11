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
        self.board = np.array([0]*8, dtype = np.int8)   # initiliasing 1D array with the first row of 8 zeroes
        self.board = self.board[np.newaxis, : ]         # expanding 1D array to 2D array
        for _ in range(3):                              # increasing rows till 8
            self.board = np.concatenate((self.board, self.board), axis = 0)

        # centre squares in middle of board
        self.board[3, 3] = self.board[4,4] = Board.WHITE
        self.board[3, 4] = self.board[4,3] = Board.BLACK

        self.black_disk_count = 2
        self.white_disk_count = 2
    
    @staticmethod
    def is_valid_cell(x: int, y: int) -> bool:
        '''Returns true if given coords correspond to valid cell in an 8x8 matrix'''

        return (x >= 0 and y >= 0) and (x < 8 and y < 8)

    def all_legal_moves(self, PLAYER: int) -> list:
        '''Return all legal moves for the player'''

        all_legal_moves = []
        for row in range(8):
            for col in range(8):
                if self.board[row, col] == PLAYER:
                    all_legal_moves.extend(self.legal_moves(row, col))
        
        return all_legal_moves

    def all_legal_moves_old(self, PLAYER: int) -> set:
        '''Return all legal moves for the player'''

        all_legal_moves = set()
        for row in range(8):
            for col in range(8):
                if self.board[row, col] == PLAYER:
                    all_legal_moves.update(self.legal_moves(row, col))
        
        return all_legal_moves

    def legal_moves(self, r: int, c: int) -> list:
        '''Return all legal moves for the cell at the given position'''

        PLAYER = self.board[r, c]
        OPPONENT = PLAYER * -1

        legal_moves = []
        for dir in Board.DIRECTIONS:
            rowDir, colDir = dir
            row = r + rowDir
            col = c + colDir
                
            if Board.is_valid_cell(row, col) is False or self.board[row, col] != OPPONENT:
                continue
            
            row += rowDir
            col += colDir
            while (Board.is_valid_cell(row, col) is True and self.board[row, col] == OPPONENT):
                row += rowDir
                col += colDir
            if (Board.is_valid_cell(row, col) is True and self.board[row, col] == Board.EMPTY):   # possible move
                legal_moves.append((row, col))

        return legal_moves

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

    def flip_disks(self, PLAYER: int, initCoords: tuple[int, int], endCoords: tuple[int, int], direction: tuple[int, int]):
        '''Flip the disks between the given two cells to the given PLAYER color.'''

        OPPONENT = PLAYER * -1
        rowDir, colDir = direction

        row, col = initCoords
        row += rowDir
        col += colDir 

        r, c = endCoords

        while (self.board[row, col] == OPPONENT) and (row != r or col != c):
            self.board[row, col] = PLAYER
            row += rowDir
            col += colDir

    def make_move(self, row: int, col: int, PLAYER: int) -> None:
        ''' Set the disks on the board as per the move made on the given cell '''
        
        self.board[row, col] = PLAYER
        OPPONENT = PLAYER * - 1
        
        for dir in Board.DIRECTIONS:
            rowDir, colDir = dir
            r = row + rowDir
            c = col + colDir

            if Board.is_valid_cell(r, c) is False or self.board[r, c] != OPPONENT:
                continue
            
            r += rowDir
            c += colDir
            while (Board.is_valid_cell(r, c) is True and self.board[r, c] == OPPONENT):
                r += rowDir
                c += colDir
            if (Board.is_valid_cell(r, c) is True and self.board[r, c] == PLAYER):
                self.flip_disks(PLAYER, (row, col), (r, c), dir) 
                
        # update disc counters
        self.black_disk_count = self.board[self.board > 0].sum()
        self.white_disk_count = -self.board[self.board < 0].sum()

    def reset_board(self) -> None:
        """
        Reset the game board to its initial state.

        This method fills the board with empty squares and initializes the center squares
        with two white and two black disks

        """
        self.board.fill(Board.EMPTY)

        # initiliasing the centre squares
        self.board[3, 3] = self.board[4,4] = Board.WHITE
        self.board[3, 4] = self.board[4,3] = Board.BLACK

        self.black_disk_count = self.white_disk_count = 2

    
    def is_game_over(self) -> bool:
        '''Return True if the game is over (i.e., neither player can make a move), False otherwise'''

        return len(self.all_legal_moves(Board.BLACK)) == 0 and len(self.all_legal_moves(Board.WHITE)) == 0

    def evaluate_board(self, player) -> int:
        '''Evaluate the board as per coin parity, mobility & corner value heuristics.'''

        # coin parity heuristic - difference in number of disks for player
        if player == Board.BLACK:
            coin_parity = 100 * (self.black_disk_count - self.white_disk_count) / (self.black_disk_count + self.white_disk_count)
        else:
            coin_parity = 100 * (self.white_disk_count - self.black_disk_count) / (self.black_disk_count + self.white_disk_count)
        
        # mobility heuristic - number of empty spaces a player could move into
        black_mobility = len(self.all_legal_moves(Board.BLACK))
        white_mobility = len(self.all_legal_moves(Board.WHITE))
        if black_mobility + white_mobility == 0:
            actual_mobility = 0
        else:
            # evaluate for given player
            if player == Board.BLACK:
                actual_mobility = 100 * (black_mobility - white_mobility) / (black_mobility + white_mobility)
            else:
                actual_mobility = 100 * (white_mobility - black_mobility) / (black_mobility + white_mobility)
        
        # corner heuristic - corners cannot be flipped once set
        corners = (self.board[0, 0], self.board[0,7], self.board[7, 0], self.board[7, 7])
        if player == Board.BLACK:
            player_corners = sum(+20 for coin in corners if coin == Board.BLACK)
            opponent_corners = sum(-20 for coin in corners if coin == Board.WHITE)
        else:
            player_corners = sum(+20 for coin in corners if coin == Board.WHITE)
            opponent_corners = sum(-20 for coin in corners if Board.BLACK)

        if player_corners + opponent_corners == 0:
            corner_value = 0
        else:
            corner_value = 100 * (player_corners - opponent_corners) / (player_corners + opponent_corners)

        return coin_parity + actual_mobility + corner_value