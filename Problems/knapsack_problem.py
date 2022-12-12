import random, statistics

import numpy as np


class knapsack():
    '''
    Class Implementing the Knapsack problem
    '''
    def __init__(self, N, capacity_percentage):
        '''
        :param N: problem size
        :param capacity_percentage: the knapsack capacity will be computed as total_weight * capacity_percentage
        '''
        self.N = N
        self.capacity_percentage = capacity_percentage

    def setup(self, max=100, weights=None, values=None):
        '''
        Setup the knapsack problem.
        By default weights and values will be set randomly in a range (1, max).
        Set weights and values for a not random setup of the problem.
        :param max: set upper limit for weight and value of an item
        :param weights(list): preset weights
        :param values(list): preset values
        :return:None
        '''
        if weights==None or values==None:
            self.values, self.weights = [random.randint(0, max) for _ in range(self.N)], [random.randint(0, max) for _ in range(self.N)]
        else:
            self.weights, self.values = weights, values
        self.capacity = sum(self.weights) * self.capacity_percentage

    def evaluate(self, solution, verbose=False):
        '''
        Evaluate a solution
        :param solution: candidate solution
        :param verbose: False by default
        :return: value of the solution. -1 if it is invalid.
        '''
        if len(solution) != self.N:
            raise 'solution length different from problem size N'
        if verbose:
            print('candidate solution ', solution)
        sol_weight = np.dot(np.array(solution),np.array(self.weights))
        if sol_weight < self.capacity:
            return np.dot(np.array(solution), np.array(self.values))
        else:
            if verbose:
                print('invalid solution found')
            return -1




