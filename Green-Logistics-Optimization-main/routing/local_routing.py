from utils import *
from routingGA import RoutingGeneticAlgorithm

BASE_PATH = '../data/world'
NODES_PATH = '../results/clusters/local/local_0.txt'
EDGES_PATH = BASE_PATH + '/world_edges.txt'

GraphBuilder = GraphBuilder(NODES_PATH, EDGES_PATH)
graph = GraphBuilder.build_graph()


print("Generating Optimal Route...")

# Specify a subset of nodes if needed
subset_nodes = [(2499,1) ,(3816,2), (3817,3) ,(3819,2), (3820,3), (3821,4), (3822,1), (3824,3), (3825,100), (3826,1), (3827,1), (3828,1), (3829,1), (3830,1)] 
vehicles = [1,2]

# Create a GeneticAlgorithm instance and run the algorithm
genetic_algorithm = RoutingGeneticAlgorithm(graph,vehicles, subset_nodes , population_size=100, generations=1)
best_order , best_fitness = genetic_algorithm.evolve()
print("Best order:", best_order , "Best fitness:", best_fitness)