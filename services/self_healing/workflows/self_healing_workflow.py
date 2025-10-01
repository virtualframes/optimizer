from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from ..activities.bug_bounty_ingestion import ingest_bug_bounty_data


@workflow.defn
class SelfHealingWorkflow:
    @workflow.run
    async def run(self):
        return await workflow.execute_activity(
            ingest_bug_bounty_data,
            start_to_close_timeout=timedelta(minutes=5),
        )
