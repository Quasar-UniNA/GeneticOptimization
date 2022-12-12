from Problems.knapsack_problem import knapsack
from GA_Optimization import GA_Optimizer
import random
from deap import tools

kn = knapsack(N=10, capacity_percentage=0.75)
kn.setup(max=100)

def two_point(offspring, cx_pb):
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < cx_pb:
            tools.cxTwoPoint(child1, child2)
            del child1.fitness.values
            del child2.fitness.values



#roulette_sel = tools.selRoulette()
GA = GA_Optimizer(problem_size=10,  verbose=True)
roul_sel = GA.toolbox.register('custom_sel', tools.selRoulette)
GA.set_Fitness_Function(kn.evaluate)
two_point = GA.toolbox.register('custom_cx', two_point, cx_pb=0.9)
GA.start_GA(pop_size=10)
GA.optimize(n_gen=100, elitism=True, sel=True,  cx=True, mut=True, mut_pb=0.7, custom_cx=two_point)

