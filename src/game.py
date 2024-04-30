from utils.board import Board
from utils.colors import Colours
from agents.minimax_AI import minimax_move, minimax_noprune_move
from agents.random_AI import random_move
from agents.greedy_AI import greedy_move
from agents.negamax_AI import negamax_move
from agents.MCTS_AI import mcts_move
from agents.value_matrix_AI import evolutionary_matrix_move, wipeout_matrix_move
from agents.dqn_AI import Qagent
import pygame, time
from pygame import gfxdraw

pygame.init()

class Game:
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800

    def __init__(self) -> None:
        '''Initialise the Game Object'''

        self.game_board = Board()

        self.background = (204,204,204)
        self.text_colour = (0,0,0)

        self.high_contrast = False

        # pygame window setup: set size, colours, window title
        self.screen = pygame.display.set_mode((Game.WINDOW_WIDTH, Game.WINDOW_HEIGHT))
        self.screen.fill(Colours.WHITE)
        pygame.display.flip() # 'flip' is full display update
        pygame.display.set_caption("Reversi AI")

        # Load images such as grid lines, starting menu, game over screen
        self.boardIMG = pygame.image.load("images/board.png")

        self.black_winsIMG = pygame.image.load("images/black_wins.png")
        self.white_winsIMG = pygame.image.load("images/white_wins.png")
        self.drawIMG = pygame.image.load("images/draw.png")

        self.replay_choiceIMG  = pygame.image.load("images/replay.png")
        self.menuIMG = pygame.image.load("images/main_menu.png")
        self.choose_opponentIMG = pygame.image.load("images/choose_AI.png")
        self.choose_p1IMG = pygame.image.load("images/choose_p1.png")
        self.choose_p2IMG = pygame.image.load("images/choose_p2.png")

        # Load font that displays the score
        self.score_font = pygame.font.Font("Gotham-Font/GothamLight.ttf", 40)
        self.message_font = pygame.font.Font("Gotham-Font/GothamLight.ttf", 60)
        self.player_font = pygame.font.Font("Gotham-Font/GothamLight.ttf", 20)

        self.preview_positions = []
        self.is_single_player = False
        self.computer_vs_computer = False
        self.player_vs_player = False
        self.game_mode_chosen = False
        self.opponent_chosen = False

        self.chosen_AI = None # for PvAI
        
        self.chosen_p1 = None # for AIvAI
        self.chosen_p2 = None 
        self.p1_set = False
        self.p2_set = False
        self.players_set = False

        self.running = True
        
        self.is_game_over = False
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

    def toggle_high_contrast(self) -> None:
        '''Toggle the high contrast mode of the game for accessibility'''

        if not self.high_contrast:
            # set high contrast mode
            self.high_contrast = True
            self.background = (13, 12, 12)
            self.text_colour = (255, 245, 0)
            self.boardIMG = pygame.image.load("images/board(access).png")
            self.black_winsIMG = pygame.image.load("images/black_wins(access).png")
            self.white_winsIMG = pygame.image.load("images/white_wins(access).png")
            self.drawIMG = pygame.image.load("images/draw(access).png")
            self.replay_choiceIMG  = pygame.image.load("images/replay(access).png")
            self.menuIMG = pygame.image.load("images/main_menu(access).png")
            self.choose_opponentIMG = pygame.image.load("images/choose_AI(access).png")
            self.choose_p1IMG = pygame.image.load("images/choose_p1(access).png")
            self.choose_p2IMG = pygame.image.load("images/choose_p2(access).png")
        else:
            self.high_contrast = False
            self.background = (204, 204, 204)
            self.text_colour = (0,0,0)
            self.boardIMG = pygame.image.load("images/board.png")
            self.black_winsIMG = pygame.image.load("images/black_wins.png")
            self.white_winsIMG = pygame.image.load("images/white_wins.png")
            self.drawIMG = pygame.image.load("images/draw.png")
            self.replay_choiceIMG  = pygame.image.load("images/replay.png")
            self.menuIMG = pygame.image.load("images/main_menu.png")
            self.choose_opponentIMG = pygame.image.load("images/choose_AI.png")
            self.choose_p1IMG = pygame.image.load("images/choose_p1.png")
            self.choose_p2IMG = pygame.image.load("images/choose_p2.png")

        

    def draw_black_disk(self, x: int, y: int, r: int):
        if not self.high_contrast:
            gfxdraw.aacircle(self.screen, x, y, r, Colours.BLACK)
            gfxdraw.filled_circle(self.screen, x, y, r, Colours.BLACK)
        else:
            gfxdraw.aacircle(self.screen, x, y, r, (0, 255, 255))
            gfxdraw.filled_circle(self.screen, x, y, r, (0, 255, 255))
   
    def draw_white_disk(self, x: int, y: int, r: int):
        if not self.high_contrast:
            gfxdraw.aacircle(self.screen, x, y, r, Colours.WHITE)
            gfxdraw.filled_circle(self.screen, x, y, r, Colours.WHITE)
        else:
            gfxdraw.aacircle(self.screen, x, y, r, (255, 192, 203))
            gfxdraw.filled_circle(self.screen, x, y, r, (255, 192, 203))

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
        self.game_board.make_move(r, c, self.turn)
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
        self.display_score()
    
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
        self.opponent_chosen = False
        self.chosen_AI = None
        self.game_board = Board() # create a new fresh board

        self.display_starting_pieces()
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

    def display_score(self) -> None:
        '''Display the score text of each player'''

        dummy_surface = pygame.Surface((60, 40))
        dummy_surface.fill(self.background)
        self.screen.blit(dummy_surface, (885, 510))
        self.screen.blit(dummy_surface, (1060, 510))

        text_color = self.text_colour
        black_disc_count = self.score_font.render(f"{self.game_board.black_disk_count}", True, text_color)
        white_disc_count = self.score_font.render(f"{self.game_board.white_disk_count}", True, text_color)
        self.screen.blit(black_disc_count, (885, 510))
        self.screen.blit(white_disc_count, (1060, 510))
        
        pygame.display.flip()

    def display_thinking(self) -> None:
        '''Blit a message while the AI player concocts a move to make'''

        text_surface = pygame.Surface((60, 40))
        text_surface.fill(self.background)
        self.screen.blit(text_surface, (860, 210))

        text_color = self.text_colour
        thinking_text = self.message_font.render(f"Thinking...", True, text_color)
        self.screen.blit(thinking_text, (820, 210))
        
        pygame.display.flip()

    def clear_thinking(self):
        '''Clear the AI decision time message'''
        
        pygame.draw.rect(self.screen, self.background, pygame.Rect(820, 200, 300, 100))

        pygame.display.flip()

    def display_turn(self) -> None:
        '''Blit a message while the AI player concocts a move to make'''

        #text_surface = pygame.Surface((60, 40))
        #text_surface.fill(self.background)
        #self.screen.blit(text_surface, (30, 720))

        pygame.draw.rect(self.screen, self.background, pygame.Rect(20, 710, 300, 60))
        text_color = self.text_colour
        if not self.high_contrast:
            turn = "Black's" if self.turn == 1 else "White's"
        else:
            turn = "Cyan's" if self.turn == 1 else "Pinks's"
        turn_text = self.score_font.render(f"{turn} turn!", True, text_color)
        self.screen.blit(turn_text, (30, 720))
        
        pygame.display.flip()

    def clear_turn_text(self):
        '''Clear the AI decision time message'''
        
        pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(20, 710, 300, 60))

        pygame.display.flip()

    def display_opponent(self) -> None:
        '''Display the name of the current opponent above the board'''

        pygame.draw.rect(self.screen, self.background, pygame.Rect(40, 30, 500, 60))
        text_color = self.text_colour
        opp_name = self.score_font.render(f"Opponent: {self.chosen_AI}", True, text_color)

        self.screen.blit(opp_name, (90, 40))  
        
        pygame.display.flip()

    def display_players(self) -> None:
        '''Display the current AI players below the score text'''

        text_color = self.text_colour

        p1_name = self.player_font.render(f"{self.chosen_p1}", True, text_color)
        p2_name = self.player_font.render(f"{self.chosen_p2}", True, text_color)

        self.screen.blit(p1_name, (885, 560)) 
        self.screen.blit(p2_name, (1060, 560))  
        
        pygame.display.flip()

    def move_preview(self):
        '''Display previews for the current player as shadowed circles'''

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
                if not self.high_contrast:
                    pygame.draw.circle(surface,(*Colours.BLACK, 50),(37.5, 37.5), 32.5)
                else:
                    pygame.draw.circle(surface,(*(0, 255, 255), 50),(37.5, 37.5), 32.5)

            elif self.turn == Board.WHITE:
                if not self.high_contrast:
                    pygame.draw.circle(surface,(*Colours.BLACK, 50),(37.5, 37.5), 32.5)
                    pygame.draw.circle(surface,(*Colours.WHITE, 50),(37.5, 37.5), 30)
                else:
                    pygame.draw.circle(surface,(*(255, 192, 203), 50),(37.5, 37.5), 32.5)
                    pygame.draw.circle(surface,(*Colours.WHITE, 50),(37.5, 37.5), 30)
            self.screen.blit(surface, (x, y))

            # Store the position of the preview
            self.preview_positions.append((x, y))
            
        self.preview_set = True

    def clear_preview(self):
        ''' Draws a rectangle over old move previewed cells in background colour '''
        
        for pos in self.preview_positions:
            x, y = pos
            pygame.draw.rect(self.screen, self.background, pygame.Rect(x+4, y+4, 67, 67))

        # Reset the preview_positions list
        self.preview_positions = []
        self.preview_set = False
    
    def game_over_screen(self) -> None:
        '''Display the game over screen in accordance with the game result.'''

        if self.game_board.black_disk_count > self.game_board.white_disk_count: # black won
            Game.fade(self.screen, (self.black_winsIMG, (725, 250)))

        elif self.game_board.black_disk_count < self.game_board.white_disk_count:   # white won
            Game.fade(self.screen, (self.white_winsIMG, (725, 250)))

        else:   # draw
            Game.fade(self.screen, (self.drawIMG, (725, 250)))

        Game.fade(self.screen, (self.replay_choiceIMG, (840, 410)))
        self.is_game_over = True

    def computer_turn(self, player, chosen_AI) -> None:
        ''' Code to run when computer player's turn '''
        
        # determine the move based on the chosen AI
        if chosen_AI == "random":
            r, c = random_move(self.game_board, player)
        elif chosen_AI == "greedy":
            r, c = greedy_move(self.game_board, player)
        elif chosen_AI == "negamax":
            r, c = negamax_move(self.game_board, player)
        elif chosen_AI == "simple minimax":
            r, c = minimax_noprune_move(self.game_board, player)
        elif chosen_AI == "minimax":
            r, c = minimax_move(self.game_board, player)
        elif chosen_AI == "mcts-100":
            r, c = mcts_move(self.game_board, player, 250)
        elif chosen_AI == "mcts-250":
            r, c = mcts_move(self.game_board, player, 500)
        elif chosen_AI == "wipeout matrix":
            r, c = wipeout_matrix_move(self.game_board, player)
        elif chosen_AI == "evolutionary matrix":
            r, c = evolutionary_matrix_move(self.game_board, player)
        elif chosen_AI == "Q-Learner NN":
            r, c = self.Qagent.dqn_move(self.game_board, player)


        self.preview_set = False
        
        # cannot move (skip)
        if (r,c) == (None,None):
            return
        
        self.last_move = (r, c)
        self.game_board.make_move(r, c, self.turn)
        self.turn *= -1

        self.clear_preview

        # update board visuals
        self.display_disks()
        #self.mark_last_move()
        self.display_score()

    def choose_game_mode(self, event) -> None:
        ''' Handles the mode choice at main menu, Player VS AI, AI VS AI etc... '''

        if event.key not in (pygame.K_a, pygame.K_h, pygame.K_s, pygame.K_c):
            return
        
        # press a to play human vs AI
        self.is_single_player = (event.key == pygame.K_a)

        # press s to play AI vs AI
        self.computer_vs_computer = (event.key == pygame.K_s)
        
        # h to play a friend
        self.player_vs_player = (event.key == pygame.K_h)
        
        self.game_mode_chosen = True

        # c to switch to high contrast mode
        if event.key == pygame.K_c:
            self.game_mode_chosen = False # stay on menu if switching view
            self.toggle_high_contrast()

        # continue if chosen
        if self.game_mode_chosen:

            dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                            Game.WINDOW_HEIGHT  ))
            dummy_surface.fill(self.background)
            Game.fade(self.screen, (dummy_surface, (0, 0)))

            # pvp can jump straight in
            if self.player_vs_player:
                self.display_starting_pieces()
    
    def choose_opponent(self, event) -> None:
        ''' Handles the choice of AI opponent for Player Vs AI mode '''

        if event.key not in (range(pygame.K_0, pygame.K_9 + 1)): # if not number key pressed
            return
        
        if event.key == pygame.K_1:
            self.chosen_AI = "random"
        elif event.key == pygame.K_2:
            self.chosen_AI = "greedy"
        elif event.key == pygame.K_3:
            self.chosen_AI = "negamax [2]"
        elif event.key == pygame.K_4:
            self.chosen_AI = "minimax [2]"
        elif event.key == pygame.K_5:
            self.chosen_AI = "minimax [3]"
        elif event.key == pygame.K_6:
            self.chosen_AI = "mcts-100"
        elif event.key == pygame.K_7:
            self.chosen_AI = "mcts-250"
        elif event.key == pygame.K_8:
            self.chosen_AI = "wipeout matrix"
        elif event.key == pygame.K_9:
            self.chosen_AI = "evolutionary matrix"
        elif event.key == pygame.K_0:
            self.chosen_AI = "Q-Learner NN"
            self.Qagent = Qagent()
            self.Qagent.load_model("models/Best_Model.keras")
        
        self.opponent_chosen = True

        dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                        Game.WINDOW_HEIGHT  ))
        dummy_surface.fill(self.background)
        Game.fade(self.screen, (dummy_surface, (0, 0)))

        self.display_starting_pieces()
            
    def choose_p1(self, event) -> None:
        ''' Handles the choice of AI opponent for AI vs AI player 1 '''

        print("In choose p1")
        if event.key not in (range(pygame.K_1, pygame.K_9)): # if not number key pressed
            return
        
        if event.key == pygame.K_1:
            self.chosen_p1 = "random"
        elif event.key == pygame.K_2:
            self.chosen_p1 = "greedy"
        elif event.key == pygame.K_3:
            self.chosen_p1 = "negamax [2]"
        elif event.key == pygame.K_4:
            self.chosen_p1 = "minimax [2]"
        elif event.key == pygame.K_5:
            self.chosen_p1 = "minimax [3]"
        elif event.key == pygame.K_6:
            self.chosen_p1 = "mcts-100"
        elif event.key == pygame.K_7:
            self.chosen_p1 = "mcts-250"
        elif event.key == pygame.K_8:
            self.chosen_p1 = "wipeout matrix"
        elif event.key == pygame.K_9:
            self.chosen_p1 = "evolutionary matrix"
        elif event.key == pygame.K_0:
            self.chosen_p1 = "Q-Learner NN"
            self.Qagent = Qagent()
            self.Qagent.load_model("models/Best_Model.keras")

        self.p1_set = True

        dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                        Game.WINDOW_HEIGHT  ))
        dummy_surface.fill(self.background)
        Game.fade(self.screen, (dummy_surface, (0, 0)))
 
    def choose_p2(self, event) -> None:
        ''' Handles the choice of AI opponent for AI vs AI player 2 '''

        if event.key not in (range(pygame.K_0, pygame.K_9 + 1)): # if not number key pressed
            return
        
        if event.key == pygame.K_1:
            self.chosen_p2 = "random"
        elif event.key == pygame.K_2:
            self.chosen_p2 = "greedy"
        elif event.key == pygame.K_3:
            self.chosen_p2 = "negamax [2]"
        elif event.key == pygame.K_4:
            self.chosen_p2 = "minimax [2]"
        elif event.key == pygame.K_5:
            self.chosen_p2 = "minimax [3]"
        elif event.key == pygame.K_6:
            self.chosen_p2 = "mcts-100"
        elif event.key == pygame.K_7:
            self.chosen_p2 = "mcts-250"
        elif event.key == pygame.K_8:
            self.chosen_p2 = "wipeout matrix"
        elif event.key == pygame.K_9:
            self.chosen_p2 = "evolutionary matrix"
        elif event.key == pygame.K_0:
            self.chosen_p2 = "Q-Learner NN"
            self.Qagent = Qagent()
            self.Qagent.load_model("models/Best_Model.keras")

        self.p2_set = True
        self.players_set = True

        dummy_surface = pygame.Surface( (Game.WINDOW_WIDTH, 
                                        Game.WINDOW_HEIGHT  ))
        dummy_surface.fill(self.background)
        Game.fade(self.screen, (dummy_surface, (0, 0)))

        self.display_starting_pieces() # jump in after p2 chosen

    def display_starting_pieces(self) -> None:
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
                # for debugging events that are not mouse clicks
                #if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN):
                    #print(event)
                
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.do_mouse_click()

                elif self.is_game_over and event.type == pygame.KEYDOWN:
                    self.game_over(event)

                elif not self.game_mode_chosen and event.type == pygame.KEYDOWN:
                    self.choose_game_mode(event)

                # Player vs AI
                elif self.is_single_player and not self.opponent_chosen and event.type == pygame.KEYDOWN:
                    self.choose_opponent(event)

                # AI vs AI
                elif self.computer_vs_computer and not self.p1_set and event.type == pygame.KEYDOWN:
                    self.choose_p1(event)
                
                elif self.computer_vs_computer and not self.p2_set and event.type == pygame.KEYDOWN:
                    self.choose_p2(event)

            if not self.game_mode_chosen:
                self.screen.blit(self.menuIMG, (0,0))
                continue
            elif not self.opponent_chosen and self.is_single_player:
                self.screen.blit(self.choose_opponentIMG, (0,0))
                continue
            elif not self.p1_set and self.computer_vs_computer:
                self.screen.blit(self.choose_p1IMG, (0,0))
                continue
            elif not self.p2_set and self.computer_vs_computer:
                self.screen.blit(self.choose_p2IMG, (0,0))
                continue

            if self.is_game_over:
                continue  
            
            self.display_disks()
            
            #self.mark_last_move()

            self.display_score()
            self.display_turn()

            if self.is_single_player:
                self.display_opponent()

            # Chosen AI plays white against human
            if self.is_single_player and self.turn == Board.WHITE:
                self.display_thinking()
                time.sleep(2)
                self.computer_turn(Board.WHITE,self.chosen_AI)
                self.clear_thinking()
                #self.clear_turn_text()

            # AI plays black & white w/ arbitrary slowdown factor
            if self.computer_vs_computer and self.players_set:
                self.display_players()
                self.computer_turn(Board.BLACK, self.chosen_p1)
                time.sleep(0.1)
                self.computer_turn(Board.WHITE, self.chosen_p2)
                time.sleep(0.1)
            
            # only need previews for humans
            if self.is_single_player or self.player_vs_player:
                self.move_preview()

            # game over?
            if self.game_board.is_game_over():
                self.game_over_screen()


        pygame.quit()

game = Game()
game.game_loop()