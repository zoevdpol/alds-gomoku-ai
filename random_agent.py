import random
import gomoku
import math
import time
from copy import deepcopy
from gomoku import Board, Move, GameState, check_win, valid_moves
from gomoku import move as play

#class node
# children list, N counter number visited, Q value, parent
moves_played = []

class gamestatenode:
    def __init__(self, gamestate, move, parentnode = None):
        self.children = []
        self.state = deepcopy(gamestate)
        self.parent = parentnode
        self.last_move = moves_played[-1]
        self.Q = 0  # number of wins
        self.N = 0  # number of visits
        self.finished = check_win(self.state[0], self.last_move) #this no work want gamestate
        self.valid_moves = valid_moves(self.state)
        self.bestchild = 0 
        self.move = move      

    def fully_expanded(self):
        return len(self.children) is len(self.valid_moves)
        

def findSpotToExpand(gamestate: GameState, last_move: Move, n: gamestatenode):
    maxuct = 0
    if (check_win(gamestate[0], last_move ) == True) or (len(valid_moves(gamestate)) == 0): #if n is terminal (game finished)
        return n

    if n.fully_expanded() == False: #if n is not fully expanded
        rmove = random.choice(n.valid_moves)
         #child node aanmaken met n als parent
        n.children.append(gamestatenode( gamestate, rmove, n)) #child in lijst van children van n zetten
        return n.children[-1]
    print("idk")
    best_child = n.children[0]
    for ch in n.children:
        uct = (ch.Q / ch.N) + 0.707 * math.sqrt(2 * math.log(ch.parent.N) / ch.N)
        if uct > maxuct:
            maxuct = uct
            best_child = ch
    n.bestchild = best_child 
    return findSpotToExpand(gamestate, last_move, best_child)


def rollout(n: gamestatenode, state, last_move: Move):
    s = deepcopy(state)
    while not (check_win(s[0], last_move) or (len(valid_moves(s)) <= 0)):
 
        moves = valid_moves(s)

        a = random.choice(moves)
        last_move = a 
        _,_,s = play(s, a)
    if check_win(s[0], last_move) == False and len(valid_moves(s)) == 0:
        return 0.5
        
    if (check_win(s[0], last_move) == True) and  ((s[1] % 2) == 0 ):
        return 1
    if (check_win(s[0], last_move) == True) and ((s[1] % 2) != 0):
        return 0
    else:

        return 5

def Backupvalue(n, val):
    while n is not None:
        n.N = n.N + 1
        if n.state[1] % 2 != 0:
            n.Q = n.Q - val
        else:
            n.Q = n.Q + val
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

        moves_played.append(last_move)
            
        node = gamestatenode(state, None)
        starttime = time.time()
        while time.time() < starttime + 15:
            nleaf = findSpotToExpand(state, last_move, node)

            value = rollout(nleaf, state, last_move)
            Backupvalue(nleaf, value)

        maxuct = 0

        best_child = node.children[0]
        for ch in node.children:
            uct = (ch.Q / ch.N) + 0.707 * math.sqrt(2 * math.log(ch.parent.N) / ch.N)
            if uct > maxuct:
                maxuct = uct
                best_child = ch
        node.bestchild = best_child 

        return node.bestchild.move
        # print(findSpotToExpand(state, last_move, node).state)
        # rollout(node, state, last_move)
        # Backupvalue
        # moves = gomoku.valid_moves(state)
        # #print(moves_played)
        # return random.choice(moves)

    def id(self) -> str:
        """Please return a string here that uniquely identifies your submission e.g., "name (student_id)" """
        return "random_player"
