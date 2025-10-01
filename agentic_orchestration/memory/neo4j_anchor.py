import time
from neo4j import GraphDatabase


class Neo4jAnchor:
    def __init__(self, uri, user, password):
        # In a real implementation, these would come from a config file.
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def anchor(self, cycle, fingerprint, mutation):
        """
        Anchors a mutation to a cycle in the Neo4j graph.
        """
        with self._driver.session() as session:
            session.write_transaction(
                self._create_mutation_and_cycle, cycle, fingerprint, mutation
            )

    @staticmethod
    def _create_mutation_and_cycle(tx, cycle, fingerprint, mutation):
        query = (
            "MERGE (c:Cycle {id: $cycle}) "
            "CREATE (m:Mutation {fingerprint: $fp, code: $mutation, timestamp: $ts}) "
            "MERGE (c)-[:GENERATED]->(m)"
        )
        tx.run(query, cycle=cycle, fp=fingerprint, mutation=mutation, ts=time.time())
