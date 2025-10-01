import json
import csv

def test_risk_classification_logic(tmp_path, monkeypatch):
    from optimizer.analytics import risk_classifiers as rc

    # --- Mock file paths ---
    monkeypatch.setattr(rc, 'CTX', tmp_path / "context_db.jsonl")
    monkeypatch.setattr(rc, 'AVAIL', tmp_path / "audit" / "availability.csv")
    monkeypatch.setattr(rc, 'RISKJ', tmp_path / "audit" / "risk_index.jsonl")
    monkeypatch.setattr(rc, 'RISKM', tmp_path / "docs" / "RISK.md")

    # Create directories for audit and docs
    (tmp_path / "audit").mkdir()
    (tmp_path / "docs").mkdir()

    # --- Create mock data ---
    mock_context_data = [
        # High entropy
        {"fingerprint": "fp1", "ts": "2023-01-01T00:00:00Z", "entropy": 0.8, "reroute_depth": 1, "payload": {"text": "normal text"}},
        # Deep reroute
        {"fingerprint": "fp2", "ts": "2023-01-01T00:01:00Z", "entropy": 0.5, "reroute_depth": 5, "payload": {"text": "normal text"}},
        # PII leak
        {"fingerprint": "fp3", "ts": "2023-01-01T00:02:00Z", "entropy": 0.5, "reroute_depth": 1, "payload": {"text": "my ssn is 123-456-7890"}},
        # Model failure
        {"fingerprint": "fp4", "ts": "2023-01-01T00:03:00Z", "entropy": 0.5, "reroute_depth": 1, "payload": {"error": "upstream provider fail"}},
        # No risk
        {"fingerprint": "fp5", "ts": "2023-01-01T00:04:00Z", "entropy": 0.1, "reroute_depth": 0, "payload": {"text": "this is fine"}},
    ]
    with (tmp_path / "context_db.jsonl").open("w") as f:
        for item in mock_context_data:
            f.write(json.dumps(item) + "\n")

    mock_availability_data = [
        # Latency spike
        {"task": "task1", "success": "1", "latency_ms": "5000"},
        # Failure
        {"task": "task2", "success": "0", "latency_ms": "100"},
        # OK
        {"task": "task3", "success": "1", "latency_ms": "200"},
    ]
    with (tmp_path / "audit" / "availability.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["task", "success", "latency_ms"])
        writer.writeheader()
        writer.writerows(mock_availability_data)

    # --- Run classification ---
    risks = rc.classify()

    # --- Assertions ---
    assert len(risks) == 6 # 4 from context, 2 from availability

    # Check for specific labels
    risk_labels = {r["fingerprint"]: r["labels"] for r in risks}
    assert "high_entropy" in risk_labels["fp1"]
    assert "deep_reroute" in risk_labels["fp2"]
    assert "pii_leak" in risk_labels["fp3"]
    assert "model_failure" in risk_labels["fp4"]
    assert "fp5" not in risk_labels # No risk

    assert any(r["labels"] == ["latency_spike"] for r in risks if r["fingerprint"].startswith("avail:"))
    assert any(r["labels"] == ["failure"] for r in risks if r["fingerprint"].startswith("avail:"))

    # --- Test output writing ---
    rc.write_outputs(risks)
    assert (tmp_path / "audit" / "risk_index.jsonl").exists()
    assert (tmp_path / "docs" / "RISK.md").exists()

    # Verify markdown content
    md_content = (tmp_path / "docs" / "RISK.md").read_text()
    assert "high_entropy | 1" in md_content
    assert "latency_spike | 1" in md_content
    assert "failure | 1" in md_content