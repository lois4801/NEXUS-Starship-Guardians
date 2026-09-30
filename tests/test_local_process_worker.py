from pathlib import Path

import pytest

from nexus_os.workers import ProcessPolicy


def test_workspace_policy_rejects_escape(tmp_path: Path):
    policy = ProcessPolicy(
        workspace_root=tmp_path,
        allowed_executables=frozenset({"python"}),
    )
    assert policy.resolve_workspace(".") == tmp_path.resolve()
    with pytest.raises(ValueError, match="escapes configured root"):
        policy.resolve_workspace("../outside")
