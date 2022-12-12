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