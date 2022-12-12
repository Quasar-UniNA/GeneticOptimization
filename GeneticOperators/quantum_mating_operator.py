import random,math
from qiskit import QuantumCircuit, QuantumRegister, execute, Aer, IBMQ, BasicAer
from qiskit.test.mock import FakeSydney
from qiskit.providers.aer.noise import NoiseModel, depolarizing_error
from qiskit.providers.aer.noise import  ReadoutError

#IBMQ.enable_account('64be1b8a0ab4152d84501676396527b41fc86f9f26807f800059e39cf35961b1127ef3be9190aae8058ba5d955fefadf3ee4663f305cdf5a3412b93dbf77464a')
#IBMQ.save_account('64be1b8a0ab4152d84501676396527b41fc86f9f26807f800059e39cf35961b1127ef3be9190aae8058ba5d955fefadf3ee4663f305cdf5a3412b93dbf77464a', overwrite=True)
#provider = IBMQ.get_provider(hub='ibm-q-research',group='uni-naples-feder-3', project='main')



def generate_ind_from_count(final_pop, counts):
    '''
    Function appending to final_pop the states in the counts vector as list of
    integers in the correct order.

    :param final_pop: pop in which the new individual will be appended
    :param counts: counts vector for qc measurement
    :return: None
    '''
    for state in list(counts.keys()):
        #print(state)
        ind = []
        for b in range(len(state)):
            ind.append(int(state[-1-b]))
        for occurence in range(counts[state]):
            final_pop.append(ind)


def compute_frequencies(ind_list):
    '''
    Function compunting the occorence of ones position
    by position of the individuals in the list ind_list.
    :param ind_list: list of individuals to mate
    :return: one_frequences as dictionary.
    '''
    ind_size = len(ind_list[0])
    one_frequences = {i:0 for i in range(ind_size)}
    for bit in range(ind_size):
        sum_bit = 0
        for ind in ind_list:
            sum_bit = sum_bit + ind[bit]
        one_frequences[bit] = sum_bit/len(ind_list)
    return one_frequences


def noise_model(prob_1=0.001, prob_2=0.01, p0given1=0.1, p1given0=0.05):
    '''
    Build noise model for simulation.
    :param prob_1: probability single qubit gate error
    :param prob_2: probability two-qubits gate error
    :param p0given1: readout probability that 1 is flipped in 0
    :param p1given0: readout probability that 0 is flipped in 1
    :return: noise model
    '''

    # Depolarizing quantum errors
    error_1 = depolarizing_error(prob_1, 1)
    error_2 = depolarizing_error(prob_2, 2)

    # Measurement miss-assignement probabilities
    error_rd = ReadoutError([[1 - p1given0, p1given0], [p0given1, 1 - p0given1]])

    # Add errors to noise model
    noise_model = NoiseModel()
    noise_model.add_all_qubit_quantum_error(error_1, ['u1', 'u2', 'u3'])
    noise_model.add_all_qubit_quantum_error(error_2, ['cx'])
    noise_model.add_all_qubit_readout_error(error_rd)

    # Get basis gates from noise model
    #basis_gates = noise_model.basis_gates
    return noise_model


def qmo(pop, ind_size, cx_pb, m_pb, provider, backend_name, noise_model=None, draw_qc=False):
    '''
    Function implementing QMO operator.
    :param pop: genetic population
    :param ind_size: problem size
    :param cx_pb: probability of crossover
    :param m_pb: probability of mutation
    :param provider: IBM provider
    :param backend_name: IBM quantum circuit backend
    :param noise_model: Noise Model - None by default
    :param draw_qc: Show QMO quantum circuit if TRUE - False by default
    :return: New Genetic Population
    '''
    pop_size = len(pop)
    new_pop = []
    to_consider, to_not_consider = [],[]
    # if random < cx_pb then consider the individual for crossover
    for ind in pop:
        if random.random() < cx_pb:
            to_consider.append(ind)

        else:
            to_not_consider.append(ind)
    if len(to_consider)>0:
        rotations = compute_frequencies(to_consider)
        #print(to_consider,rotations)
        for iteration in range(len(to_consider)):
            qr= QuantumRegister(ind_size)
            qc = QuantumCircuit(qr)
            for bit in range(ind_size):
                #print('bit', bit)
                qc.ry(math.pi*rotations[bit], qr[bit])
                if random.random() < m_pb:
                    #print('target', target)
                    qc.ry(math.pi*random.random(),qr[bit])
            qc.measure_all()
            if draw_qc:
                qc.draw('mpl').show()

            #execute qc
            if backend_name == 'fake':
                backend = BasicAer.get_backend('qasm_simulator')
                if noise_model != None:
                    job = execute(qc, backend, noise_model=noise_model, shots=1, seed_simulator=random.randint(1, 150))

                else:
                    job = execute(qc, backend, shots=1, seed_simulator=random.randint(1, 150))
                result = job.result()
                counts = result.get_counts()

            if backend_name == 'fake_sydney':
                backend = provider.get_backend('ibmq_qasm_simulator')
                noisy_backend = FakeSydney()
                noise_model = NoiseModel.from_backend(noisy_backend)
                job = execute(qc, backend, shots=1, seed_simulator=random.randint(1, 150), noise_model=noise_model)
                result = job.result()
                counts = result.get_counts()
            else:
                backend = provider.get_backend(backend_name)
                job = execute(qc, backend, shots=1, seed_simulator=random.randint(1, 150))
                result = job.result()
                counts = result.get_counts()

            generate_ind_from_count(new_pop, counts)

    for ind in to_not_consider:
        new_pop.append(ind)

    return new_pop