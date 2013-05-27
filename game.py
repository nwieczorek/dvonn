import pygame
from pygame.locals import *
import board
import button
import util
import ai

MESSAGE_POSITION = (10,350)
SCORE_POSITION = (500,350)
DVONN_PIECE_COUNT = 3
OTHER_PIECE_COUNT = 46 + DVONN_PIECE_COUNT
#-------------------------------------------------------------
# Classes
class Turn:
    def __init__(self):
        self.players = [util.BLACK,util.WHITE]
        self.current = 1
        self.set_player()
        self.phase = util.DVONN_PLACEMENT
        self.phase_counter = 1
        
    def next(self):
        self.current = (self.current + 1) % 2
        self.set_player()
        if self.phase == util.DVONN_PLACEMENT:
            self.phase_counter = self.phase_counter + 1
            if self.phase_counter > DVONN_PIECE_COUNT:
                self.phase = util.PLACEMENT
        elif self.phase == util.PLACEMENT:
            self.phase_counter = self.phase_counter + 1
            if self.phase_counter > OTHER_PIECE_COUNT:
                self.phase = util.STACKING
                #white always moves first during stacking
                self.current = 1  
                self.set_player()

    def set_player(self):
        self.player = self.players[self.current]

        

class Game:
    def __init__(self,screen,clock,white_control,
                 black_control,placement):
        self.screen = screen
        self.clock = clock
        self.buttons = []
        self.quit = 0
        
        #Create The Backgound
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.clear()

        #set up the buttons
        #self.add_button("New",self.do_standard_setup, (700, 20))
        self.add_button("Quit",self.do_quit, (700,300))
        
        #set up other objects
        self.board = board.Board()
        self.turn = Turn()
        if placement == util.FIXED:
            self.board.standard_setup()
            self.turn.phase = util.STACKING

        if white_control == util.AI:
            self.white_control = ai.AI(util.WHITE,self.board)
        else:
            self.white_control = None
        if black_control == util.AI:
            self.black_control = ai.AI(util.BLACK,self.board)
        else:
            self.black_control = None

    def ai_turn(self):
        return (self.white_control is not None and \
                self.turn.player == util.WHITE) \
               or \
               (self.black_control is not None and \
                self.turn.player == util.BLACK)
    
    def run(self):

        in_ai_move = 0
        ai_counter = 0
        while not self.quit:
            self.clock.tick(util.TICK_TIME)
        
            # Gather Events
            pygame.event.pump()
            keystate = pygame.key.get_pressed()
            if keystate[K_ESCAPE] or pygame.event.peek(QUIT):
                break

            for event in pygame.event.get():
                handled_by_button = 0
                for btn in self.buttons:
                    if btn.handle_event(event):
                        handled_by_button = 1
                        break
                
                if event.type is MOUSEBUTTONUP:
                    if not self.ai_turn() and not handled_by_button:
                        if self.board.handle_click(
                                    event.pos, self.turn.player,event.button,
                                    self.turn.phase):
                            self.turn.next()

            if self.turn.phase == util.STACKING and \
               not self.board.has_moves(self.turn.player):
                self.turn.next()

            if not in_ai_move:
                move = None
                if self.white_control is not None and \
                   self.turn.player == util.WHITE:
                    move = self.white_control.get_move(self.turn.phase)
                elif self.black_control is not None and \
                    self.turn.player == util.BLACK:
                     move = self.black_control.get_move(self.turn.phase)
                        
                if move is None:
                    pass
                else:
                    in_ai_move = 1
                    ai_counter = 0
                    if self.turn.phase == util.STACKING:
                        start_id,stop_id = move
                    else:
                        start_id = move
                    self.board.set_selected_by_id(start_id)

            if in_ai_move:
                ai_counter = ai_counter + 1
            if ai_counter == util.AI_WAIT_TIME_PARTIAL:
                if self.turn.phase == util.STACKING:
                    self.board.set_targeted_by_id(stop_id)
                else:
                    if self.turn.phase == util.PLACEMENT:
                        self.board.place_piece(self.board.selected,self.turn.player)
                    elif self.turn.phase == util.DVONN_PLACEMENT:
                        self.board.place_piece(self.board.selected,util.RED)
                    self.turn.next()
                    in_ai_move = 0
                    ai_counter = 0
                
            
            if ai_counter >= util.AI_WAIT_TIME_COMPLETE :
                if self.turn.phase == util.STACKING:
                    self.board.perform_move(self.board.selected,
                                            self.board.targeted)
                    self.turn.next()
                    in_ai_move = 0
                    ai_counter = 0


            self.clear()
            if not (self.board.has_moves(util.BLACK) or
                    self.board.has_moves(util.WHITE)) and \
                    self.turn.phase == util.STACKING:
                self.show_message("Game Over")            
            elif self.turn.phase == util.DVONN_PLACEMENT:
                self.show_message(self.turn.player + " DVONN Placement")
            elif self.turn.phase == util.PLACEMENT:
                self.show_message(self.turn.player + " Placement")
            else:
                self.show_message(self.turn.player)
            self.show_score()

            for btn in self.buttons:
                btn.draw(self.background)
            self.board.draw(self.background)
            self.screen.blit(self.background,(0,0))
            pygame.display.flip()

    def clear(self):
        self.background.fill( util.get_image(util.EMPTY).get_at( (0,0)))
        
    def show_message(self,message):
        text = util.render_font(message)
        textpos = text.get_rect()
        textpos.topleft = MESSAGE_POSITION
        self.background.blit(text,textpos)

    def show_score(self):
        message = "Black: " + str(self.board.get_score(util.BLACK)) + \
                  "  White: " + str(self.board.get_score(util.WHITE))
        text = util.render_font(message)
        textpos = text.get_rect()
        textpos.topleft = SCORE_POSITION
        self.background.blit(text,textpos)
        
    def do_quit(self):
        self.quit = 1

    
    def add_button(self,text,func,pos):
        self.buttons.append(
            button.Button(text,func,pos))
