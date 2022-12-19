from Problems.knapsack_problem import knapsack
from GA_Optimization import GA_Optimizer
import math

from qiskit import IBMQ
from GeneticOperators import quantum_genetic_sampling as QGS

# SETUP OF THE PROBLEM
knapsack_size = 5
kn = knapsack(N=knapsack_size, capacity_percentage=0.75)
kn.setup(max=100)

# INITIALIZING GA_OPTIMIZER
GA = GA_Optimizer(problem_size=knapsack_size,  verbose=True)
GA.set_Fitness_Function(kn.evaluate)
quantum_sel = GA.toolbox.register('custom_sel', QGS.qgs, toolbox=GA.toolbox, creator_ind=GA.deap_creator.Individual,
                                  t=3, beta=math.pi/4, iterations=3)

# RUN THE OPTIMIZATION
GA.start_GA(pop_size=5)
GA.optimize( elitism=True, sel=True,  cx=True, mut=True, max_gen=3, max_evals=100, cx_pb=0.8, mut_pb=0.2,
             custom_sel=quantum_sel)
