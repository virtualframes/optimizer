import os
import sys

# Get the absolute path of the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add the script's directory to the Python path to allow for imports
# This is necessary so that the script can find the other modules (crawler, agents, etc.)
sys.path.insert(0, script_dir)

from crawler.hiddenapitraceback import HiddenAPITraceback
from benchmarks.api_benchmark import APIBenchmark
from orchestration.agenticflowloop import AgenticFlowLoop
from orchestration.xbowgraphbuilder import XBOWGraphBuilder
from orchestration.xbow_visualizer import visualize_xbow_3d
from agents.selfmutatingagent import SelfMutatingAgent
from config import TARGET_DOCS, SOURCEPATH

# --- Helper function to get absolute path relative to the script ---
def get_abs_path(rel_path):
    return os.path.join(script_dir, rel_path)

# Ensure data directories exist using absolute paths
os.makedirs(get_abs_path("data/traces"), exist_ok=True)
os.makedirs(get_abs_path("data/graphs"), exist_ok=True)
os.makedirs(get_abs_path("data/mutations"), exist_ok=True)

print("--- Step 1: Crawl hidden APIs ---")
# Note: This performs live web requests and may take a moment.
crawler = HiddenAPITraceback(TARGET_DOCS)
crawler.run()
trace_path = get_abs_path("data/traces/hiddenapitrace.json")
crawler.export(trace_path)
print(f"Crawler finished. Trace saved to {trace_path}")

print("\n--- Step 2: Benchmark known endpoints (Placeholder) ---")
benchmark = APIBenchmark()
benchmark.run_all()
benchmark_path = get_abs_path("data/traces/api_benchmark.json")
benchmark.export(benchmark_path)

print("\n--- Step 3: Run agentic orchestration loop (Placeholder) ---")
# This part demonstrates the concept of a self-mutating agent.
abs_source_path = get_abs_path(SOURCEPATH)
mutating_agent = SelfMutatingAgent(abs_source_path)
flow = AgenticFlowLoop(
    endpoint="http://example.com/api",
    payload={"data": "test"},
    headers={"Authorization": "Bearer token"},
    source_path=abs_source_path
)
# The mutate function from the agent is passed to the loop
flow.run_loop(mutation_fn=mutating_agent.mutate, cycles=5)


print("\n--- Step 4: Build and visualize orchestration graph ---")
graph_builder = XBOWGraphBuilder()
# Corrected method name from buildfromtrace to build_from_trace
graph_builder.build_from_trace(trace_path)
graph_path = get_abs_path("data/graphs/xbow_graph.json")
graph_builder.export(graph_path)
print(f"Graph built. Data saved to {graph_path}")

# Note: Matplotlib visualization will open a new window.
# This might not be suitable for all environments (e.g., a headless server).
print("\nAttempting to visualize the graph...")
try:
    # Corrected function name from visualizexbow3d to visualize_xbow_3d
    visualize_xbow_3d(graph_path)
    print("Visualization window launched. Close the window to exit the script.")
except Exception as e:
    print(f"Could not launch visualization. This is expected in a non-GUI environment. Error: {e}")

print("\n--- Run complete ---")