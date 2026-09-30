import pytest

from nexus_os.failure_taxonomy import FailureCategory, FailureSignal, classify_failure


def test_classify_security_failure():
    signal = classify_failure(error="TLS security verification disabled")
    assert signal.category == FailureCategory.SAFETY
    assert signal.severity == 5


def test_regression_takes_priority():
    signal = classify_failure(error="timeout", regression=True)
    assert signal.category == FailureCategory.REGRESSION
    assert signal.severity == 5


def test_failure_signal_validates_severity():
    with pytest.raises(ValueError):
        FailureSignal(FailureCategory.UNKNOWN, "bad", 6)
