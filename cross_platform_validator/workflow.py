import asyncio
from datetime import timedelta

from temporalio import activity, workflow

# This is now a clean, relative import within our new package.
from .validator import CrossPlatformValidator


@activity.defn
async def run_validation_activity(repo_path: str) -> str:
    """
    An activity that runs the CrossPlatformValidator on a given repository path.
    """
    activity.logger.info(f"Running cross-platform validation on repo: {repo_path}")

    validator = CrossPlatformValidator(repo_path)

    # Run the synchronous validator in an executor to avoid blocking the event loop.
    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, validator.run_all)

    result_message = f"Validation completed for {repo_path}."
    activity.logger.info(result_message)
    return result_message


@workflow.defn
class CrossPlatformValidationWorkflow:
    """A Temporal Workflow to manage the cross-platform validation process."""

    @workflow.run
    async def run(self, repo_path: str) -> str:
        """
        Executes the cross-platform validation workflow.
        """
        workflow.logger.info(f"Starting cross-platform validation for repository: {repo_path}")

        result = await workflow.execute_activity(
            run_validation_activity,
            repo_path,
            start_to_close_timeout=timedelta(minutes=10),
        )

        workflow.logger.info("Cross-platform validation workflow completed.")
        return result