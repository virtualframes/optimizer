import httpx
from temporalio import activity
import os

# OPA service endpoint within the K8s cluster (deployed via Helm)
# The service name deployed by the Helm chart is typically 'opa'.
OPA_URL = os.getenv("OPA_URL", "http://opa.synapse-system.svc.cluster.local:8181")


@activity.defn
async def evaluate_policy(policy_path: str, input_data: dict) -> dict:
    """
    Queries the OPA service to evaluate a policy using an async HTTP client.

    Args:
        policy_path: The dot-separated path to the policy rule (e.g., 'synapse.cortex.merge_control').
        input_data: The JSON-serializable input data for the policy.

    Returns:
        A dictionary containing the policy evaluation result.
    """
    # Convert dot notation path to a URL path for the OPA REST API
    url = f"{OPA_URL}/v1/data/{policy_path.replace('.', '/')}"
    activity.logger.info(f"Querying OPA at {url} with input: {input_data}")

    try:
        # Use an async client for non-blocking I/O
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(url, json={"input": input_data})
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json().get("result", {})
        activity.logger.info(f"OPA evaluation successful. Result: {result}")
        return result

    except httpx.TimeoutException:
        activity.logger.error(f"OPA request timed out after 5 seconds.")
        raise  # Re-raise to allow Temporal to handle the retry
    except httpx.RequestError as e:
        activity.logger.error(f"Error calling OPA service: {e}")
        # This could be a network issue, DNS failure, or an HTTP error status.
        raise  # Re-raise to allow Temporal retry logic to take effect
