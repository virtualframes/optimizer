import networkx as nx
import json

class XBOWGraphBuilder:
    def __init__(self):
        self.graph = nx.MultiDiGraph()

    def add_node(self, node_id, node_type):
        self.graph.add_node(node_id, type=node_type)

    def add_edge(self, src, dst, label):
        self.graph.add_edge(src, dst, label=label)

    def build_from_trace(self, trace_path):
        with open(trace_path) as f:
            trace_data = json.load(f)

        for entry in trace_data:
            source_js = entry.get("source")
            if source_js:
                self.add_node(source_js, "javascript_source")
                for endpoint in entry.get("endpoints", []):
                    self.add_node(endpoint, "api_endpoint")
                    self.add_edge(source_js, endpoint, "calls")

    def export(self, path="xbow_graph.json"):
        data = nx.json_graph.node_link_data(self.graph)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)