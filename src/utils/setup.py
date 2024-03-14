from utils.board import Board
from utils.colors import Colors
from utils.minimax_AI import minimax_move
from utils.random_AI import random_move
from utils.greedy_AI import greedy_move
import pygame, time
from pygame import gfxdraw

pygame.init()

class Game:
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    LIGHT = 1
    DARK = 0

    def __init__(self) -> None:
        '''Initialise the Game Object'''

        self.game_board = Board()

        self.background = (204,204,204)

        # pygame window setup: set size, colours, window title
        self.screen = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT))
        self.screen.fill(Colors.WHITE)
        pygame.display.flip() # 'flip' is full display update
        pygame.display.set_caption("Reversi AI")

        # Load images such as grid lines, starting menu, game over screen
        self.boardIMG = pygame.image.load("images/Board2.png")

        self.endScreenBlackIMG = pygame.image.load("images/Black_Win_Screen.png")
        self.endScreenWhiteIMG = pygame.image.load("images/White_Win_Screen.png")
        self.endScreenDrawIMG = pygame.image.load("images/Draw_Win_Screen.png")

        self.endPromptIMG  = pygame.image.load("images/Replay_Prompt.png")
        self.choiceIMG = pygame.image.load("images/Game_Mode_Prompt.png")

        # Load font that displays the score
        self.scoreFont = pygame.font.Font("Gotham-Font/GothamLight.ttf", 40)

        self.is_single_player = False
        self.game_mode_chosen = False

        self.running = True
        
        self.is_game_over = False #just declaring
        self.preview_set = False

        self.turn = 1 #black player always starts
        self.last_move = (0,0)

    @staticmethod
    def fade(screen: pygame.Surface, *surfaceNcoords: tuple[pygame.Surface, tuple[int, int]]):
        '''Fade-in surface(s) on a given screen, at the specified coordinates.'''

        for alpha in range(0, 257, 6):
            for snc in surfaceNcoords:
                surface, coordinates = snc
                surface.set_alpha(alpha)
                screen.blit(surface, coordinates)
                pygame.time.delay(30)
            pygame.display.flip()        

    def draw_black_disk(self, x: int, y: int, r: int):
        gfxdraw.aacircle(self.screen, x, y, r, Colors.BLACK)
        gfxdraw.filled_circle(self.screen, x, y, r, Colors.BLACK)
   
    def draw_white_disk(self, x: int, y: int, r: int):
        gfxdraw.aacircle(self.screen, x, y, r, Colors.WHITE)
        gfxdraw.filled_circle(self.screen, x, y, r, Colors.WHITE)

    def do_mouse_click(self) -> None:
        '''Handle events following mouse click on the board'''

        mx, my = pygame.mouse.get_pos()
        mx -= 100
        my -= 100
        r = my // 75
        c = mx // 75

        possible_moves = self.game_board.all_legal_moves(self.turn)
        if (r, c) not in possible_moves:   return

        self.last_move = (r, c)
        self.game_board.set_discs(r, c, self.turn)
        self.preview_set = False

        # draws over old move previews
        for pos in possible_moves:
            row, col = pos
            x = 100 + 75 * col
            y = 100 + 75 * row
            pygame.draw.rect(self.screen, self.background, pygame.Rect(x+4, y+4, 67, 67))

        self.turn *= -1

        # Update the display after each move
        self.display_disks()
        self.displayScore()
    
    def game_over(self, event: pygame.event.Event):
        '''Handle the events following the end of game:
                1. Either restarts the game,
                2. Or Quits the Application.
        '''

        if event.key not in (pygame.K_r, pygame.K_q): return

        # fade out the screen
        dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                            Game.WINDOW_HEIGHT  ))
        dummy_surface.fill(self.background)
        Game.fade(self.screen, (dummy_surface, (0, 0)))

        if event.key == pygame.K_q:
            self.running = False
            return
        
        '''Reset game init'''
        self.turn = Board.BLACK
        self.is_single_player = False
        self.game_mode_chosen = False
        self.is_game_over = False
        self.game_board.reset_board()

        self.displayInitialBoardPos()
        self.last_move = (0,0)

    def display_disks(self) -> None:
        '''Display all Disks on board (not score disks)'''

        # iterate over an 8x8 matrix
        for row in range(8):
            for col in range(8):
                # NOT SURE WHY THIS WASNT BROKEN PASSING FLOAT TO AN INT DRAW FUNCTION
                #x = 137.5 + 75 * col
                #y = 137.5 + 75 * row
                x = 138 + 75 * col
                y = 138 + 75 * row
                if self.game_board.board[row, col] == Board.BLACK:
                    self.draw_black_disk(x, y, 33)

                elif self.game_board.board[row, col] == Board.WHITE:
                    self.draw_white_disk(x, y, 33)

    def displayScore(self) -> None:
        '''Display the score text of each player'''

        dummy_surface = pygame.Surface((60, 40))
        dummy_surface.fill(self.background)
        self.screen.blit(dummy_surface, (885, 510))
        self.screen.blit(dummy_surface, (1060, 510))

        text_color = Colors.BLACK
        black_disc_count = self.scoreFont.render(f"{self.game_board.black_disk_count}", True, text_color)
        white_disc_count = self.scoreFont.render(f"{self.game_board.white_disk_count}", True, text_color)
        self.screen.blit(black_disc_count, (885, 510))
        self.screen.blit(white_disc_count, (1060, 510))
        
        pygame.display.flip()

    def move_preview(self):
        ''' Display all the possible legal moves for the player with the current turn '''

        if self.preview_set:    # possible moves are already displayed
            return
        
        possible_moves = self.game_board.all_legal_moves(self.turn)
        if not possible_moves:
            self.preview_set = False
            self.turn *= -1
            return
        
        # else there are new possible moves to be displayed
        
        surface = pygame.Surface((75, 75), pygame.SRCALPHA) # transparent surface to draw possible moves on
        for pos in possible_moves:
            r, c = pos
            x = 100 + 75 * c
            y = 100 + 75 * r

            if self.turn == Board.BLACK:
                pygame.draw.circle(surface,(*Colors.BLACK, 50),(37.5, 37.5), 32.5)

            elif self.turn == Board.WHITE:
                pygame.draw.circle(surface,(*Colors.BLACK, 50),(37.5, 37.5), 32.5)
                pygame.draw.circle(surface,(*Colors.WHITE, 50),(37.5, 37.5), 30)

            self.screen.blit(surface, (x, y))
            
        self.preview_set = True

    def clear_preview(self):
        ''' Draws a rectangle over old move previewed cells in background colour '''
        
        possible_moves = self.game_board.all_legal_moves(self.turn)
        
        for pos in possible_moves:
            row, col = pos
            x = 100 + 75 * col
            y = 100 + 75 * row
            pygame.draw.rect(self.screen, self.background, pygame.Rect(x+4, y+4, 67, 67))
    
    def gameOverScreen(self) -> None:
        '''Display the game over screen in accordance with the game result.'''

        if self.game_board.black_disk_count > self.game_board.white_disk_count: # black won
            Game.fade(self.screen, (self.endScreenBlackIMG, (725, 250)))

        elif self.game_board.black_disk_count < self.game_board.white_disk_count:   # white won
            Game.fade(self.screen, (self.endScreenWhiteIMG, (725, 250)))

        else:   # draw
            Game.fade(self.screen, (self.endScreenDrawIMG, (725, 250)))

        Game.fade(self.screen, (self.endPromptIMG, (877, 420)))
        self.is_game_over = True
    
    def random_AI_turn(self, colour) -> None:
        ''' Code to run when it is (random strategy) computer player's turn '''
        
        if colour == Board.WHITE:
            r, c = random_move(self.game_board, -1)
        elif colour == Board.BLACK:
            r, c = random_move(self.game_board, 1)
        else: raise Exception("random_AI_turn needs colour argument 1/-1")

        self.preview_set = False
        
        if (r,c) == (20, 20):
            return
        
        self.last_move = (r, c)
        self.game_board.set_discs(r, c, self.turn)
        self.turn *= -1

        self.clear_preview


        # update board visuals
        self.display_disks()
        #self.mark_last_move()
        self.displayScore()

    def greedy_AI_turn(self, colour) -> None:
        ''' Code to run when it is (basic greedy) computer player's turn '''
        
        r, c = greedy_move(self.game_board, colour)
        

        self.preview_set = False
        
        if (r,c) == (20, 20):
            return
        
        self.last_move = (r, c)
        self.game_board.set_discs(r, c, self.turn)
        self.turn *= -1

        self.clear_preview

        # update board visuals
        self.display_disks()
        #self.mark_last_move()
        self.displayScore()

    def minimax_AI_turn(self, colour) -> None:
        ''' Code to run when it is (minimax strategy) computer player's turn '''
        
        if colour == Board.WHITE:
            r, c = minimax_move(self.game_board)
        elif colour == Board.BLACK:
            r, c = minimax_move(self.game_board)
        else: raise Exception("minimax needs colour argument 1/-1")

        self.preview_set = False
        
        if (r,c) == (20, 20):
            return
        
        self.last_move = (r, c)
        self.game_board.set_discs(r, c, self.turn)
        self.turn *= -1

        self.clear_preview

        # update board visuals
        self.display_disks()
        #self.mark_last_move()
        self.displayScore()

    def choose_game_mode(self, event) -> None:
        ''' Handles the mode choice at main menu, Player VS AI, AI VS AI etc... '''

        if event.key not in (pygame.K_a, pygame.K_h, pygame.K_b):
            return
        
        # press a to play human vs AI
        self.is_single_player = (event.key == pygame.K_a)

        # press b to play AI vs AI
        self.computer_vs_computer = (event.key == pygame.K_b)
        
        self.game_mode_chosen = True

        dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                        Game.WINDOW_HEIGHT  ))
        dummy_surface.fill(self.background)
        Game.fade(self.screen, (dummy_surface, (0, 0)))

        self.displayInitialBoardPos()
            
    def displayInitialBoardPos(self) -> None:
        '''Blit the board image and score indicators'''

        self.screen.blit(self.boardIMG, (0,0))

        # draw the score circles
        self.draw_black_disk(825, 525, 50)
        self.draw_white_disk(1000, 525, 50)

    def game_loop(self) -> None:
        '''Game loop to run the application.'''

        while self.running:
            pygame.display.flip()
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.do_mouse_click()

                elif self.is_game_over and event.type == pygame.KEYDOWN:
                    self.game_over(event)

                elif not self.game_mode_chosen and event.type == pygame.KEYDOWN:
                    self.choose_game_mode(event)

            if not self.game_mode_chosen:
                self.screen.blit(self.choiceIMG, (0,0))
                continue

            if self.is_game_over:
                continue  
            
            self.display_disks()
            
            #self.mark_last_move()

            self.displayScore()

            # AI plays white against human
            if self.is_single_player and self.turn == Board.WHITE:
                self.random_AI_turn(Board.WHITE)

            # AI plays black & white w/ arbitrary slowdown factor
            if self.computer_vs_computer:
                self.greedy_AI_turn(1)
                time.sleep(0.2)
                self.minimax_AI_turn(-1)
                time.sleep(0.2)
            
            # only need previews for humans
            if self.is_single_player:
                self.move_preview()

            # game over?
            if self.game_board.is_game_over():
                self.gameOverScreen()

        pygame.quit()