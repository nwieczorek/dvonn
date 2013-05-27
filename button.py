import pygame
from pygame.locals import *
import util


class Button:
    def __init__(self,text,func,topleft):
        self.text = text
        self.func = func
        self.image = util.get_image(util.BUTTON)
        self.pushed_image = util.get_image(util.PUSHED_BUTTON)
        self.rect = self.image.get_rect()
        self.rect.topleft = topleft
        self.pushed = 0
        
    def draw(self,screen):
        self.draw_background(screen)
        self.draw_text(screen)
        
    def draw_background(self,screen):
        if self.pushed:
            i = self.pushed_image
        else:
            i = self.image
        screen.blit(i,self.rect)

    def draw_text(self,screen):
        t = util.render_font(self.text)
        textpos = t.get_rect()
        textpos.center = self.rect.center
        screen.blit(t,textpos)


    def is_within(self,point):
        x,y = point
        if self.rect.collidepoint(x,y):
            return 1
        return 0
        
    def handle_event(self,event):
        handled =0
        if event.type is MOUSEBUTTONUP:
            self.pushed = 0
            if self.is_within(event.pos):
                self.func()
                handled = 1
        elif event.type is MOUSEBUTTONDOWN:
            if self.is_within(event.pos):
                self.pushed = 1
            
        return handled



class ToggleButton(Button):
    def __init__(self,text,topleft):
        Button.__init__(self,text,self.toggle,topleft)
        self.on = 0

    def set_other(self,other):
        self.other = other
        
    def toggle(self):
        if not self.on:
            self.on = 1
            self.other.on = 0

    def draw_text(self,screen):
        if self.on:
            t = util.render_font(self.text,util.HIGHLIGHT_COLOR)
        else:
            t = util.render_font(self.text,util.OFF_COLOR)            
        textpos = t.get_rect()
        textpos.center = self.rect.center
        screen.blit(t,textpos)
        
