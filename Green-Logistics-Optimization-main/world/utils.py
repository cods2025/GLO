import matplotlib.pyplot as plt

class Node:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

class WarehouseNode(Node):
    def __init__(self, id, x, y, warehouse_type):
        super().__init__(id, x, y)
        self.warehouse_type = warehouse_type

class Edge:
    def __init__(self, node1, node2, weight):
        self.node1 = node1
        self.node2 = node2
        self.weight = weight

class Graph:
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, node):
        self.nodes.append(node)

    def add_edge(self, edge):
        self.edges.append(edge)

    def get_node_by_id(self, id):
        for node in self.nodes:
            if node.id == id:
                return node
    
    def get_edges_by_node(self, node):
        return [edge for edge in self.edges if edge.node1 == node or edge.node2 == node]
    
    def get_edge_by_nodes(self, node1, node2):
        for edge in self.edges:
            if edge.node1 == node1 and edge.node2 == node2:
                return edge
            elif edge.node1 == node2 and edge.node2 == node1:
                return edge
        return None
    
    def plot_graph(self):
        node_coordinates = [(node.x, node.y) for node in self.nodes]
        local_warehouse_coordinates = [(node.x, node.y) for node in self.nodes if isinstance(node, WarehouseNode) and node.warehouse_type == 'local']
        regional_warehouse_coordinates = [(node.x, node.y) for node in self.nodes if isinstance(node, WarehouseNode) and node.warehouse_type == 'regional']
        central_warehouse_coordinates = [(node.x, node.y) for node in self.nodes if isinstance(node, WarehouseNode) and node.warehouse_type == 'central']

        plt.scatter(*zip(*node_coordinates), color='blue', label='Nodes')
        plt.scatter(*zip(*local_warehouse_coordinates), color='red', marker='s', label='Local Warehouse Nodes')
        plt.scatter(*zip(*regional_warehouse_coordinates), color='green', marker='X', label='Regional Warehouse Nodes')
        plt.scatter(*zip(*central_warehouse_coordinates), color='yellow', marker='*', label='Central Warehouse Nodes')

        plt.xlabel('X')
        plt.ylabel('Y')
        plt.legend()
        plt.show()
        
class GraphBuilder:
    def __init__(self, nodes_file, edges_file):
        self.nodes_file = nodes_file
        self.edges_file = edges_file

    def build_graph(self):
        graph = Graph()

        # Read nodes from nodes.txt
        with open(self.nodes_file, 'r') as nodes_file:
            for line in nodes_file:
                node_info = line.strip().split()
                node_id, x, y = node_info
                node = Node(node_id, float(x), float(y))
                graph.add_node(node)

        # Read edges from edges.txt
        with open(self.edges_file, 'r') as edges_file:
            for line in edges_file:
                edge_info = line.strip().split()
                node_id1, node_id2, distance, duration = edge_info
                node1 = graph.get_node_by_id(node_id1)
                node2 = graph.get_node_by_id(node_id2)
                
                weight = (float(distance), float(duration))
                edge = Edge(node1, node2, weight)
                graph.add_edge(edge)

        return graph