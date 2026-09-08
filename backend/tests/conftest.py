import pytest

from app.core.rate_limit import rate_limiter


@pytest.fixture(autouse=True)
def reset_rate_limits_between_tests():
    rate_limiter.reset()
    yield
    rate_limiter.reset()
