from Problems.knapsack_problem import knapsack
from GA_Optimization import GA_Optimizer

from qiskit import IBMQ
from GeneticOperators import quantum_mating_operator as QMO

IBMQ.enable_account('64be1b8a0ab4152d84501676396527b41fc86f9f26807f800059e39cf35961b1127ef3be9190aae8058ba5d955fefadf3ee4663f305cdf5a3412b93dbf77464a')
IBMQ.save_account('64be1b8a0ab4152d84501676396527b41fc86f9f26807f800059e39cf35961b1127ef3be9190aae8058ba5d955fefadf3ee4663f305cdf5a3412b93dbf77464a', overwrite=True)
provider = IBMQ.get_provider(hub='ibm-q-research',group='uni-naples-feder-3', project='main')


# SETUP OF THE PROBLEM
knapsack_size = 10
kn = knapsack(N=knapsack_size, capacity_percentage=0.25)
kn.setup(max=100)

def quantum_mating(offspring, cx_pb, mut_pb):
    QMO.qmo(pop=offspring, ind_size=knapsack_size, cx_pb=cx_pb, m_pb=mut_pb, provider=provider, backend_name='fake',
            draw_qc=False, creator_ind=GA.deap_creator.Individual)
    return offspring


# INITIALIZING GA_OPTIMIZER
GA = GA_Optimizer(problem_size=knapsack_size,  verbose=True)
GA.set_Fitness_Function(kn.evaluate)
quantum_mating = GA.toolbox.register('custom_cx', quantum_mating, cx_pb=0.9, mut_pb=0.5)

# RUN THE OPTIMIZATION
GA.start_GA(pop_size=10)
GA.optimize( elitism=True, sel=True,  cx=True, mut=False, max_gen=20, max_evals=1000, custom_cx=quantum_mating)
