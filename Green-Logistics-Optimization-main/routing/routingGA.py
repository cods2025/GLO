import random
import copy
import pandas as pd
import numpy as np
import tensorflow as tf
import math

class RoutingGeneticAlgorithm:
    def __init__(self, graph, vehicles, subset_nodes=None, population_size=100, generations=500):
        self.graph = graph
        self.subset_nodes = subset_nodes if subset_nodes is not None else [(node.id, 1) for node in self.graph.nodes]
        self.population_size = population_size
        self.generations = generations
        self.vehicles_df = self.get_vehicles_info('../data/world/vehicles.csv', vehicles)
        self.loaded_model = tf.keras.models.load_model('../ml-modules/models/emission_model')
        self.co2_emissions = self.get_vehicle_emissions(self.vehicles_df)
        self.capacity = self.get_vehicles_capacity(self.vehicles_df)


    def get_vehicles_info(self, path, vehicles):
        # print("Reading csv")
        df = pd.read_csv(path)
        filtered_df = df[df['Vehicle ID'].isin(vehicles)]
        return filtered_df

    def get_vehicles_capacity(self, vehicle_df):
        capacity_map = dict(zip(vehicle_df['Vehicle ID'], vehicle_df['Capacity (cubic feet)']))
        return capacity_map

    def get_emission_prediction(self, sample):
        # loaded_model = tf.keras.models.load_model('../ml-modules/models/emission_model')
        return self.loaded_model.predict(sample).tolist()[0][0]

    def get_vehicle_emissions(self, vehicles_df):
        features_columns = ['Capacity (cubic feet)', 'Engine Size(L)', 'Cylinders', 'Transmission', 
                         'Fuel Type', 'Fuel Consumption City (L/100 km)', 'Fuel Consumption Hwy (L/100 km)', 
                         'Fuel Consumption Comb (L/100 km)', 'Fuel Consumption Comb (mpg)']

        predictions = {row['Vehicle ID']: self.get_emission_prediction(np.array([row[features_columns]])) for _, row in vehicles_df.iterrows()}

        return predictions

    def initialize_population(self):
        population = []

        for _ in range(self.population_size):
            individual = self.random_individual()
            population.append(individual)

        return population

    def random_individual(self):
        individual = {}

        # Shuffle the subset nodes to randomize the assignment order
        shuffled_nodes = random.sample(self.subset_nodes, len(self.subset_nodes))

        for node, delivery_capacity in shuffled_nodes:
            remaining_capacity = delivery_capacity

            # Filter available vehicles for the current node
            available_vehicles = [v_id for v_id, v_cap in self.capacity.items() if v_cap >= remaining_capacity]

            # Check if there are available vehicles for the current node
            if available_vehicles:
                vehicle_id = random.choice(available_vehicles)
                vehicle_capacity = self.capacity[vehicle_id]

                # Assign the remaining capacity to the vehicle
                assigned_capacity = min(remaining_capacity, vehicle_capacity)

                # Check if the assigned capacity exceeds the capacity of a single route
                if assigned_capacity <= vehicle_capacity:
                    individual.setdefault(vehicle_id, []).append((node, assigned_capacity))
                else:
                    # If the assigned capacity exceeds the capacity of a single route,
                    # create multiple routes for the vehicle
                    while assigned_capacity > 0:
                        route_capacity = min(assigned_capacity, vehicle_capacity)
                        individual.setdefault(vehicle_id, []).append((node, route_capacity))
                        assigned_capacity -= route_capacity

        return individual

    def calculate_fitness(self, individual):
        total_fitness = 0

        for vehicle_id, nodes in individual.items():
            route_duration , route_distance = self.calculate_route_info(nodes)
            carbon_emissions = self.co2_emissions[vehicle_id]*route_distance

            # Apply negative logarithmic transformation to both duration and emissions
            neg_log_duration = -math.log(1 + route_duration)
            neg_log_emissions = -math.log(1 + carbon_emissions)

            # Combine negative logarithmic values with weights
            duration_weight = 0.9  # Adjust according to your preferences
            emissions_weight = 0.1  # Adjust according to your preferences

            fitness_value = duration_weight * neg_log_duration + emissions_weight * neg_log_emissions

            total_fitness += fitness_value

        return total_fitness

    def calculate_route_info(self, nodes):
        total_duration = 0
        total_distance = 0
        for i in range(len(nodes) - 1):
            edge = self.graph.get_edge_by_nodes(nodes[i][0], nodes[i + 1][0])

            # Check if the edge exists
            if edge is not None:
                total_duration += edge.weight[1]
                total_distance += edge.weight[0]
            else:
                total_duration += 100000  # Penalize for non-existent edges

        # Add info  for returning to the starting node
        return total_duration , total_distance

    def crossover(self, parent1, parent2):
        child = {}

        # Combine routes from parents at the vehicle level
        for vehicle_id in set(parent1.keys()) | set(parent2.keys()):
            routes = []
            for parent in [parent1, parent2]:
                if vehicle_id in parent:
                    routes.extend(parent[vehicle_id])

            # Ensure all nodes from subset_nodes are included
            for node, delivery_capacity in self.subset_nodes:
                if any(node == n for n, _ in routes):
                    child.setdefault(vehicle_id, []).append((node, delivery_capacity))

        # Ensure the child's routes adhere to capacity constraints
        self.adjust_routes_capacity(child)

        return child

    def mutate(self, individual):
        mutation_point = random.choice(list(individual.keys()))
        route_to_mutate = individual[mutation_point]

        # Mutate a random route by adding or removing nodes while respecting capacity constraints
        mutated_route = self.adjust_route_capacity(mutation_point, route_to_mutate)

        # Ensure all nodes from subset_nodes are included
        for node, delivery_capacity in self.subset_nodes:
            if any(node == n for n, _ in mutated_route):
                mutated_route.append((node, delivery_capacity))

        individual[mutation_point] = mutated_route

    def adjust_routes_capacity(self, individual):
        for vehicle_id, nodes in individual.items():
            individual[vehicle_id] = self.adjust_route_capacity(vehicle_id, nodes)

    def adjust_route_capacity(self, vehicle_id, nodes):
        # Adjust the route to adhere to capacity constraints
        vehicle_capacity = self.capacity[vehicle_id]
        remaining_capacity = vehicle_capacity

        # Filter nodes based on capacity constraints
        valid_nodes = []

        for node, delivery_capacity in nodes:
            if delivery_capacity <= remaining_capacity:
                valid_nodes.append((node, delivery_capacity))
                remaining_capacity -= delivery_capacity

        return valid_nodes

    def evolve(self):
        population = self.initialize_population()
        for generation in range(self.generations):
            population = sorted(population, key=lambda x: self.calculate_fitness(x), reverse=True)

            # Select top 50% of the population as parents
            parents = population[:len(population) // 2]

            # Generate offspring through crossover and mutation
            offspring = []

            while len(offspring) < len(population) - len(parents):
                parent1, parent2 = random.sample(parents, 2)
                child = self.crossover(parent1, parent2)

                if random.random() < 0.5:
                    self.mutate(child)

                offspring.append(child)

            # Combine parents and offspring for the next generation
            population = parents + offspring

        # Return the best order and its fitness score from the final generation
        best_order = max(population, key=lambda x: self.calculate_fitness(x))
        best_fitness = self.calculate_fitness(best_order)

        return best_order , best_fitness
