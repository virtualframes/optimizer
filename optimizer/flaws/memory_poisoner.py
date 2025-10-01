# FLAWMODE: Memory Poisoner
# This module simulates flaws that corrupt the agent's internal state or memory.
# It tests the agent's ability to detect and recover from corrupted memory,
# which could be caused by parsing errors, data degradation, or other anomalies.

def corrupt_memory_json(memory_dict):
    """
    Simulates corruption of a JSON-like memory structure (a Python dict).
    It might replace a valid value with one of a different, unexpected type.
    """
    if "agent_state" in memory_dict:
        print("MEMORY FLAW: Corrupting agent_state from dict to string.")
        memory_dict["agent_state"] = "INVALID_STATE_TYPE"
    return memory_dict

def introduce_contradictory_facts(knowledge_base):
    """
    Simulates a flaw where contradictory information is added to a knowledge base.
    The agent must be able to resolve or at least identify the contradiction.
    """
    if isinstance(knowledge_base, list):
        fact = {"id": "fact-001", "statement": "sky_is_blue"}
        contradiction = {"id": "fact-002", "statement": "sky_is_not_blue"}
        if fact in knowledge_base:
            print("MEMORY FLAW: Introducing contradictory fact.")
            knowledge_base.append(contradiction)
    return knowledge_base

def wipe_critical_memory_node(memory_graph):
    """
    Simulates the loss of a critical piece of information from a graph-based memory.
    """
    if "critical_node_id" in memory_graph:
        node_id = memory_graph["critical_node_id"]
        if node_id in memory_graph.get("nodes", {}):
            print(f"MEMORY FLAW: Wiping critical memory node '{node_id}'.")
            del memory_graph["nodes"][node_id]
    return memory_graph