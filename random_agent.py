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
        self.checkselfwon = check_win(self.state[0], self.move) 

    def fully_expanded(self):
        return len(self.children) is self.countpmoves
    
    


def findSpotToExpand(n: gamestatenode):
    if (n.finished == True) or (n.countpmoves == 0): #if n is terminal (game finished)
        return n

    if n.fully_expanded() == False: #if n is not fully expanded
        temp = deepcopy(n.state) #kopie maken van state zodat we hem niet oprecht aanpassen
        rmove = random.choice(n.valid_moves) #random move kiezen
        _,_,temp = play(temp, rmove) #kopie van gamestate veranderen door de random move te spelen
        n.children.append(gamestatenode( temp, n.move, n, rmove)) #child maken en in lijst van children van n zetten
        n.valid_moves.remove(rmove) #move uit random moves halen
        return n.children[-1] #hoogste kind returnen

    best_child = n.children[0] 
    maxuct = (best_child.Q / best_child.N) + (0.707 * math.sqrt((2 * math.log(best_child.parent.N, 2)) / best_child.N)) 

    for ch in n.children: #door alle kinderen heen van n
        uct = (ch.Q / ch.N) + (0.707 * math.sqrt((2 * math.log(ch.parent.N, 2)) / ch.N)) #uct waarde berekenen
        if uct > maxuct: #hoogste uct waarde eruit halen
            maxuct = uct
            best_child = ch

    n.bestchild = best_child  #beste kind van n in n zetten 
    return findSpotToExpand(best_child) #weer kijken waar we kunnen expanden bij bestchild


def rollout(n: gamestatenode, last_move: Move, black): 
    s = deepcopy(n.state) #kopie van state maken
    boolwin = check_win(s[0], last_move) 
    Validmoves = valid_moves(s)

    while not ((boolwin) or (len(Validmoves) <= 0)): #geen terminal moves (geen winnende move en lengte van validmoves is nog hoger dan 0)
        a = random.choice(Validmoves) #random move uitkiezen
        last_move = a 
        _,_,s = play(s, a) #random move spelen 
        Validmoves = valid_moves(s) #validmoves lijst weer updaten
        boolwin = check_win(s[0], last_move) #checkwin weer updaten

    if (boolwin == False) and len(Validmoves) == 0: #gelijkspelen
        return 0
      
    if (boolwin == True) and  ((s[1] % 2) == 0 ): 
        if not black: 
            return 1 #win
        else:
            return -1 #verlies
    
    if (boolwin == True) and ((s[1] % 2) != 0):
        if not black:
            return -1 #verlies
        else:
            return 1 #win
    

def Backupvalue(n, val, black):
    while n is not None: #zolang we niet bij de root zijn
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


    def move(self, state: GameState, last_move: Move, max_time_to_move: int = 1000) -> Move:
        rootnode = gamestatenode(state, last_move, None)
        starttime = time.time()
        while time.time() < starttime + 1: #zolang de tijd niet 0 is
            nleaf = findSpotToExpand(rootnode) #nlead maken
            value = rollout(nleaf, last_move, self.black) #waarde van nleaf berekenen
            Backupvalue(nleaf, value, self.black) #backupvalues berekenen
            
        best_child = rootnode.children[0]
        maxuct = best_child.Q / best_child.N 
        for ch in rootnode.children: #door alle children van de rootnode
            if ch.checkselfwon == True: #als ik gewonnen heb met de volgende move dan die altijd spelen
                return ch.move
            uct = (ch.Q / ch.N) 
            if uct > maxuct: #anders gewoon de child met de beste uct waarde pakken en de move daarvan berekenen
                maxuct = uct
                best_child = ch
        rootnode.bestchild = best_child 
        return best_child.move
        
        

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "random_player"
