# Genetic Optimization
___ 

This repo contains code for implementing genetic algorithms (GAs) using as backend the DEAP library.

The code is useful to easily equip a classical GA with new operators. 

The repo is organized as follows: 

- **GA_Optimization.py** contains the main class for implementing a binary encoded GA. 
  (<i>A more general version enabling also the execution of real encoded GA must be developed yet.</i>)

- **Problems** folder contains benchmark problems (<i>For now just the 0-1 knapsack problem </i>)

- **Genetic Operators** folder contains code for implementing custom genetic operators. 
 
  - quantum_mating_operator.py implements the QMO algorithm presented in <i> Acampora, Giovanni, Roberto Schiattarella,
   and Autilia Vitiello. "Quantum Mating Operator: A New Approach to Evolve Chromosomes in Genetic Algorithms." 
   2022 IEEE Congress on Evolutionary Computation (CEC). IEEE, 2022. </i>

## Usage

```python
from Problems.knapsack_problem import knapsack
from GA_Optimization import GA_Optimizer
import random
from deap import tools

# SETUP OF THE PROBLEM
kn = knapsack(N=10, capacity_percentage=0.75)
kn.setup(max=100)

# DEFINING CUSTOM CROSSOVER OPERATOR
def two_point(offspring, cx_pb):
    for child1, child2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < cx_pb:
            tools.cxTwoPoint(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

# INITIALIZING GA_OPTIMIZER
GA = GA_Optimizer(problem_size=10,  verbose=True)
GA.set_Fitness_Function(kn.evaluate)
two_point = GA.toolbox.register('custom_cx', two_point, cx_pb=0.9)

# RUN THE OPTIMIZATION
GA.start_GA(pop_size=10)
GA.optimize(n_gen=100, elitism=True, sel=True,  cx=True, mut=True, mut_pb=0.7, custom_cx=two_point)

```

**Examples** contains more examples of application. 

