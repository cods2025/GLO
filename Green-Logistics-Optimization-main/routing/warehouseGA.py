import numpy as np
import random
import matplotlib.pyplot as plt
from routingGA import RoutingGeneticAlgorithm
import os
from sklearn.cluster import KMeans
from scipy.spatial import distance
from sklearn.cluster import MiniBatchKMeans
from scipy.spatial import KDTree


class Cluster:
    def __init__(self, nodes):
        self.nodes = nodes
        self.fitness = 0

class Population:
    def __init__(self, clusters):
        self.clusters = clusters
        self.fitness = 0
    
    def __str__(self):
        return f"Population with {len(self.clusters)} clusters"

class WarehouseGeneticAlgorithm:
    def __init__(self, graph, n_clusters, population_size=100, generations=1, crossover_prob=0.7, mutation_prob=0.2):
        self.graph = graph
        self.n_clusters = n_clusters
        self.population_size = population_size
        self.generations = generations
        self.crossover_prob = crossover_prob
        self.mutation_prob = mutation_prob
        self.population = []
        self.edge_weights = self.calculate_edge_weights()
        self.cluster_kdtree = None  # Initialize KDTree
        self.colors = self.generate_hue_shades(n_clusters)
    
    def calculate_edge_weights(self):
        num_nodes = len(self.graph.nodes)
        edge_weights = np.zeros((num_nodes, num_nodes))

        edges = self.graph.edges

        node_indices = {node: i for i, node in enumerate(self.graph.nodes)}

        for edge in edges:
            i, j = node_indices[edge.node1], node_indices[edge.node2]
            edge_weights[i, j] = edge_weights[j, i] = edge.weight[1]

        return edge_weights
    
    def initialize_population(self):
        print("Initializing population...")

        nodes_array = np.array([[node.x, node.y] for node in self.graph.nodes])

        # Use MiniBatchKMeans for efficient initialization
        kmeans = MiniBatchKMeans(n_clusters=self.n_clusters, batch_size=100).fit(nodes_array)
        cluster_labels = kmeans.labels_

        clusters = []
        for i in range(self.n_clusters):
            cluster_nodes = [self.graph.nodes[j] for j, label in enumerate(cluster_labels) if label == i]
            clusters.append(Cluster(cluster_nodes))

        self.population = [Population(clusters) for _ in range(self.population_size)]

        # Create KDTree for efficient nearest neighbor search during mutation
        cluster_centroids = np.array([np.mean(np.array([[node.x, node.y] for node in cluster.nodes]), axis=0)
                                      for cluster in clusters])
        self.cluster_kdtree = KDTree(cluster_centroids)

    def find_nearest_cluster(self, node):
        # Use KDTree to efficiently find the nearest cluster for a given node
        node_coordinates = np.array([[node.x, node.y]])
        dist, idx = self.cluster_kdtree.query(node_coordinates, k=1)
        return idx[0]
    
    def convert_clusters_to_nodes_list(self, clusters):
        # Convert a list of Cluster instances to a list of node lists
        return [cluster.nodes for cluster in clusters]

    def convert_nodes_list_to_clusters(self, nodes_list):
        # Convert a list of node lists to a list of Cluster instances
        return [Cluster(nodes) for nodes in nodes_list]

    def evaluate_population(self):
        # Evaluate the fitness of each individual in the population
        fitness_values = []
        for population in self.population:
            fitness = self.calculate_fitness(population.clusters)
            fitness_values.append(fitness)

            # Attach fitness value to the population
            population.fitness = fitness

    def get_routing_fitness(self, cluster):
        vehicles = [1,2]
        genetic_algorithm = RoutingGeneticAlgorithm(self.graph, vehicles, [(node.id,random.randint(1,10)) for node in cluster.nodes ] , population_size=100, generations=1)  
        best_order , best_fitness = genetic_algorithm.evolve()
        return best_fitness

    def calculate_fitness(self, clusters):
        total_fitness = 0
        for cluster in clusters:
            if len(cluster.nodes) > 0:
                intra_cluster_distance = self.calculate_intra_cluster_distance(cluster.nodes)
                # routing_fitness = self.get_routing_fitness(cluster)
                total_fitness += intra_cluster_distance 
                # total_fitness += routing_fitness
        return total_fitness

    def calculate_intra_cluster_distance(self, cluster_nodes):
        # Extract node indices
        indices = [self.graph.nodes.index(node) for node in cluster_nodes]
        indices = np.array(indices, dtype=int)
        intra_cluster_distances = self.edge_weights[indices[:, None], indices].sum()
        return intra_cluster_distances

    def select_parents(self):
        # Tournament selection
        parents = []
        for _ in range(self.population_size):
            tournament_size = random.randint(2, min(self.population_size, len(self.population)))
            tournament = random.sample(self.population, tournament_size)

            # Select the population with the highest fitness in each tournament
            best_population = max(tournament, key=lambda x: x.fitness)
            parents.append(best_population)
        return parents

    def mutate(self, population):
        # Perform mutation by reassigning nodes to the nearest cluster using KDTree
        for cluster in population.clusters:
            for node in cluster.nodes:
                nearest_cluster_idx = self.find_nearest_cluster(node)
                if nearest_cluster_idx != population.clusters.index(cluster):
                    population.clusters[nearest_cluster_idx].nodes.append(node)
                    cluster.nodes.remove(node)

    def crossover(self, parent1, parent2):
        # Perform crossover with balanced node assignment between clusters
        child_clusters = []
        for cluster1, cluster2 in zip(parent1.clusters, parent2.clusters):
            child_nodes = cluster1.nodes + cluster2.nodes
            child_cluster = Cluster(child_nodes)
            child_clusters.append(child_cluster)

        while len(child_clusters) > self.n_clusters:
            # Merge the two most similar clusters
            min_distance = float('inf')
            merge_idx = (-1, -1)

            for i in range(len(child_clusters)):
                for j in range(i + 1, len(child_clusters)):
                    dist = self.calculate_cluster_distance(child_clusters[i], child_clusters[j])
                    if dist < min_distance:
                        min_distance = dist
                        merge_idx = (i, j)

            i, j = merge_idx
            # Merge clusters with similar nodes
            child_clusters[i].nodes += child_clusters[j].nodes
            child_clusters.pop(j)

        return Population(child_clusters)

    def calculate_cluster_distance(self, cluster1, cluster2):
        # Calculate distance between two clusters based on their centroids
        centroid1 = np.mean(np.array([[n.x, n.y] for n in cluster1.nodes]), axis=0)
        centroid2 = np.mean(np.array([[n.x, n.y] for n in cluster2.nodes]), axis=0)
        return distance.euclidean(centroid1, centroid2)
    
    def generate_hue_shades(self, n_clusters):
        hues = [
            [(0.2, 0.4, 0.6), (0.1, 0.1, 0.6)],  # Blue hues
            [(0.1, 0.6, 0.3), (0.1, 0.5, 0.2)],  # Green hues
            [(0.8, 0.1, 0.1), (0.6, 0.1, 0.1)],  # Red hues
            [(0.1, 0.8, 0.8), (0.1, 0.6, 0.7)],  # Cyan hues
            [(0.8, 0.8, 0.1), (0.7, 0.7, 0.1)],  # Yellow hues
        ]

        hues_count = len(hues)
        shades_per_hue = n_clusters // hues_count
        remainder = n_clusters % hues_count

        shades = []

        for hue in hues:
            start_color, end_color = hue
            for i in range(shades_per_hue):
                # Vary shade intensity by adding random values
                shade = [start + random.uniform(0.1, 0.2) for start in start_color]
                shades.append(shade)

        # Handling any remainder shades
        if remainder:
            for i in range(remainder):
                start_color, end_color = hues[i]
                # Vary shade intensity by adding random values
                shade = [start + random.uniform(0.1, 0.3) for start in start_color]
                shades.append(shade)

        return shades
    
    def plot_clusters(self, clusters_map, iteration,fitness_scores):
        # Create a directory to save the plots
        results_directory = "../results/warehouses"
        
        if not os.path.exists(results_directory):
            os.makedirs(results_directory)
        
        # Get node coordinates
        node_coordinates = {node.id: (node.x, node.y) for node in self.graph.nodes}

        # Plot the graph with clusters and centroids
        for idx, (cluster_id, cluster_nodes) in enumerate(clusters_map.items()):
            cluster_color = self.colors[idx]
            cluster_x = [node_coordinates[node_id][0] for node_id in cluster_nodes]
            cluster_y = [node_coordinates[node_id][1] for node_id in cluster_nodes]
            plt.scatter(cluster_x, cluster_y, color=cluster_color, s=50, label=cluster_id)
            centroid_x = np.mean(cluster_x)
            centroid_y = np.mean(cluster_y)
            plt.scatter(centroid_x, centroid_y, marker='o', color='black', edgecolor='black', s=200)

        plt.title(f'Iteration {iteration}')
        plt.legend()
        plt.savefig(os.path.join(results_directory, f'iteration_{iteration}.png'))
        plt.clf()

        plt.plot(range(iteration+1), fitness_scores, marker='o', linestyle='-')
        plt.title('Fitness Score Evolution')
        plt.xlabel('Generation')
        plt.ylabel('Fitness Score')
        plt.xticks(range(iteration+1), [f'{i}' for i in range(iteration+1)])
        plt.grid(True)
        plt.savefig(os.path.join(results_directory, f'fitness_score_evolution.png'))
        plt.clf()

    def run(self):
        print("Starting the Warehouse Genetic Algorithm...")
        self.initialize_population()
        # Create a map of cluster ID to nodes for the best clusters
        best_clusters_map = {}
        
        fitness_scores = []  # Store fitness scores across generations

        print("Warehouse Generations : " , self.generations)

        for generation in range(self.generations):
            print(f'Generation {generation}')
            parents = self.select_parents()
            offspring = []

            for i in range(0, self.population_size, 2):
                if random.random() < self.crossover_prob:
                    child = self.crossover(parents[i], parents[i + 1])
                else:
                    child = parents[i]

                if random.random() < self.mutation_prob:
                    self.mutate(child)

                offspring.append(child)

            self.population = offspring
            self.evaluate_population()

            # Return the best population
            best_population = max(self.population, key=lambda x: x.fitness)
            
            for idx, cluster in enumerate(best_population.clusters):
                cluster_id = f"Cluster_{idx+1}"
                best_clusters_map[cluster_id] = [node.id for node in cluster.nodes]
            
            mean_fitness = np.mean([pop.fitness for pop in self.population])
            fitness_scores.append(mean_fitness)        

            # Plot the clusters for each generation
            if generation % 100 == 0:
                # Store the best fitness score of the generation
                self.plot_clusters(best_clusters_map, int(generation), fitness_scores)

        return best_clusters_map

