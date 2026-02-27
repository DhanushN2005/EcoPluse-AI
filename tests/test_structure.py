def test_package_import():
    import ecopulse_ai

    assert hasattr(ecopulse_ai, "__version__")
