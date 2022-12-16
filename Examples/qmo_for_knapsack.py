from Problems.knapsack_problem import knapsack
from GA_Optimization import GA_Optimizer

from qiskit import IBMQ
from GeneticOperators import quantum_mating_operator as QMO

# SETUP OF THE PROBLEM
knapsack_size = 10
kn = knapsack(N=knapsack_size, capacity_percentage=0.25)
kn.setup(max=100)

def quantum_mating(offspring, cx_pb, mut_pb, prob_1=0.001, prob_2=0.01, p0given1=0.1, p1given0=0.05):
    # Build Custom Noise Model
    noise_model = QMO.noise_model(prob_1=prob_1, prob_2=prob_2, p0given1=p0given1, p1given0=p1given0)
    # Define QMO operator
    QMO.qmo(pop=offspring, ind_size=knapsack_size, cx_pb=cx_pb, m_pb=mut_pb, draw_qc=False,
            creator_ind=GA.deap_creator.Individual, noise_model=noise_model)
    return offspring


# INITIALIZING GA_OPTIMIZER
GA = GA_Optimizer(problem_size=knapsack_size,  verbose=True)
GA.set_Fitness_Function(kn.evaluate)
q_mating = GA.toolbox.register('custom_cx', quantum_mating, cx_pb=0.8, mut_pb=0.5)

# RUN THE OPTIMIZATION
GA.start_GA(pop_size=10)
GA.optimize(elitism=True, sel=True,  cx=True, mut=False, max_gen=20, max_evals=1000, custom_cx=q_mating)
