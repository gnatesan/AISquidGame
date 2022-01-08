import numpy as np
import random
import time
import sys
import os 
from BaseAI import BaseAI
from Grid import Grid
from Utils import manhattan_distance

# TO BE IMPLEMENTED
# 
class PlayerAI(BaseAI):

    def __init__(self) -> None:
        # You may choose to add attributes to your player - up to you!
        super().__init__()
        self.pos = None
        self.player_num = None
    
    def getPosition(self):
        return self.pos

    def setPosition(self, new_position):
        self.pos = new_position 

    def getPlayerNum(self):
        return self.player_num

    def setPlayerNum(self, num):
        self.player_num = num

    def manhattanDistance(self, oppPos, grid : Grid) -> int:
        ans = (self.getPosition()[0] - oppPos[0]) + (self.getPosition()[1] - oppPos[1])
        return ans
    
    def heuristic(self, opponentNum, grid : Grid) -> int:
        oppPos = grid.find(opponentNum)
        possibleMovesSelf = len(grid.get_neighbors(self.pos, only_available = True))
        possibleMovesOpp = len(grid.get_neighbors(oppPos, only_available = True))
        return possibleMovesSelf - possibleMovesOpp

    def maximizeThrow(self, grid : Grid, depth, alpha, beta):
        gridCopy = grid.clone() #make a copy of the grid
        if self.player_num == 1:
            oppNum = 2
        else:
            oppNum = 1
        oppPos = gridCopy.find(oppNum)
        #print("opponent position is ", oppPos)
        openNeighbors = gridCopy.get_neighbors(oppPos, only_available = True)
        (maxChild, maxUtility) = ((-1, -1), -500)
        #if len(openNeighbors) == 1: #terminal test if the opponent has 1 possible move, we throw trap on that cell
        #    print("killed him")
        #    gridCopy = gridCopy.trap(openNeighbors[0]) #add the trap to the grid copy
        #    return (openNeighbors[0], self.heuristic(oppNum, gridCopy))
        #if depth == 5: #terminal test DFS limit of 5
         #   print("depth limit reached,", "opponent position is ", oppPos)
          #  for neighbor in openNeighbors:
            #print("depth is ", depth)
           #     gridCopy2 = grid.clone()
            #    gridCopy2 = gridCopy.trap(neighbor)
             #   utility2 = self.heuristic(oppNum, gridCopy2)
              #  if utility2 > maxUtility:
               #     (maxChild, maxUtility) = (neighbor, utility2)
                #    print("new max utility at leaf node is ", maxUtility, "neighbor is", neighbor)
            #return (maxChild, maxUtility)
        #loop through each open neighboring cell for opponent
        for neighbor in openNeighbors:
            print("depth is ", depth, "opponent position is ", oppPos)
            print("neighbor is ", neighbor, "length is ", len(openNeighbors))
            gridCopy2 = grid.clone()
            gridCopy2 = gridCopy.trap(neighbor)
            chance = 1 - 0.05*(manhattan_distance(neighbor, oppPos))
            (pos, utility) = self.minimizeThrow(gridCopy2, depth + 1, alpha, beta)
            if (utility*chance) > maxUtility:
                #(maxChild, maxUtility) = (pos, utility)
                (maxChild, maxUtility) = (neighbor, utility*chance)
                print("depth is ", depth, "new max utility is ", maxUtility)
            else:
                print("max utility is unchanged")
            if maxUtility >= beta:
                print("PRUNING IN MAX")
                break
            if maxUtility > alpha:
                alpha = maxUtility
        return (maxChild, maxUtility)
                
             
    def minimizeThrow(self, grid : Grid, depth, alpha, beta):
        gridCopy = grid.clone() #make a copy of the grid
        if self.player_num == 1:
            oppNum = 2
        else:
            oppNum = 1
        oppPos = gridCopy.find(oppNum)
        #print("opponent position is ", oppPos)
        openNeighbors = gridCopy.get_neighbors(oppPos, only_available = True)
        if depth == 5: #terminal test DFS limit of 5
            print("opponent position is ", oppPos)
            return (oppPos, self.heuristic(oppNum, gridCopy))
        if len(openNeighbors) == 0: #terminal test if the opponent has 1 possible move, we throw trap on that cell
            #grid.print_grid()
           # gridCopy = gridCopy.trap(openNeighbors[0]) #add the trap to the grid copy
            return (oppPos, self.heuristic(oppNum, gridCopy))
        if len(openNeighbors) == 1: #terminal test if the opponent has 1 possible move, we throw trap on that cell
            gridCopy = gridCopy.trap(openNeighbors[0]) #add the trap to the grid copy
            return (openNeighbors[0], self.heuristic(oppNum, gridCopy))
        (minChild, minUtility) = ((-1, -1), 500)
        #loop through each open neighboring cell for opponent
        for neighbor in openNeighbors:
            print("depth is ", depth, "opponent position is ", oppPos)
            gridCopy = gridCopy.move(neighbor, oppNum)
            chance = 1 - 0.05*(manhattan_distance(neighbor, oppPos)-1)
            (pos, utility) = self.maximizeThrow(gridCopy, depth + 1, alpha, beta)
            if utility < minUtility:
                (minChild, minUtility) = (neighbor, utility)
                #(minChild, minUtility) = (pos, utility)
                print("new min utility is ", minUtility)
            else:
                print("min utility is unchanged")
            if minUtility <= alpha:
                "PRUNING IN MIN"
                break
            if minUtility < beta:
                beta = minUtility
        return (minChild, minUtility) #6,4 5,4 5,3 5,2 6,2

    def getMove(self, grid: Grid) -> tuple:
        if self.player_num == 1:
            oppNum = 2
        else:
            oppNum = 1
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player moves.

        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Trap* actions, 
        taking into account the probabilities of them landing in the positions you believe they'd throw to.

        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
         # find all available moves 
        available_moves = grid.get_neighbors(self.pos, only_available = True)
        if len(available_moves) > 0:
            counter = -100
            for neighbor in available_moves:
                gridCopy = grid.clone()
                gridCopy = gridCopy.move(neighbor, oppNum)
                if self.heuristic(oppNum, gridCopy) > counter:
                    counter = self.heuristic(oppNum, gridCopy)
                    pos = neighbor
            return pos
        return NULL
            
        # make random move
        new_pos = random.choice(available_moves) if available_moves else None

        return new_pos

    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player *WANTS* to throw the trap.
        
        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Move* actions, 
        taking into account the probabilities of it landing in the positions you want. 
        
        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        #if self.player_num == 1:
        #    oppNum = 2
        #else:
        #    oppNum = 1
        #oppPos = grid.find(oppNum)
        #openNeighbors = grid.get_neighbors(oppPos, only_available = True)
        #if len(openNeighbors) > 0:
        #    return random.choice(openNeighbors)
        #return None
        (child, util) = self.maximizeThrow(grid, 0, -10000, 10000)
        return (child[0], child[1])
    
