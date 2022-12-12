import copy

import numpy,random
from deap import base, creator, tools
from Problems.knapsack_problem import knapsack

class GA_Optimizer():

    """
    Class implementing a Genetic Optimizer based on DEAP
    """
    def __init__(self, problem_size, optimization='max', sel=lambda:None, cx=lambda:None, mut=lambda:None, verbose=False):
        """
        Initialization of Deap Creator, Toolbox and Stats objects.
        By Default, the GA performs a binary optimization. Toolbox object must be adapted to other cases.
        Current Toolbox is initialized with:
            - Tournament Selection
            - OnePoint Crossover
            - BitFlip Mutation
        Other genetic operators can be used by creating the toolbox register 'custom_cx', 'custom_mut' and 'custom_sel'.
        See examples in GA.Optimize() below.
        ...
        :param problem_size: (int) Size of the problem
        :param optimization: (Str) 'min' or 'max' for Minimization or Maximization - 'max' default
        :param verbose: (Bool) Default False, set True for displaying the evolution.
        ...
        """
        self.cx = cx
        self.mut = mut
        self.sel = sel
        self.verbose = verbose
        self.N = problem_size
        self.deap_creator = creator
        self.toolbox = base.Toolbox()
        ### creator init ###
        if optimization == 'max':
            self.deap_creator.create('FitnessMax', base.Fitness, weights=(1.0,))
        elif optimization == 'min':
            self.deap_creator.create('FitnessMin', base.Fitness, weights=(-1.0,))
        else:
            raise "please indicate optimization 'max' or 'min' for maximization or minimization problems respectively"

        self.deap_creator.create('Individual', list, fitness=self.deap_creator.FitnessMax)

        ### toolbox init ###

        self.toolbox.register('attr_float', lambda: random.randint(0, 1))
        # Ind Register
        self.toolbox.register('individual', tools.initRepeat, self.deap_creator.Individual, self.toolbox.attr_float, n=self.N)
        # Pop Register
        self.toolbox.register('population', tools.initRepeat, list, self.toolbox.individual)
        # Crossover Operator
        self.toolbox.register('one_point', tools.cxOnePoint) #Default
        self.toolbox.register('custom_cx', self.cx)
        # Mutation
        self.toolbox.register('mutate', tools.mutFlipBit, indpb=1) #Default
        self.toolbox.register('custom_mut', self.mut)

        # Selection
        self.toolbox.register('select_TS', tools.selTournament, tournsize=3) #Default
        self.toolbox.register('custom_sel', self.sel)


        ### Stats Collector ###
        self.stats = tools.Statistics(key=lambda ind: ind.fitness.values)
        self.stats.register("avg", numpy.mean)
        self.stats.register("std", numpy.std)
        self.stats.register("min", numpy.min)
        self.stats.register("max", numpy.max)

        # Defining the Logbook
        self.logbook = tools.Logbook()
        self.logbook.header = ["gen", "nevals"] + (self.stats.fields) + ["best"]

        # HOF
        self.hof = tools.HallOfFame(1)

    def set_Fitness_Function(self, fitness):
        """
        Define fitness function for the optimization
        ...
        :param fitness: python function taking in input an individual and returning its fitness value as integer
        ...
        :return: None
        """
        self.toolbox.register('evaluate', fitness)


    def start_GA(self, pop_size, pop_list=None):
        """
        Function initializing genetic optimization with its first generation.
        ...
        :param pop_size: (int) Size of the population
        :param pop_list: (list) None by Default - Specified initial population
        ...
        :return: None
        """
        self.pop_size = pop_size

        if pop_list == None:
            self.pop = self.toolbox.population(n=self.pop_size)
        else:
            self.pop= self.toolbox.clone(pop_list)

        self.init_pop = copy.copy(self.pop)

        fitness = list(map(self.toolbox.evaluate, self.pop))

        for self.ind, fit in zip(self.pop, fitness):
            self.ind.fitness.values = [fit]

        self.hof.update(self.pop)

        record = self.stats.compile(self.pop)
        self.logbook.record(gen=1, nevals=len(self.pop), **record, best= self.hof[0])
        if self.verbose:
            print(self.logbook.stream)


    def optimize(self, n_gen, elitism=True, sel=True,  cx=True, mut=True, **kwargs):
        """
        Run the optimization.
        ...
        :param n_gen(int): Maximum number of generations
        :param elitism(bool - Default:True): if True elitism is considered. False for not considering Elitism.
        :param sel(bool - Default:True): For using selection operator in the evolution loop
        :param cx(bool - Default:True): For using crossover operator in the evolution loop
        :param mut(bool - Default:True:) For using mutation operator in the evolution loop
        ...
        :keyword **cx_pb (float): Crossover Probability. If not specified cx_pb=0.8.
            If a custom crossover operator is passed as **custom_cx, then cx_pb must be specified in the external
            function.
        :keyword **mut_pb (float): Mutation Probability. If not specified mut_pb=0.1.
            If a custom crossover operator is passed as **custom_mut, then mut_pb must be specified in the
            external function.
        :keyword **custom_sel (func): Custom Selection Operation as Deap register. Use a function returning a list of
        individuals and which has at least two parameters the population to select from and the number of individuals
        to select.
            For instance:
                rul_sel = GA.toolbox.register('custom_sel', tools.selRoulette)
                GA.optimize(n_gen=100, elitism=True, sel=True,  cx=True, mut=True, mut_pb=0.1, custom_sel=rul_sel)
        :keyword **custom_cx (func): Custom Crossover Operation as Deap register. Use a function which takes as input
        the mating pool and return as output the modified offspring set. Specify the cx_pb in it.
        Be sure to deleting the fitness of created individuals.
            For instance:
                def two_point(offspring, cx_pb):
                    for child1, child2 in zip(offspring[::2], offspring[1::2]):
                        if random.random() < cx_pb:
                            tools.cxTwoPoint(child1, child2)
                            del child1.fitness.values
                            del child2.fitness.values
                two_point = GA.toolbox.register('custom_cx', two_point, cx_pb=0.9)
                GA.optimize(n_gen=100, elitism=True, sel=True,  cx=True, mut=True, mut_pb=0.7, custom_cx=two_point)
        :keyword **custom_mut (func): Custom Mutation Operation as Deap register. Use a function which takes as input
        the mating pool and return as output the modified offspring set. Specify the mut_pb in it.
        Be sure to deleting the fitness of created individuals.
        ...
        :return: logbook object.
        """

        self.n_gen = n_gen

        if 'mut_pb' in kwargs: self.mut_pb = kwargs['mut_pb']
        else: self.mut_pb=0.1

        if 'cx_pb' in kwargs: self.cx_pb = kwargs['cx_pb']
        else: self.cx_pb=0.8

        # Start loop over generations
        for g in range(2, n_gen+1):

            if self.verbose:
                print('starting generation number ', g)

            # Save Best Ind
            if elitism:
                bests = self.toolbox.clone(tools.selBest(self.pop, 1))
                elitist = bests[0]

            # Genetic Selection
            if sel:
                if 'custom_sel' in kwargs:
                    offspring = self.toolbox.custom_sel(self.pop, k=self.pop_size)
                else:
                    offspring = self.toolbox.select_TS(self.pop, k=self.pop_size)
            else:
                offspring = self.pop
            offspring = list(map(self.toolbox.clone, offspring))

            # Genetic Crossover
            if cx:
                if 'custom_cx' in kwargs:
                    self.toolbox.custom_cx(self.pop)

                else:
                    for child1, child2 in zip(offspring[::2], offspring[1::2]):
                        if random.random() < self.cx_pb:
                            self.toolbox.one_point(child1, child2)
                            del child1.fitness.values
                            del child2.fitness.values

            # Genetic Mutation
            if mut:
                if 'custom_mut' in kwargs:
                    self.toolbox.custom_mut(self.pop)
                else:
                    for mutant in offspring:
                        if random.random() < self.mut_pb:
                            self.toolbox.mutate(mutant)
                            del mutant.fitness.values

            # Evaluate the new individuals in the population
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitness = list(map(self.toolbox.evaluate, invalid_ind))
            for ind, fit in zip(invalid_ind, fitness):
                ind.fitness.values = [fit]

            # Replacement
            if elitism:
                self.pop[:] = tools.selBest(offspring, self.pop_size-1)
                self.pop.append(elitist)
            else:
                self.pop[:] = offspring

            # Updating HOF
            self.hof.update(self.pop)

            # Updating Log
            record = self.stats.compile(self.pop)
            self.logbook.record(gen=g, nevals=len(invalid_ind), **record, best= self.hof[0])
            if self.verbose:
                print(self.logbook.stream)

            return self.logbook







