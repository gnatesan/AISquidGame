import numpy as np
import random
import time
import sys
import os 
from BaseAI import BaseAI
from Grid import Grid
from Utils import manhattan_distance

# TO BE IMPLEMENTED
MAX_SEARCH_DEPTH = 5
MAX, MIN = 10000, -10000
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

    def move_utility(self, grid: Grid):
        opp_pos = grid.find(3 - self.getPlayerNum())
        num_possible_moves_self = len(grid.get_neighbors(self.pos, only_available=True))
        num_possible_moves_opp = len(grid.get_neighbors(opp_pos, only_available=True))
        return num_possible_moves_self - num_possible_moves_opp

    #heuristic for trap
    def heuristic(self, opponentNum, grid : Grid) -> int:
        gridCopy = grid.clone() 
        oppPos = grid.find(opponentNum)
        possibleMovesSelf = len(grid.get_neighbors(self.pos, only_available = True))
        possibleMovesOpp = len(grid.get_neighbors(oppPos, only_available = True))
        centerFactor = manhattan_distance((3, 3), oppPos) #prioritize moving the opponent further away from center cell 
        openNeighbors = gridCopy.get_neighbors(oppPos, only_available = True)
        two_moves_ahead = set() 
        for neighbor in openNeighbors: #look at available neighbors two moves ahead
            for neighbor_2 in gridCopy.get_neighbors(neighbor, only_available=True):
                two_moves_ahead.add(neighbor_2)
        ans = len(two_moves_ahead)
        return (possibleMovesSelf - possibleMovesOpp) * 0.55 + (centerFactor) * 0.20 + ans * 0.375 * 0.25

    def maximizeThrow(self, grid : Grid, depth, alpha, beta):
        gridCopy = grid.clone() #make a copy of the grid
        if self.player_num == 1:
            oppNum = 2
        else:
            oppNum = 1
        oppPos = gridCopy.find(oppNum)
        openNeighbors = gridCopy.get_neighbors(oppPos, only_available = True)
        (maxChild, maxUtility) = ((-1, -1), -500)
        #loop through each open neighboring cell for opponent
        if len(openNeighbors) == 0:
            return (oppPos, self.heuristic(oppNum, grid))
        for neighbor in openNeighbors:
            gridCopy2 = grid.clone()
            gridCopy2 = gridCopy.trap(neighbor)
            chance = 1 - 0.05*(manhattan_distance(neighbor, oppPos))
            (pos, utility) = self.minimizeThrow(gridCopy2, depth + 1, alpha, beta)
            if (utility*chance) > maxUtility:
                (maxChild, maxUtility) = (neighbor, utility*chance)
            if maxUtility >= beta:
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
        openNeighbors = gridCopy.get_neighbors(oppPos, only_available = True)
        if depth == 5: #terminal test DFS limit of 5
            return (oppPos, self.heuristic(oppNum, gridCopy))
        if len(openNeighbors) == 0: #terminal test if the opponent has 1 possible move, we throw trap on that cell
            return (oppPos, self.heuristic(oppNum, gridCopy))
        if len(openNeighbors) == 1: #terminal test if the opponent has 1 possible move, we throw trap on that cell
            gridCopy = gridCopy.trap(openNeighbors[0]) #add the trap to the grid copy
            return (openNeighbors[0], self.heuristic(oppNum, gridCopy))
        (minChild, minUtility) = ((-1, -1), 500)
        #loop through each open neighboring cell for opponent
        for neighbor in openNeighbors:
            gridCopy = gridCopy.move(neighbor, oppNum)
            chance = 1 - 0.05*(manhattan_distance(neighbor, oppPos)-1)
            (pos, utility) = self.maximizeThrow(gridCopy, depth + 1, alpha, beta)
            if utility < minUtility:
                (minChild, minUtility) = (neighbor, utility)
            if minUtility <= alpha:
                "PRUNING IN MIN"
                break
            if minUtility < beta:
                beta = minUtility
        return (minChild, minUtility) #6,4 5,4 5,3 5,2 6,2

    def getMove(self, grid: Grid) -> tuple:
        # make sure that you account for being either number
        return self.move_expectiminimax(0, grid, True, MIN, MAX)[0]

    def move_expectiminimax(self, depth, grid: Grid, maximizing, alpha, beta):
        if depth == MAX_SEARCH_DEPTH:  # need to implement time check of 5 seconds?
            return grid.find(self.getPlayerNum()), self.move_utility(grid)  # return tuple of (position, heuristic)
        if maximizing:  # maximizing recursion
            best_so_far = grid.find(self.getPlayerNum()), MIN
            # Recurse for available squares around playerAI
            for pos in grid.get_neighbors(self.getPosition(), True):
                possible_move = grid.clone().move(pos, self.getPlayerNum())  # clone grid, and move player
                val = self.move_expectiminimax(depth + 1, possible_move, False, alpha, beta)
                best_so_far = best_so_far if best_so_far[1] > val[1] else val
                alpha = max(best_so_far[1], alpha)
                if beta <= alpha:
                    break
            return best_so_far
        else:
            best_so_far = grid.find(self.getPlayerNum()), MAX
            for pos in grid.get_neighbors(self.getPosition(), True):
                possible_move = grid.clone().move(pos, self.getPlayerNum())
                throw_accuracy = 1 - 0.05 * (manhattan_distance(pos, grid.find(3 - self.getPlayerNum())))
                val = self.move_expectiminimax(depth + 1, possible_move, True, alpha, beta)
                best_so_far = best_so_far if best_so_far[1] < (throw_accuracy * val[1]) else val
                beta = min(best_so_far[1], beta)
                if beta <= alpha:
                    break
            return best_so_far

    def getTrap(self, grid : Grid) -> tuple:
        """ 
        YOUR CODE GOES HERE

        The function should return a tuple of (x,y) coordinates to which the player *WANTS* to throw the trap.
        
        It should be the result of the ExpectiMinimax algorithm, maximizing over the Opponent's *Move* actions, 
        taking into account the probabilities of it landing in the positions you want. 
        
        Note that you are not required to account for the probabilities of it landing in a different cell.

        You may adjust the input variables as you wish (though it is not necessary). Output has to be (x,y) coordinates.
        
        """
        (child, util) = self.maximizeThrow(grid, 0, -10000, 10000)
        return (child[0], child[1])
    
