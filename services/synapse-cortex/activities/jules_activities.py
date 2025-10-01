from temporalio import activity
from agents.jules.debugandpatch import debug_and_patch

@activity.defn
async def auto_debug_and_patch(failure_context: str, source: str) -> str:
    """
    Temporal activity wrapper for the Jules auto-debugging and patching agent.
    """
    activity.logger.info(f"Starting auto-debug and patch for source: {source}")

    # The debug_and_patch function is synchronous, so we run it in a separate thread
    # to avoid blocking the async event loop of the activity worker.
    # In a real-world scenario with I/O-bound operations in the agent,
    # it would be better to make the agent's functions async.
    pr_url = await activity.run_in_thread(
        lambda: debug_and_patch(failure_context, source)
    )

    activity.logger.info(f"Auto-debug and patch completed. PR URL: {pr_url}")
    return pr_url