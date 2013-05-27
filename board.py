import pygame
from pygame.locals import *
import string
import util

ROW_RANGE = [5,4,3,2,1]
COL_RANGE = ["A","B","C","D","E","F","G","H","I","J","K"]
INITIAL_TOP = 20
INITIAL_LEFT = 20
INITIAL_LEFT_MULT = (1.0,0.5,0,0.5,1.0)


#standard setup
STANDARD_RED = ["3F","4I","2C"]
STANDARD_BLACK = ["1A","1C","1E","1G","1I",
                  "5D","5F","5H","5J",
                  "4B","4D","4F","4H","4K",
                  "3B","3D","3G","3I","3K",
                  "2B","2E","2G","2I"]
STANDARD_WHITE = ["1B","1D","1F","1H",
                  "5C","5E","5G","5I","5K",
                  "4C","4E","4G","4J",
                  "3A","3C","3E","3H","3J",
                  "2A","2D","2F","2H","2J"]

def get_up_col(col,distance=1):
    
    new_index = COL_RANGE.index(col) + distance
    if new_index >= 0 and new_index < len(COL_RANGE):
        up_col = COL_RANGE[new_index]
    else:
        up_col = "error"
    return up_col

def get_down_col(col,distance=1):
    return get_up_col(col,distance * -1)


class Board:
    def __init__(self):
        self.spaces = {}
        tempImgRect = util.get_image(util.EMPTY).get_rect()
        top = INITIAL_TOP
        for row in ROW_RANGE:
            left = INITIAL_LEFT + (INITIAL_LEFT_MULT[row - 1] * tempImgRect.width)
            for col in COL_RANGE:
                if ((row == 5 and col in ("A","B")) or
                    (row == 4 and col == "A") or
                    (row == 2 and col == "K") or
                    (row == 1 and col in ("J","K"))):
                    continue
                
                id = str(row) + col
                s = Space(id, (left,top))
                self.spaces[id] = s
                left = left + tempImgRect.width
            top = top + tempImgRect.height
        self.selected = None
        self.targeted = None
        self.is_valid_id = self.spaces.has_key
        self.all_spaces = self.spaces.values()

    def set_selected_by_id(self,id):
        self.selected = self.spaces[id]
    def set_targeted_by_id(self,id):
        self.targeted = self.spaces[id]
        
    def standard_setup(self):
        for s in self.all_spaces:
            s.dvonn = 0
            s.depth = 0
            s.set_color(util.EMPTY)
            if s.id in STANDARD_RED:
                s.set_color(util.RED)
                s.depth = 1
                s.dvonn = 1
            elif s.id in STANDARD_BLACK:
                s.set_color(util.BLACK)
                s.depth = 1
            elif s.id in STANDARD_WHITE:
                s.set_color(util.WHITE)
                s.depth = 1

    def draw(self,screen):
        for s in self.all_spaces:
            s.draw(s == self.selected,s == self.targeted, screen)

    #returns true is a move was made
    def handle_click(self,point,player,button,phase):
        for s in self.all_spaces:
            if s.handle_click(point,player):
                #print s.id
                if button == util.M_LEFT:
                    if phase == util.DVONN_PLACEMENT:
                        if s.depth == 0:
                            self.place_piece(s,util.RED)
                            return 1
                    elif phase == util.PLACEMENT:
                        if s.depth == 0:
                            self.place_piece(s,player)
                            return 1
                    elif phase == util.STACKING:
                        if ((s.color == util.BLACK or
                             s.color == util.WHITE) and
                            s.color == player):
                            if self.can_move(s):
                                self.selected = s   
                elif button == util.M_RIGHT and phase == util.STACKING:
                    if self.selected is not None:
                        if self.is_legal_move(self.selected,s):
                            self.perform_move(self.selected,s)
                            return 1
        return 0

        
    def place_piece(self,space,color):
        if color == util.RED:
            space.set_color(util.RED)
            space.depth = 1
            space.dvonn = 1
        else:
            space.set_color(color)
            space.depth = 1
        self.selected = None

    def perform_move(self,start,stop):
        self.perform_piece_move(start,stop)
        self.board_reset()
    
    def board_reset(self):
        #clear color
        self.selected = None
        self.targeted = None
        #remove disconnected
        self.remove_disconnected()
        
    def perform_piece_move(self,start,stop):
        #set up destination stack
        stop.depth = stop.depth + start.depth
        stop.set_color(start.color)
        if start.dvonn:
            stop.dvonn = 1
        #set up empty space
        start.depth = 0
        start.set_color(util.EMPTY)
        start.dvonn = 0
        

    #predict which pieces will be removed after a move is made from start to stop
    def predict_disconnected(self,start,stop):
        start_saver = SpaceSaver(start)
        stop_saver = SpaceSaver(stop)

        self.perform_piece_move(start,stop)
        disconnected = self.get_disconnected()

        start_saver.restore(start)
        stop_saver.restore(stop)
        return disconnected
        
    def get_disconnected(self):
        for s in self.all_spaces:
            s.safe = 0
        process_queue = []
        for s in self.all_spaces:
            if s.dvonn:
                s.safe = 1
                process_queue.append(s)

        while len(process_queue) > 0:
            current = process_queue.pop()
            adj = self.get_adjacent(current)
            for s in adj:
                if (s.color != util.EMPTY and
                    not s.safe):
                    s.safe = 1
                    process_queue.append(s)

        disconnected = []
        for s in self.all_spaces:
            if not (s.color == util.EMPTY or s.safe):
                disconnected.append(s)
        return disconnected
        
    def remove_disconnected(self):
        for s in self.get_disconnected():
            s.set_color(util.EMPTY)
            s.depth = 0
    
    def get_distance(self,start,stop):
        if start.col == stop.col:
            distance = abs(start.row - stop.row)
        elif start.row == stop.row:
            distance = abs(COL_RANGE.index(start.col) -
                           COL_RANGE.index(stop.col))
        else:
            row_dist = start.row - stop.row
            col_dist = (COL_RANGE.index(start.col) -
                           COL_RANGE.index(stop.col))
            if row_dist == col_dist:
                distance = abs(col_dist)
            else:
                distance = -1
        return distance

    #return a list of adjacent spaces          
    def get_adjacent(self,space):
        ids = []
        up_col = get_up_col(space.col)
        down_col = get_down_col(space.col)
        for i in range(6):
            if i == 0:
                id = str(space.row - 1) + space.col
            elif i == 1:
                id = str(space.row + 1) + space.col
            elif i == 2:
                id = str(space.row) + down_col
            elif i == 3:
                id = str(space.row) + up_col
            elif i == 4:
                id = str(space.row - 1) + down_col
            elif i == 5:
                id = str(space.row + 1) + up_col
                
            if self.is_valid_id(id):
                ids.append(id)
        adj = []
        for id in ids:
            adj.append(self.spaces[id])
        return adj

    #return a list of all empty spaces on the board
    def get_empty_spaces(self):
        sps = []
        for s in self.all_spaces:
            if s.depth == 0:
                sps.append(s)
        return sps
    
    #may return an invalid ids
    def translate_id(self,id,direction,distance):
        row = string.atoi(id[0])
        col = id[1]
        if direction == util.LEFT:
            col = get_down_col(col,distance)
        elif direction == util.RIGHT:
            col = get_up_col(col,distance)
        elif direction == util.UP_LEFT:
            row = row + distance
        elif direction == util.UP_RIGHT:
            col = get_up_col(col,distance)
            row = row + distance
        elif direction == util.DOWN_LEFT:
            col = get_down_col(col,distance)
            row = row - distance
        elif direction == util.DOWN_RIGHT:
            row = row - distance
        return str(row) + col

    def is_space_open(self,space):
        adj = self.get_adjacent(space)
        if len(adj) < 6:
            return 1
        open = 0
        for s in adj:
            if s.depth == 0:
                open = 1
                break
        return open
            
    def is_legal_move(self,start,stop):
        distance = self.get_distance(start,stop)
        space_open = self.is_space_open(start)
        if (distance == start.depth and
            stop.depth > 0 and
            space_open):
            return 1
        #print "illegal:",distance,stop.depth,space_open
        return 0

    def get_score(self,color):
        count = 0
        for s in self.all_spaces:
            if s.color == color:
                count = count + s.depth
        return count

    # does the player have any legal moves
    def has_moves(self,player):
        has_moves = 0
        for s in self.all_spaces:
            if s.color == player:
                if self.can_move(s):
                    has_moves = 1
                    break
        return has_moves

    #does the stack in the space have a legal move
    def can_move(self,space):
        if space.depth == 0 or space.color == util.EMPTY:
            return 0
        if not self.is_space_open(space):
            return 0
        if space.depth == 1:
            #always have a move, otherwise they would be disconnected
            return 1
        has_move = 0
        for direction in util.ALL_DIRECTIONS:
            id = self.translate_id(space.id,direction,space.depth)
            if self.is_valid_id(id) and \
               self.spaces[ id ].depth > 0:
                has_move = 1
                break
        
        return has_move

    #get all spaces that can move for this player
    def get_all_moveable_spaces(self,player):
        spaces = []
        for s in self.all_spaces:
            if s.color == player:
                if self.can_move(s):
                    spaces.append(s)
        return spaces


    #get all legal moves for this space
    def get_moves_for_space(self,space):
        moves = []
        if self.is_space_open(space):
            for direction in util.ALL_DIRECTIONS:
                id = self.translate_id(space.id, direction, space.depth)
                if self.is_valid_id(id) and\
                   self.spaces[id].depth > 0:
                    moves.append(self.spaces[id])
        return moves

