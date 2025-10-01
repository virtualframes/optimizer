from .jules_agent import JulesAgent

def run_mission(prompt):
    agent = JulesAgent()
    result = agent.dispatch(prompt)
    audit = agent.audit()
    return {
        "result": result,
        "audit": audit
    }