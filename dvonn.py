import sys
import pygame
from pygame.locals import *
import button
import util
import game

#-------------------------------------------------------------
# Constants
LAUNCH_SCREEN_RECT = Rect(0,0, 300,300)
GAME_SCREEN_RECT = Rect(0, 0, 800, 400)




class Label:
    def __init__(self,text,pos):
        self.text = text
        self.pos = pos
    def draw(self,screen):
        text = util.render_font(self.text)
        textpos = text.get_rect()
        textpos.topleft = self.pos
        screen.blit(text,textpos)
        
        
class Launcher:
    def __init__(self,screen,clock):
        self.screen = screen
        self.clock = clock
        self.buttons = []
        self.labels = []
        self.quit = 0

        #Create The Backgound
        self.background = pygame.Surface(self.screen.get_size())
        self.background = self.background.convert()
        self.clear()

        #do the controls
        self.labels.append( Label("Black", (44,40)))
        self.black_human = self.add_toggle("Human", (100,20))
        self.black_human.on = 1
        self.black_ai = self.add_toggle("Computer", (200,20))
        self.black_human.set_other(self.black_ai)
        self.black_ai.set_other(self.black_human)

        self.labels.append( Label("White", (44,100)))
        self.white_human = self.add_toggle("Human", (100,80))
        self.white_human.on = 1
        self.white_ai = self.add_toggle("Computer", (200,80))
        self.white_human.set_other(self.white_ai)
        self.white_ai.set_other(self.white_human)

        self.labels.append( Label("Placement", (10, 160)))
        self.manual_setup = self.add_toggle("Manual", (100,140))
        self.fixed_setup = self.add_toggle("Fixed", (200, 140))
        self.manual_setup.on = 1
        self.fixed_setup.set_other(self.manual_setup)
        self.manual_setup.set_other(self.fixed_setup)
        
        self.add_button("Quit",self.do_quit, (160,220))
        self.add_button("Launch",self.do_launch, (60,220))
        

    def run(self):
        while not self.quit:
            self.clock.tick(util.TICK_TIME)
        
            # Gather Events
            pygame.event.pump()
            keystate = pygame.key.get_pressed()
            if keystate[K_ESCAPE] or pygame.event.peek(QUIT):
                break

            for event in pygame.event.get():
                for btn in self.buttons:
                    if btn.handle_event(event):
                        break

            self.clear()

            for lbl in self.labels:
                lbl.draw(self.background)
            for btn in self.buttons:
                btn.draw(self.background)
            self.screen.blit(self.background,(0,0))
            pygame.display.flip()

    def add_button(self,text,func,pos):
        self.buttons.append(
            button.Button(text,func,pos))

    def add_toggle(self,text,pos):
        b = button.ToggleButton(text,pos)
        self.buttons.append(b)
        return b
        
    def clear(self):
        self.background.fill( util.get_image(util.EMPTY).get_at( (0,0)))
    def do_quit(self):
        self.quit = 1

    def do_launch(self):
        screen = pygame.display.set_mode(GAME_SCREEN_RECT.size,0)
        if self.white_human.on:
            white_ai = util.HUMAN
        else:
            white_ai = util.AI
        if self.black_human.on:
            black_ai = util.HUMAN
        else:
            black_ai = util.AI
        if self.fixed_setup.on:
            placement = util.FIXED
        else:
            placement = util.MANUAL
        g = game.Game(screen,self.clock,
                      white_ai,black_ai,placement)
        g.run()
        self.screen = pygame.display.set_mode(LAUNCH_SCREEN_RECT.size,0)
        


ABOUT_MESSAGE = \
"""
DVONN FOR ONE
Nick Wieczorek,  2003
Original Game by Kris Burm, 2001
"""

def about():
    print ABOUT_MESSAGE
def main():

    if len(sys.argv) > 1 and \
       sys.argv[1] == "--about":
        about()
        return

    pygame.init()
    screen = pygame.display.set_mode(LAUNCH_SCREEN_RECT.size,0)
    util.initialize()
    pygame.display.set_caption("DVONN for One")
    icon = pygame.transform.scale(util.get_image("icon"),(32,32))
    pygame.display.set_icon(icon)
    clock = pygame.time.Clock()

    l = Launcher(screen,clock)
    l.run()

if __name__ == "__main__":
    main()
