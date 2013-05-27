import board
import util
import random

#PLACEMENT WEIGHTS
EDGE_PLACEMENT_WEIGHT=3.0
NEAR_DVONN_PLACEMENT_WEIGHT=2.0
NEAR_THIS_COLOR_PLACEMENT_WEIGHT=0
NEAR_OTHER_COLOR_PLACEMENT_WEIGHT=2.0

#DVONN PLACEMENT WEIGHTS
DVONN_MIDDLE_WEIGHT=3.0
DVONN_THIS_COLOR_WEIGHT= 2.0
DVONN_OTHER_COLOR_WEIGHT= -3.0
DVONN_OTHER_DVONN_WEIGHT= -6.0

#MOVE WEIGHTS
CAN_MOVE_WEIGHT = 6.0
DEPTH_WEIGHT = 1.0
DEPTH_INVERSE_WEIGHT = 4.0
DVONN_WEIGHT = 3.0
SAME_COLOR_WEIGHT = 0
DISCONNECTED_WEIGHT = 10.0


INITIAL_MAXIMUM_VALUE = -1000
class AI:
    def __init__(self,color,board):
        self.color = color
        if self.color == util.BLACK:
            self.other_color = util.WHITE
        else:
            self.other_color = util.BLACK
        self.board = board

    def get_move(self,phase):
        if phase == util.STACKING:
            return self.get_stacking_move()
        elif phase == util.PLACEMENT or \
           phase == util.DVONN_PLACEMENT:
            return self.get_placement_move(phase)
        return None

    #the move returned is of the form (start_space_id,stop_space_id)
    def get_stacking_move(self):
        spaces = self.board.get_all_moveable_spaces(self.color)
        if spaces == []:
            return None
        maximum_value = INITIAL_MAXIMUM_VALUE
        move_values = []
        for space in spaces:
            moves = self.board.get_moves_for_space(space)
            for move in moves:
                value = self.evaluate_move(space,move)
                if value > maximum_value:
                    maximum_value = value
                move_values.append( (space.id,move.id,value))
        good_moves = []
        for start,stop,value in move_values:
            if value == maximum_value:
                good_moves.append( (start,stop))
        return random.choice(good_moves)

    def get_placement_move(self,phase):
        sps = self.board.get_empty_spaces()
        maximum_value = INITIAL_MAXIMUM_VALUE
        move_values = []
        for sp in sps:
            if phase == util.PLACEMENT:
                value = self.evaluate_placement(sp)
            elif phase == util.DVONN_PLACEMENT:
                value = self.evaluate_dvonn_placement(sp)
            if value > maximum_value:
                maximum_value = value
            move_values.append( (sp.id,value))
        good_moves = []
        for id,value in move_values:
            if value == maximum_value:
                good_moves.append( id)
        return random.choice(good_moves)

    def evaluate_dvonn_placement(self,space):
        value = 0
        adj = self.board.get_adjacent(space)
        value = value + (len(adj) * DVONN_MIDDLE_WEIGHT)
        for a in adj:
            if a.color == self.color:
                value = value + DVONN_THIS_COLOR_WEIGHT
            elif a.color == self.other_color:
                value = value + DVONN_OTHER_COLOR_WEIGHT
            elif a.color == util.RED:
                value = value + DVONN_OTHER_DVONN_WEIGHT
        return value
    
    def evaluate_placement(self,space):    
        value = 0
        adj = self.board.get_adjacent(space)
        value = value + (6 - len(adj) * EDGE_PLACEMENT_WEIGHT)
        for a in adj:
            if a.dvonn:
                value = value + NEAR_DVONN_PLACEMENT_WEIGHT
            if a.color == self.color:
                value = value + NEAR_THIS_COLOR_PLACEMENT_WEIGHT
            elif a.color == self.other_color:
                value = value + NEAR_OTHER_COLOR_PLACEMENT_WEIGHT
        return value

    def evaluate_move(self,start,stop):
        value = 0
        if stop.color == self.other_color:
            #can the target space move
            if self.board.can_move(stop):
                value = value + CAN_MOVE_WEIGHT

            #depth
            value = value + (stop.depth * DEPTH_WEIGHT)
            if stop.depth < 5:
                value = value + ((5 - stop.depth) * DEPTH_INVERSE_WEIGHT)
            
            #has dvonn piece
            if stop.dvonn:
                value = value + DVONN_WEIGHT
        elif stop.color == util.RED:
            value = value + DVONN_WEIGHT
        elif stop.color == self.color:
            value = value + SAME_COLOR_WEIGHT

        #which pieces will be disconnected by this move
        disconnected = self.board.predict_disconnected(start,stop)
        disconnect_this_color = 0
        disconnect_other_color = 0
        for d in disconnected:
            if d.color == self.color:
                disconnect_this_color = disconnect_this_color + d.depth
            elif d.color == self.other_color:
                disconnect_other_color = disconnect_other_color + d.depth

        net_disconnected = disconnect_other_color - disconnect_this_color
        value = value + (DISCONNECTED_WEIGHT * net_disconnected)
        return value
