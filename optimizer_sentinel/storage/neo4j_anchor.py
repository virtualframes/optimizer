import os
from neo4j import GraphDatabase

class Neo4jAdapter:
    def __init__(self):
        """
        Initializes the Neo4j adapter with credentials from environment variables.
        """
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, user, password]):
            raise ValueError("NEO4J_URI, NEO4J_USER, and NEO4J_PASSWORD environment variables must be set.")

        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def _execute_write(self, query, **params):
        with self._driver.session() as session:
            result = session.write_transaction(lambda tx: tx.run(query, **params).data())
            return result

    def anchor_event(self, task_id: str, patch: dict, pr_url: str):
        """
        Anchors a debug and patch event in Neo4j, creating nodes for the task,
        patch, and pull request, and linking them together.
        """
        query = """
        MERGE (t:JulesTask {id: $task_id})
        CREATE (p:Patch {message: $patch_message, diff: $patch_diff, timestamp: timestamp()})
        CREATE (pr:PullRequest {url: $pr_url, timestamp: timestamp()})
        MERGE (t)-[:GENERATED]->(p)
        MERGE (p)-[:RESULTED_IN]->(pr)
        RETURN t, p, pr
        """
        return self._execute_write(
            query,
            task_id=task_id,
            patch_message=patch.get('message', 'N/A'),
            patch_diff=patch.get('diff', 'N/A'),
            pr_url=pr_url
        )

    def anchor_forecast(self, source: str, forecast: dict, patch: dict):
        """
        Anchors a forecast event in Neo4j.
        """
        query = """
        MERGE (s:Source {name: $source})
        CREATE (f:Forecast {details: $forecast_details, timestamp: timestamp()})
        CREATE (p:Patch {message: $patch_message, diff: $patch_diff, timestamp: timestamp()})
        MERGE (s)-[:TRIGGERED]->(f)
        MERGE (f)-[:LED_TO]->(p)
        RETURN s, f, p
        """
        return self._execute_write(
            query,
            source=source,
            forecast_details=str(forecast),
            patch_message=patch.get('message', 'N/A'),
            patch_diff=patch.get('diff', 'N/A')
        )

# Singleton instance to be used by the application
neo4j_adapter = Neo4jAdapter()

def anchor_event(task_id, patch, pr):
    pr_url = getattr(pr, 'html_url', str(pr)) # PyGithub uses html_url
    neo4j_adapter.anchor_event(task_id, patch, pr_url)

def anchor_forecast(source, forecast, patch):
    neo4j_adapter.anchor_forecast(source, forecast, patch)