# services/synapse_cortex/activities/prompt.py
from temporalio import activity

@activity.defn
def send_prompt_to_jules(payload: dict) -> dict:
    """
    An activity to send a prompt to the Jules agent.

    This is a scaffold and currently just logs the received payload.
    In a real implementation, this would trigger a call to the Jules agent.
    """
    activity.logger.info(f"Received prompt payload: {payload}")
    # In a real scenario, you might return a confirmation or result
    return {"status": "received", "task_id": payload.get("taskid")}