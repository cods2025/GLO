from utils import Graph, Node, Edge
import requests

version = "v2"

class DatasetExtractor():

    def __init__(self):
        self.graph = Graph()
        self.last_processed_line = 0
        self.progress_file = f"../data/progress/progress_{version}.txt"

    def load_progress(self):
        try:
            with open(self.progress_file, 'r') as file:
                self.last_processed_line = int(file.readline())
        except FileNotFoundError:
            pass

    def save_progress(self, line_number):
        with open(self.progress_file, 'w') as file:
            file.write(str(line_number))


    def api_call_to_get_edge_weight(self, from_id, to_id):
        node1 = self.graph.get_node_by_id(from_id)
        node2 = self.graph.get_node_by_id(to_id)

        # Calculate distance between two nodes
        long1 = float(node1.x) / 1000000
        lat1 = float(node1.y) / 1000000

        long2 = float(node2.x) / 1000000
        lat2 = float(node2.y) / 1000000

        # Make the API call
        url = f"http://router.project-osrm.org/route/v1/driving/{long1},{lat1};{long2},{lat2}"
        response = requests.get(url)

        if response.status_code == 200:
            result = response.json()

            # Extract distance and duration from the response
            distance = result['routes'][0]['distance']
            duration = result['routes'][0]['duration']

            print(f"From {from_id} to {to_id} - distance: {distance} - duration: {duration}")

            return distance, duration
        else:
            print(f"Error: Unable to fetch data from API. Status code {response.status_code}")
            return None, None

    def extract_nodes(self,size,write_to_file) :
        content = ""

        # Read from file USA-road-d.USA.co and add nodes
        filename = "../data/archive/USA-road-d.USA.co"
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v'):
                    tokens = line.split()
                    id = int(tokens[1])
                    x = int(tokens[2])
                    y = int(tokens[3])
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
        self.load_progress()
        # Read from file USA-road-d.USA.gr and add edges based on distance
        filename = "../data/archive/USA-road-d.USA.gr"
        with open(filename, 'r') as file:
            for line_number, line in enumerate(file, 1):
                if line_number <= self.last_processed_line:
                    continue

                if line.startswith('a'):
                    tokens = line.split()
                    from_id = int(tokens[1])
                    to_id = int(tokens[2])

                    if from_id > size or to_id > size:
                        continue

                    distance,duration = self.api_call_to_get_edge_weight(from_id, to_id)
                    weight = (distance , duration)

                    if write_to_file:
                        with open(f"../data/world/edges_{version}.txt", 'a') as file:
                            file.write(f"{from_id} {to_id} {distance} {duration}\n")

                    node1 = self.graph.get_node_by_id(from_id)
                    node2 = self.graph.get_node_by_id(to_id)
                    edge = Edge(node1, node2, weight)
                    self.graph.add_edge(edge)

                self.last_processed_line = line_number
                self.save_progress(line_number)

        print(f"Number of edges: {len(self.graph.edges)}")


    def extract_dataset(self, size, write_to_file):
        
        self.extract_nodes(size,write_to_file)
        self.extract_edges(size,write_to_file)     
        return self.graph


if __name__ == "__main__":
    dataset_extractor = DatasetExtractor()
    size = 25000
    graph = dataset_extractor.extract_dataset(size, True)
    print("Graph created successfully!")