class SpaceSaver:
    def __init__(self,space):
        self.color = space.color
        self.depth = space.depth
        self.dvonn = space.dvonn

    def restore(self,space):
        space.set_color(self.color)
        space.depth = self.depth
        space.dvonn = self.dvonn
        
        
class Space:
    def __init__(self, id, topleft):
        self.id = id
        self.row = string.atoi(id[0])
        self.col = id[1]
        self.set_color(util.EMPTY)
        self.depth = 0
        self.rect = self.image.get_rect()
        self.highlight = util.get_image(util.HIGHLIGHT)
        self.target = util.get_image(util.TARGET)
        self.dvonn_marker = util.get_image(util.DVONN)
        self.rect.topleft = topleft
        self.dvonn = 0

    def set_color(self,color):
        self.color = color
        self.image = util.get_image(self.color)
        
    def draw(self,selected,targeted,screen):
        #draw top piece
        screen.blit(self.image, self.rect)
        #draw highlight
        if selected:
            screen.blit(self.highlight,self.rect)
        if targeted:
            screen.blit(self.target, self.rect)
        #mark if there is a hidden dvonn piece in the stack
        if self.dvonn and self.color != util.RED:
            screen.blit(self.dvonn_marker,self.rect)
        #draw stack depth
        if self.depth > 0:
            text = util.render_font(str(self.depth))
            textpos = text.get_rect()
            textpos.center = self.rect.center
            screen.blit(text,textpos)

    def handle_click(self,point,player):
        x,y = point
        return self.rect.collidepoint(x,y)
                
    def __repr__(self):
        return "[" + self.id + "]"

def main():
    b = Board()
    print b.spaces
    
if __name__ == "__main__":
    main()
