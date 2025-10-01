from datetime import timedelta
from temporalio import workflow

# Import all activities from the jules agent module
from optimizer_sentinel.agents import jules as jules_activities

@workflow.defn
class DebugAndPatchWorkflow:
    @workflow.run
    async def run(self, task: dict) -> dict:
        """
        Workflow to orchestrate the debug and patch process by calling activities.
        """
        # 1. Diagnose the error
        error = await workflow.execute_activity(
            jules_activities.diagnose,
            task["body"],
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 2. Generate a patch
        patch = await workflow.execute_activity(
            jules_activities.generate_patch,
            error,
            task,
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 3. Commit the patch and create a pull request
        pr_url = await workflow.execute_activity(
            jules_activities.commit_and_create_pr,
            task["repo"],
            task["branch"],
            patch,
            start_to_close_timeout=timedelta(minutes=10),
        )

        # 4. Anchor the event in Neo4j
        await workflow.execute_activity(
            jules_activities.anchor_event_activity,
            task["id"],
            patch,
            pr_url,
            start_to_close_timeout=timedelta(minutes=2),
        )

        result = {"pr_url": pr_url, "status": "patched"}
        return result