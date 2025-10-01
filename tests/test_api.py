from fastapi.testclient import TestClient
from optimizer.api.main import app
import unittest

client = TestClient(app)


class TestApi(unittest.TestCase):
    def test_health_check(self):
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_ingest_node(self):
        response = client.post(
            "/ingest/node",
            json={
                "node_id": "test_node_ingest",
                "position": [1, 2, 3],
                "velocity": [0.1, 0.2, 0.3],
                "metadata": {"key": "value"},
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {
                "message": "Node ingested successfully",
                "node_id": "test_node_ingest",
            },
        )

    def test_query_node(self):
        # First, ingest a node to query to ensure this test is self-contained
        node_data = {
            "node_id": "test_node_query",
            "position": [4, 5, 6],
            "velocity": [0.4, 0.5, 0.6],
            "metadata": {"source": "test_query_node"},
        }
        client.post("/ingest/node", json=node_data)

        response = client.get(f"/query/node/{node_data['node_id']}")
        self.assertEqual(response.status_code, 200)

        # The API should return the full node data, including the new velocity field
        expected_data = node_data.copy()
        self.assertEqual(response.json(), expected_data)

    def test_query_nonexistent_node(self):
        response = client.get("/query/node/nonexistent_node_12345")
        self.assertEqual(response.status_code, 404)

    def test_ingest_credential(self):
        response = client.post(
            "/ingest/credential",
            json={"source_node_id": "node_a_cred", "target_node_id": "node_b_cred"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(), {"message": "Credential ingested successfully"}
        )

    def test_query_auth_matrix(self):
        # Ingest credentials to make the test self-contained
        source_id = "node_c_matrix"
        target_id = "node_d_matrix"
        client.post(
            "/ingest/credential",
            json={"source_node_id": source_id, "target_node_id": target_id},
        )

        response = client.get("/query/auth_matrix")
        self.assertEqual(response.status_code, 200)

        # Check that the ingested credential exists in the matrix
        auth_matrix = response.json()
        self.assertIn(source_id, auth_matrix)
        self.assertIn(target_id, auth_matrix[source_id])