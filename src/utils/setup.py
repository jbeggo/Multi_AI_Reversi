from utils.board import Board
from utils.colors import Colors
from utils.minimax import find_best_move
import pygame
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

        self.background = Colors.WHITE

        # pygame window setup: set size, colours, window title
        self.screen = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT))
        self.screen.fill(Colors.WHITE)
        pygame.display.flip() # 'flip' is full display update
        pygame.display.set_caption("Reversi AI")

        # Load images from assets such as grid lines, starting menu, game over screen
        self.boardIMG = pygame.image.load("images/Light-Mode/Othello_Black_Side_Board.png")
        self.endScreenBlackIMG = pygame.image.load("images/Light-Mode/End_Screen_Black.png")
        self.endScreenWhiteIMG = pygame.image.load("images/Light-Mode/End_Screen_White.png")
        self.endScreenDrawIMG = pygame.image.load("images/Light-Mode/End_Screen_Draw.png")
        self.endPromptIMG  = pygame.image.load("images/Light-Mode/End_Prompt.png")
        self.choiceIMG = pygame.image.load("images/Light-Mode/Othello_Game-mode_Choice.png")
        self.blackCircleIMG = pygame.image.load("images/Light-Mode/black-circle.png")

        # Load font that displays the score
        self.scoreFont = pygame.font.Font("Gotham-Font/GothamLight.ttf", 40)

        self.single_player = False
        self.displayed_choice = False

        self.running = True
        
        self.is_game_over = False #just declaring
        self.move_preview = False

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

    def drawBlackDisc(self, x: int, y: int, r: int):
        #pygame.draw.circle(self.screen, Colors.BLACK, coords, radius)
        gfxdraw.aacircle(self.screen, x, y, r, Colors.BLACK)
        gfxdraw.filled_circle(self.screen, x, y, r, Colors.BLACK)
        
        #img = pygame.transform.scale(self.blackCircleIMG,(radius,radius))
        #self.screen.blit(img, (x, y))

    def drawWhiteDisc(self, x, y, radius: int, radius_diff: int):
        drawBlackDisc(self.screen, x, y,radius)
        pygame.draw.circle(self.screen, Colors.WHITE, (x, y), radius - radius_diff)

    def handleMouseClick(self) -> None:
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
        self.move_preview = False

        for pos in possible_moves:
            row, col = pos
            x = 100 + 75 * col
            y = 100 + 75 * row
            pygame.draw.rect(self.screen, self.background, pygame.Rect(x+4, y+4, 67, 67))

        self.turn *= -1
    
    def handleGameEnd(self, event: pygame.event.Event):
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
        self.single_player = False
        self.displayed_choice = False
        self.is_game_over = False
        self.game_board.reset_board()

        self.displayInitialBoardPos()
        self.last_move = (0,0)

    def displayDiscs(self) -> None:
        '''Display all the dics present on the game board'''

        for row in range(8):
            for col in range(8):
                #x = 137.5 + 75 * col
                x = 138 + 75 * col
                #y = 137.5 + 75 * row
                y = 138 + 75 * row
                if self.game_board.board[row, col] == Board.BLACK:
                    self.drawBlackDisc(x, y, 33)

                elif self.game_board.board[row, col] == Board.WHITE:
                    self.drawWhiteDisc(x, y, 33, 2.5)
    
    def markLastMove(self) -> None:
        '''Mark the last move made on the game board'''

        r, c = self.last_move

        x = c * 75 + 100 + 75/2
        y = r * 75 + 100 + 75/2
        pygame.draw.circle(self.screen, Colors.RED, (x, y), radius=5)
        pygame.display.flip()

    def displayScore(self) -> None:
        '''Blit the score of each player during the game'''

        dummy_surface = pygame.Surface((60, 40))
        dummy_surface.fill(self.background)
        self.screen.blit(dummy_surface, (885, 510))
        self.screen.blit(dummy_surface, (1060, 510))

        text_color = Colors.BLACK
        black_disc_count = self.scoreFont.render(f"{self.game_board.black_disc_count}", False, text_color)
        white_disc_count = self.scoreFont.render(f"{self.game_board.white_disc_count}", False, text_color)
        self.screen.blit(black_disc_count, (885, 510))
        self.screen.blit(white_disc_count, (1060, 510))
        
        pygame.display.flip()

    def displayLegalMoves(self) -> None:
        '''Display all the possible legal moves for the player with the current turn.'''

        if self.move_preview:    # possible moves are already displayed
            return
        
        possible_moves = self.game_board.all_legal_moves(self.turn)
        if not possible_moves:
            self.move_preview = False
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
            
        self.move_preview = True

    def gameOverScreen(self) -> None:
        '''Display the game over screen in accordance with the game result.'''

        if self.game_board.black_disc_count > self.game_board.white_disc_count: # black won
            Game.fade(self.screen, (self.endScreenBlackIMG, (725, 250)))

        elif self.game_board.black_disc_count < self.game_board.white_disc_count:   # white won
            Game.fade(self.screen, (self.endScreenWhiteIMG, (725, 250)))

        else:   # draw
            Game.fade(self.screen, (self.endScreenDrawIMG, (725, 250)))

        Game.fade(self.screen, (self.endPromptIMG, (877, 420)))
        self.is_game_over = True
    
    def computerPlayerTurn(self) -> None:
        '''Code to run when it is computer player's turn.'''
        
        r, c = find_best_move(self.game_board)
        self.move_preview = False
        
        if (r,c) == (20, 20):
            return
        
        self.last_move = (r, c)
        self.game_board.set_discs(r, c, self.turn)
        self.turn *= -1

        # update board visuals
        self.displayDiscs()
        self.markLastMove()
        self.displayScore()

    def handleGameModeChoice(self, event) -> None:
        '''Handle the events at the initial screen.'''

        if event.key not in (pygame.K_a, pygame.K_h):
            return
        
        self.single_player = (event.key == pygame.K_a)

        self.displayed_choice = True

        dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                            Game.WINDOW_HEIGHT  ))
        dummy_surface.fill(self.background)
        Game.fade(self.screen, (dummy_surface, (0, 0)))

        self.displayInitialBoardPos()
            
    def displayInitialBoardPos(self) -> None:
        '''Blitting initial board position on screen'''

        self.screen.blit(self.boardIMG, (0,0))

        self.drawBlackDisc(825, 525, 50)
        self.drawWhiteDisc(1000, 525, 50, 5)

    def game_loop(self) -> None:
        '''Game loop to run the application.'''

        while self.running:
            pygame.display.flip()
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handleMouseClick()

                elif self.is_game_over and event.type == pygame.KEYDOWN:
                    self.handleGameEnd(event)

                elif not self.displayed_choice and event.type == pygame.KEYDOWN:
                    self.handleGameModeChoice(event)

            if not self.displayed_choice:
                self.screen.blit(self.choiceIMG, (0,0))
                continue

            if self.is_game_over:
                continue  
            
            self.displayDiscs()
            
            self.markLastMove()

            self.displayScore()

            if self.single_player and self.turn == Board.WHITE:
                self.computerPlayerTurn()

            self.displayLegalMoves()

            if self.game_board.check_game_over() is True:
                self.gameOverScreen()

        pygame.quit()