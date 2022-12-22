import random
import gomoku
import math
import time
from copy import deepcopy
from gomoku import Board, Move, GameState, check_win, valid_moves
from gomoku import move as play


class gamestatenode:
    def __init__(self, gamestate, last_move, parentnode = None, move = None):
        self.children = []
        self.state = deepcopy(gamestate)
        self.parent = parentnode
        self.Q = 0  # number of wins
        self.N = 0  # number of visits
        self.last_move = last_move
        self.finished = check_win(self.state[0], move) #anders last_move, this no work want gamestate
        self.valid_moves = valid_moves(self.state)
        self.bestchild = 0 
        self.move = move 
        self.countpmoves = len(self.valid_moves)     

    def fully_expanded(self):
        return len(self.children) is self.countpmoves
        

def findSpotToExpand(gamestate: GameState, last_move: Move, n: gamestatenode):
    if (n.finished == True) or (n.countpmoves == 0): #if n is terminal (game finished)
        return n

    if n.fully_expanded() == False: #if n is not fully expanded
        temp = deepcopy(n.state)
        rmove = random.choice(n.valid_moves)
        #print(rmove)
        _,_,temp = play(temp, rmove)
        n.children.append(gamestatenode( temp, n.move, n, rmove)) #child in lijst van children van n zetten
        n.valid_moves.remove(rmove)
        return n.children[-1]

    best_child = n.children[0]
    maxuct = (best_child.Q / best_child.N) + (0.707 * math.sqrt((2 * math.log(best_child.parent.N, 2)) / best_child.N))

    for ch in n.children:
        uct = (ch.Q / ch.N) + (0.707 * math.sqrt((2 * math.log(ch.parent.N, 2)) / ch.N))
        if uct > maxuct:
            maxuct = uct
            best_child = ch
    n.bestchild = best_child 
    return findSpotToExpand(best_child.state, best_child.move, best_child) #maybe move beter


def rollout(n: gamestatenode, last_move: Move, black):
    s = deepcopy(n.state)
    boolwin = check_win(s[0], last_move)
    moves = valid_moves(s)

    while not ((boolwin) or (len(moves) <= 0)):
        a = random.choice(moves)
        last_move = a 
        _,_,s = play(s, a)
        moves = valid_moves(s)
        boolwin = check_win(s[0], last_move)

    if (boolwin == False) and len(moves) == 0:
        return 0.5
      
    if (boolwin == True) and  ((s[1] % 2) == 0 ):
        if not black:
            return 1
        else:
            return 0
    
    if (boolwin == True) and ((s[1] % 2) != 0):
        if not black:
            return 0
        else:
            return 1
    

def Backupvalue(n, val, black):
    while n is not None:
        n.N = n.N + 1
        if n.state[1] % 2 != 0:
            if black:
                n.Q = n.Q + val 
            else:
                n.Q = n.Q - val
        else:
            if not black:
                n.Q = n.Q + val
            else:
                n.Q = n.Q - val
        n = n.parent

class random_dummy_player:
    def __init__(self, black_: bool = True):
        self.black = black_

    def new_game(self, black_: bool):
        self.black = black_


    def move(
        self, state: GameState, last_move: Move, max_time_to_move: int = 1000
    ) -> Move:
        node = gamestatenode(state, last_move, None)
        starttime = time.time()
        ding_count = 0
        while time.time() < starttime + 10:
            nleaf = findSpotToExpand(state, last_move, node)
            value = rollout(nleaf, last_move, self.black)
            Backupvalue(nleaf, value, self.black)
            ding_count += 1

        best_child = node.children[0]
        maxuct = best_child.Q / best_child.N
        for ch in node.children:
            uct = (ch.Q / ch.N) 
            print("MOVE: ",ch.move," UCT: ",uct)
            print("Q: ", ch.Q)
            print("N: ", ch.N)
            print("                                                                     ")
            if uct > maxuct:
                maxuct = uct
                best_child = ch
        node.bestchild = best_child 
        print(ding_count)
        return best_child.move
        
        

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "random_player"
