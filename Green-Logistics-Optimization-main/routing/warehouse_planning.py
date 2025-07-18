from utils import *
from warehouseGA import WarehouseGeneticAlgorithm
import json

VERSION = 'v9'
BASE_PATH = '../data/world'
NODES_PATH = BASE_PATH + f'/nodes_{VERSION}.txt'
EDGES_PATH = BASE_PATH + f'/edges_{VERSION}.txt'

GraphBuilder = GraphBuilder(NODES_PATH, EDGES_PATH)
graph = GraphBuilder.build_graph()

# Create a GeneticAlgorithm instance and run the algorithm
warehouse_planning = WarehouseGeneticAlgorithm(graph,generations=500, n_clusters=6)
best_population = warehouse_planning.run()

# Save the best clusters map in JSON format
json_filename = 'best_clusters_map.json'
with open(json_filename, 'w') as json_file:
    json.dump(best_population, json_file)

print(f'Best clusters map saved in {json_filename}')

