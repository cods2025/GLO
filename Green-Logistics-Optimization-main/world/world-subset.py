from utils import Graph, Node, Edge
import requests

version = "v7"

class DatasetExtractor():

    def __init__(self):
        self.graph = Graph()

    def extract_nodes(self,size,write_to_file) :
        content = ""

        filename = "../data/master_data/master_nodes.txt"
        with open(filename, 'r') as file:
            for line in file:
                tokens = line.split()
                id = int(tokens[0])
                x = float(tokens[1])
                y = float(tokens[2])
                if id > size:
                    continue
                if write_to_file:
                    content += f"{id} {x} {y}\n"
                node = Node(id, x, y)
                self.graph.add_node(node)

        print(f"Number of nodes: {len(self.graph.nodes)}")
        # Write to file
        if write_to_file:
            filename = f"../data/world/nodes_{version}.txt"
            with open(filename, 'w') as file:
                file.write(content)

    def extract_edges(self,size,write_to_file):
        filename = "../data/master_data/master_edges.txt"
        with open(filename, 'r') as file:
            for line_number, line in enumerate(file, 1):
          
                tokens = line.split()
                from_id = int(tokens[0])
                to_id = int(tokens[1])
                distance = float(tokens[2])
                duration = float(tokens[3])

                if from_id > size or to_id > size:
                    continue
                
                weight = (distance , duration)

                if write_to_file:
                    with open(f"../data/world/edges_{version}.txt", 'a') as file:
                        file.write(f"{from_id} {to_id} {distance} {duration}\n")

                node1 = self.graph.get_node_by_id(from_id)
                node2 = self.graph.get_node_by_id(to_id)
                edge = Edge(node1, node2, weight)
                self.graph.add_edge(edge)


        print(f"Number of edges: {len(self.graph.edges)}")


    def extract_dataset(self, size, write_to_file):
        
        self.extract_nodes(size,write_to_file)
        self.extract_edges(size,write_to_file)     
        return self.graph


if __name__ == "__main__":
    dataset_extractor = DatasetExtractor()
    size = 2500
    graph = dataset_extractor.extract_dataset(size, True)
    print("Graph created successfully!")
