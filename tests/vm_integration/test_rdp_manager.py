import pytest

# --- Test Suite for the RDP Manager ---

def test_rdp_manager_module_imports_without_extras():
    """
    Smoke Test: Ensures the rdp_manager module can be imported even if optional
    dependencies ('[vm]' extra) are not installed. This validates the
    guarded import logic.
    """
    try:
        from optimizer.vm_integration import rdp_manager
    except ImportError as e:
        pytest.fail(
            "Failed to import the rdp_manager module without optional dependencies. "
            f"The guarded imports may be faulty. Error: {e}"
        )

# Mark the next test as skippable if the 'docker' dependency is not found.
# This serves as a proxy to check if the '[vm]' extra was installed.
vm_deps_installed = False
try:
    import docker
    import psutil
    vm_deps_installed = True
except ImportError:
    pass

@pytest.mark.skipif(not vm_deps_installed, reason="Requires '[vm]' optional dependencies (e.g., docker, psutil)")
def test_rdp_manager_initializes_with_extras_installed():
    """
    Functional Test: Checks if the RDPManager class can be instantiated
    when the optional '[vm]' dependencies are present.
    """
    from optimizer.vm_integration.rdp_manager import RDPManager

    try:
        manager = RDPManager()
        # Check that a core attribute is initialized
        assert manager.platform is not None
        assert isinstance(manager.config, dict)
    except Exception as e:
        pytest.fail(
            "Failed to instantiate RDPManager even though '[vm]' dependencies seem to be installed. "
            f"Error: {e}"
        )