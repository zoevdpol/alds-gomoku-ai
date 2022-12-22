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

    def fully_expanded(self):
        return len(self.children) is len(self.valid_moves)
        

def findSpotToExpand(gamestate: GameState, last_move: Move, n: gamestatenode):
    #random.seed(69)
    if (n.finished == True) or (len(n.valid_moves) == 0): #if n is terminal (game finished)
        return n

    if n.fully_expanded() == False: #if n is not fully expanded
        temp = deepcopy(n.state)
        rmove = random.choice(n.valid_moves)
        #print(rmove)
        _,_,s = play(temp, rmove)
        n.children.append(gamestatenode( s, last_move, n, rmove)) #child in lijst van children van n zetten
        n.valid_moves.remove(rmove)
        #n.children[-1].valid_moves.remove(rmove)
        return n.children[-1]

    best_child = n.children[0]
    maxuct = (best_child.Q / best_child.N) + (0.707 * math.sqrt((2 * math.log(best_child.parent.N, 2)) / best_child.N))

    for ch in n.children:
        uct = (ch.Q / ch.N) + (0.707 * math.sqrt((2 * math.log(ch.parent.N, 2)) / ch.N))
        if uct > maxuct:
            maxuct = uct
            best_child = ch
    n.bestchild = best_child 
    return findSpotToExpand(best_child.state, best_child.last_move, best_child)


def rollout(n: gamestatenode, last_move: Move, black):
    s = deepcopy(n.state)
    #print(n.state)
    moves = valid_moves(s)
    #waarde van checkwin opslaan in de bool
    while not (check_win(s[0], last_move) or (len(moves) <= 0)):
        a = random.choice(moves)
        last_move = a 
        _,_,s = play(s, a)
        moves = valid_moves(s)

    if check_win(s[0], last_move) == False and len(moves) == 0:
        return 0.5
      
    if (check_win(s[0], last_move) == True) and  ((s[1] % 2) == 0 ):
        if not black:
            return 1
        else:
            return 0
    
    if (check_win(s[0], last_move) == True) and ((s[1] % 2) != 0):
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
        print("Val: ", val)
        print("N.Q: ", n.Q)
        print("N.N: ", n.N)
        print("PLY: ", n.state[1])

        n = n.parent

class random_dummy_player:
    """This class specifies a player that just does random moves.
    The use of this class is two-fold: 1) You can use it as a base random roll-out policy.
    2) it specifies the required methods that will be used by the competition to run
    your player
    """

    def __init__(self, black_: bool = True):
        """Constructor for the player."""
        self.black = black_

    def new_game(self, black_: bool):
        """At the start of each new game you will be notified by the competition.
        this method has a boolean parameter that informs your agent whether you
        will play black or white.
        """
        self.black = black_


    def move(
        self, state: GameState, last_move: Move, max_time_to_move: int = 1000
    ) -> Move:
        """This is the most important method: the agent will get:
        1) the current state of the game
        2) the last move by the opponent
        3) the available moves you can play (this is a special service we provide ;-) )
        4) the maximum time until the agent is required to make a move in milliseconds [diverging from this will lead to disqualification].
        """

       
        
        node = gamestatenode(state, last_move, None)
        starttime = time.time()
        while time.time() < starttime + 1:
            nleaf = findSpotToExpand(state, last_move, node)

            value = rollout(nleaf, last_move, self.black)
            Backupvalue(nleaf, value, self.black)


        best_child = node.children[0]
        maxuct = best_child.Q / best_child.N
        for ch in node.children:
            uct = (ch.Q / ch.N) 
            # print("CHILDREN: ", ch.move)
            # print("UCT: ", uct)
            # print("Q: ", ch.Q)
            # print("N: ", ch.N)
            if uct > maxuct:
                #print("MOVE: ", ch.move)
                maxuct = uct
                best_child = ch
        node.bestchild = best_child 
        return best_child.move
        
        

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "random_player"
