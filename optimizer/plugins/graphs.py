from optimizer.universal import command
import sys, subprocess

@command("graph-service")
def graph_service(args=None) -> int:
    return subprocess.call([sys.executable, "-m", "optimizer.graphs.service_graph"])

@command("graph-code")
def graph_code(args=None) -> int:
    return subprocess.call([sys.executable, "-m", "optimizer.graphs.code_graph"])

@command("graph-all")
def graph_all(args=None) -> int:
    a = graph_service(args)
    b = graph_code(args)
    return a or b

def main():
    """Entry point for the graph-all script."""
    graph_all()

if __name__ == "__main__":
    main()