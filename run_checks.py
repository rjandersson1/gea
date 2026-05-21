import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import time
from src.utils.timing import RateLimiter, LoopProfiler
from src.utils.logger import CSVLogger
from src.utils.config import load_config

# --- test RateLimiter ---
print("testing RateLimiter at 5 Hz for 5 iterations...")
limiter = RateLimiter(hz=5.0)
t_start = time.time()
for i in range(5):
    time.sleep(0.04)    # pretend this is OCR work
    limiter.sleep()
elapsed = time.time() - t_start
print(f"  elapsed: {elapsed:.2f}s  (expected ~1.0s)")

# --- test LoopProfiler ---
print("testing LoopProfiler...")
profiler = LoopProfiler()
for i in range(5):
    profiler.tick()
    time.sleep(0.05)
report = profiler.report()
print(f"  mean loop time: {report['mean_ms']:.1f}ms  (expected ~50ms)")
print(f"  n_samples: {report['n_samples']}  (expected 4)")

# --- test CSVLogger ---
print("testing CSVLogger...")
logger = CSVLogger(
    path='data/logs/test_run.csv',
    fields=['timestamp', 'heading', 'airspeed']
)

for i in range(50):
    logger.log({'timestamp': time.time(), 'heading': 0.0 + i, 'airspeed': 1.0 + i})
logger.close()
print("  wrote data/logs/test_run.csv")
print("  open it in Excel/Numbers to verify")

# --- test config loader ---
print("testing load_config...")
config = load_config('config/rois.yaml')
print(f"  loaded keys: {list(config.keys())}")

print("\nall checks done")