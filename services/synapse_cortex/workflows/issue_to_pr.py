from datetime import timedelta
from temporalio import workflow

# Import activity stubs
from services.synapse_cortex.activities.policy_activities import evaluate_policy

# Mock other activities for this example
# from .activities import ensure_audit_anchor, dispatch_jules_merge, get_scan_report


# Since other activities are not defined, we'll create mock stubs for them
# In a real scenario, these would be imported from their respective activity files.
@workflow.activity
async def ensure_audit_anchor(data: dict) -> dict: ...
@workflow.activity
async def dispatch_jules_merge(data: dict) -> dict: ...
@workflow.activity
async def get_scan_report(data: dict) -> dict: ...


@workflow.defn
class IssueToPRWorkflow:
    @workflow.run
    async def run(self, issue_data: dict) -> str:
        workflow.logger.info("Starting IssueToPRWorkflow...")

        # 1. & 2. Mocking initial steps like PR creation and security scanning
        pr = {"pr_number": 123, "branch": "feature-branch"}
        scan_report = await workflow.execute_activity(
            get_scan_report,
            {"branch": pr["branch"]},
            start_to_close_timeout=timedelta(minutes=5),
        )

        # 3. Audit Anchoring
        audit_anchor = await workflow.execute_activity(
            ensure_audit_anchor,
            {"pr_number": pr["pr_number"]},
            start_to_close_timeout=timedelta(minutes=2),
        )

        # 4. OPA Policy Evaluation
        policy_input = {
            "security_scan": scan_report,
            "audit_anchor": audit_anchor,
            "requester_role": "engineer",  # Placeholder: This could be determined dynamically
        }

        workflow.logger.info(f"Evaluating merge policy with input: {policy_input}")
        policy_result = await workflow.execute_activity(
            evaluate_policy,
            args=["synapse.cortex.merge_control", policy_input],
            start_to_close_timeout=timedelta(minutes=1),
        )

        # 5. Enforce Decision
        if policy_result.get("allow_merge", False):
            workflow.logger.info("Policy check passed. Proceeding to merge.")
            merge_task = await workflow.execute_activity(
                dispatch_jules_merge,
                {"pr_number": pr["pr_number"]},
                start_to_close_timeout=timedelta(minutes=10),
            )
            return f"Merged PR #{pr['pr_number']}. Policy PASS. Merge task ID: {merge_task['id']}"
        else:
            # Utilize the denial reasons from the OPA policy for clear feedback
            reasons = policy_result.get(
                "deny_reason", ["Policy denied merge for an unspecified reason."]
            )
            reasons_str = "; ".join(reasons)
            workflow.logger.warning(
                f"Merge blocked by OPA policy. Reasons: {reasons_str}"
            )
            # Potentially trigger a human-in-the-loop (HITL) workflow for manual review
            return f"PR #{pr['pr_number']} Blocked. Reasons: {reasons_str}"
