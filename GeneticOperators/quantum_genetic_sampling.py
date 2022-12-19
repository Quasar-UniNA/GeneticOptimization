from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, execute, Aer, IBMQ, BasicAer
from deap import tools
import math, random



def qgs(pop, toolbox, creator_ind, t, beta, iterations, draw_circuit=False, **kwargs):
    """
    Function implementing QGS operator. By default, QGS works simulating ideally the quantum circuit created.
    Real quantum devices from IBM Quantum can be used specifying the backend argument.
    ...
    :param (list) pop: genetic population from which select the mating pool;
    :param (DEAP Toolbox) toolbox: DEAP toolbox related to a GA object;
    :param (DEAP Creator Method) creator_ind: DEAP individual creator object related to a GA object;
    :param (int) t: Number of individuals to amplify;
    :param (float) beta: progressive angle for adaptive amplitude amplification;
    :param (int) iterations: Grover's Oracle iterations in the quantum circuit;
    :param (bool - False Default) draw_circuit: True for plotting the created quantum circuit.
    ...
    :keyword **provider: IBMQ provider if real backands or IBMQ simulators have to be used;
    :keyword **backend: IBMQ backend object;
    :keyword **noise_model: Qiskit Noise Model Object. If specified, it will be considered in the simulation;
    ...
    :return (list): Mating pool.

    """
    n = len(pop[0])
    shots = len(pop)
    bests = toolbox.clone(tools.selBest(pop, t))
    n2f = [int(list_to_string(bests[i]),2) for i in range(t)]

    reg = QuantumRegister(n, name='reg')
    scratch = QuantumRegister(n-3, name='scratch')
    c_reg = ClassicalRegister(n, name='output')
    qc = QuantumCircuit(reg, scratch, c_reg)
    qc.h(reg)

    for i in range(iterations):
        ## Flip the marked value
        qc.x(scratch)
        qc.barrier()
        k = 0
        for number_to_flip in n2f:
            x_bits = ~number_to_flip
            x_list = [reg[x] for x in range(len(reg)) if x_bits & (1 << x)]
            if x_list:
                qc.x(x_list)
            customize_phase_flip(qc, math.pi-k*beta, [x for x in reg], scratch[0])
            if x_list:
                qc.x(x_list)
            k = k+1
        qc.x(scratch)
        qc.barrier()
        Grover(qc, reg, scratch)
    qc.measure(reg, c_reg)

    # Execute qc
    if 'backend' not in kwargs:
        # QASM SIMULATOR
        backend = Aer.get_backend('qasm_simulator')
        if 'noise_model' in kwargs:
            job = execute(qc, backend, noise_model=kwargs['noise_model'], shots=shots,
                          seed_simulator=random.randint(1, 150))
        else:
            job = execute(qc, backend, shots=shots, seed_simulator=random.randint(1, 150))
        result = job.result()
        counts = result.get_counts()

    # CUSTOM BACKEND
    else:
        if 'noise_model' in kwargs:
            job = execute(qc, kwargs['backend'], noise_model=kwargs['noise_model'], shots=shots,
                          seed_simulator=random.randint(1, 150))
        else:
            job = execute(qc, kwargs['backend'], shots=shots, seed_simulator=random.randint(1, 150))
        result = job.result()
        counts = result.get_counts()

    if draw_circuit:
        qc.draw(output='mpl').show()
    off = create_offspring(creator_ind, counts)
    return off




###############################################
## Some utility functions

def Grover(qc, qreg, scratch, condition_qubits=None):
    if condition_qubits is None:
        condition_qubits = []
    qc.h(qreg)
    qc.x(qreg)
    qubits = [x for x in qreg] + condition_qubits
    multi_cz(qc=qc, qubits=qubits, scratch=scratch)
    qc.x(qreg)
    qc.h(qreg)

def multi_cx(qc, qubits, scratch, do_cz=False):
    ## This will perform a CCCCCX with as many conditions as we want,
    ## as long as we have enough scratch qubits
    ## The last qubit in the list is the target.
    target = qubits[-1]
    conds = qubits[:-1]
    #print(conds)
    #print(target, conds)
    scratch_index = 0
    ops = []
    while len(conds) > 2:
        new_conds = []
        for i in range(len(conds)//2):
            #print(i, len(conds)//2 )
            ops.append((conds[i * 2], conds[i * 2 + 1], scratch[scratch_index]))
            new_conds.append(scratch[scratch_index])
            scratch_index += 1
        if len(conds) & 1:
            new_conds.append(conds[-1])
        conds = new_conds
    for op in ops:
        qc.ccx(op[0], op[1], op[2])
    if do_cz:
        qc.h(target)
    if len(conds) == 0:
        qc.x(target)
    elif len(conds) == 1:
        qc.cx(conds[0], target)
    else:
        qc.ccx(conds[0], conds[1], target)

    if do_cz:
        qc.h(target)
    ops.reverse()
    for op in ops:
        qc.ccx(op[0], op[1], op[2])

def customize_phase_flip(qc, angle, reg, scratch):
    qc.mcp(angle, reg, scratch)




def multi_cz(qc, qubits, scratch):
    ## This will perform a CCCCCZ on as many qubits as we want,
    ## as long as we have enough scratch qubits
    multi_cx(qc, qubits, scratch, do_cz=True)

def list_to_string(l):
    """Function that transform a a list such as [0,1,1,1,0]
    in string such as '01110' """
    s=''
    for i in l:
        s = s + str(i)
    return s


def create_offspring(creator_ind, offspring_dict):
    offspring=[]
    for ind in list(offspring_dict.keys()):
        for iteration in range(offspring_dict[ind]):
            individuo = creator_ind([int(i) for i in ind])
            offspring.append(individuo)
    return offspring