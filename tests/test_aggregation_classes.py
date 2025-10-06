"""Testing aggregation classes."""

from __future__ import annotations

from scruby.aggregation import Average, Counter, Max, Min, Sum


def test_average_int() -> None:
    """Test a Average class."""
    avg = Average()
    avg.set(5)
    avg.set(10)
    avg.set(15)
    assert int(avg.get()) == 10.0


def test_average_float() -> None:
    """Test a Average class."""
    avg = Average()
    avg.set(5.0)
    avg.set(10.0)
    avg.set(15.0)
    assert float(avg.get()) == 10.0


def test_counter() -> None:
    """Test a Counter class."""
    counter = Counter(2)
    assert not counter.check()
    counter.next()
    assert not counter.check()
    counter.next()
    assert counter.check()


def test_max_int() -> None:
    """Test a Max class."""
    max_num = Max()
    max_num.set(5)
    max_num.set(10)
    max_num.set(15)
    assert max_num.get() == 15


def test_max_float() -> None:
    """Test a Max class."""
    max_num = Max()
    max_num.set(5.0)
    max_num.set(10.0)
    max_num.set(15.0)
    assert max_num.get() == 15.0


def test_min_int() -> None:
    """Test a Min class."""
    max_num = Min()
    max_num.set(5)
    max_num.set(10)
    max_num.set(15)
    assert max_num.get() == 5


def test_min_float() -> None:
    """Test a Min class."""
    max_num = Min()
    max_num.set(5.0)
    max_num.set(10.0)
    max_num.set(15.0)
    assert max_num.get() == 5.0


def test_sum_int() -> None:
    """Test a Sum class."""
    sum_num = Sum()
    sum_num.set(5)
    sum_num.set(10)
    sum_num.set(15)
    assert int(sum_num.get()) == 30


def test_sum_float() -> None:
    """Test a Sum class."""
    sum_num = Sum()
    sum_num.set(5.0)
    sum_num.set(10.0)
    sum_num.set(15.0)
    assert float(sum_num.get()) == 30.0
