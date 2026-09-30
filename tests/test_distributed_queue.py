import pytest

from nexus_os.distributed_queue import CLAIM_SQL, POSTGRES_QUEUE_DDL, LeasePolicy


def test_postgres_queue_uses_skip_locked_and_lease_columns():
    assert "FOR UPDATE SKIP LOCKED" in CLAIM_SQL
    assert "lease_expires_at" in POSTGRES_QUEUE_DDL
    assert "heartbeat_at" in POSTGRES_QUEUE_DDL


def test_lease_policy_validates_values():
    with pytest.raises(ValueError):
        LeasePolicy(lease_seconds=0)
    with pytest.raises(ValueError):
        LeasePolicy(retry_delay_seconds=-1)
