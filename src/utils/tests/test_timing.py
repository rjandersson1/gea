import time
import pytest
from src.utils.timing import RateLimiter, LoopProfiler


class TestRateLimiter:

    def test_sleep_maintains_approximate_rate(self):
        hz = 10.0
        limiter = RateLimiter(hz)
        n_iterations = 5
        t_start = time.time()
        for _ in range(n_iterations):
            time.sleep(0.01)    # simulate loop work
            limiter.sleep()
        elapsed = time.time() - t_start
        expected = n_iterations / hz
        assert abs(elapsed - expected) < 0.05    # 50ms tolerance

    def test_no_sleep_if_loop_overruns(self):
        limiter = RateLimiter(10.0)
        time.sleep(0.2)          # simulate overrun (longer than 0.1s period)
        t0 = time.time()
        limiter.sleep()          # should return immediately, not sleep
        assert time.time() - t0 < 0.05


class TestLoopProfiler:

    def test_report_empty(self):
        profiler = LoopProfiler()
        report = profiler.report()
        assert report['n_samples'] == 0
        assert report['mean_ms'] == 0

    def test_report_single_tick(self):
        profiler = LoopProfiler()
        profiler.tick()
        report = profiler.report()
        assert report['n_samples'] == 0    # need at least 2 ticks for 1 interval

    def test_report_correct_duration(self):
        profiler = LoopProfiler()
        for _ in range(5):
            profiler.tick()
            time.sleep(0.05)      # 50ms per iteration
        report = profiler.report()
        assert report['n_samples'] == 4
        assert abs(report['mean_ms'] - 50.0) < 10.0    # within 10ms

    def test_report_keys_present(self):
        profiler = LoopProfiler()
        profiler.tick()
        profiler.tick()
        report = profiler.report()
        assert set(report.keys()) == {'mean_ms', 'p95_ms', 'max_ms', 'n_samples'}