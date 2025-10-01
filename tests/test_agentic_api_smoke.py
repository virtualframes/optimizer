def test_quorum_prefix_pass():
    from optimizer.resilience.quorum import prefix_validator, validate
    res = validate("[LOCAL_OK:mixtral] hello", 1, [prefix_validator("[LOCAL_OK:")])
    assert res.passed and res.witnesses >= 1