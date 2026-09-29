import pytest

from nexus_os.storage import Store
from nexus_os.tools import ToolError, run_tool


def test_calculator_safe():
    store = Store(":memory:")
    assert run_tool("calculator", {"expression": "(12+3)*4"}, "any", store)["result"] == 60
    for expression in ["__import__('os').system('id')", "2**100000", "1/0", "999999999999999"]:
        with pytest.raises(ToolError):
            run_tool("calculator", {"expression": expression}, "any", store)
