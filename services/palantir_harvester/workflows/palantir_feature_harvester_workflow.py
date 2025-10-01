from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from ..activities.palantir_ingestion import ingest_palantir_features


@workflow.defn
class PalantirFeatureHarvesterWorkflow:
    @workflow.run
    async def run(self):
        return await workflow.execute_activity(
            ingest_palantir_features,
            start_to_close_timeout=timedelta(hours=4),
        )