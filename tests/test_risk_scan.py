def test_risk_outputs_smoke(tmp_path, monkeypatch):
    from optimizer.analytics import risk_classifiers as rc
    rc.write_outputs([]) # should still write files
    assert (rc.RISKM).exists() and (rc.RISKJ).exists()