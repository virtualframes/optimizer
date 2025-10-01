def test_lineage_and_graph(tmp_path, monkeypatch):
    from optimizer.resilience import entropy as e
    e.main()  # writes audit + prints mutated
    from optimizer.dev import mermaid_lineage as ml
    ml.main()
    from optimizer.dev import service_graph as sg
    sg.main()