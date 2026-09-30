from nexus_os.verification_pipeline import default_node_gates, default_python_gates


def test_default_python_gates_are_structured_argv():
    gates = default_python_gates()
    assert [gate.name for gate in gates] == ["ruff", "pytest"]
    assert gates[0].argv == ["ruff", "check", "."]
    assert gates[1].argv == ["pytest", "-q"]


def test_default_node_gates_are_structured_argv():
    gates = default_node_gates()
    assert [gate.name for gate in gates] == ["lint", "test"]
    assert gates[0].argv[0] == "npm"
    assert gates[1].argv[0] == "npm"
