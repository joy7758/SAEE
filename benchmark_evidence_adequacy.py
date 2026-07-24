import time
import json
from saee_backend.services.evidence_adequacy import _profile_valid, _load_profile

def benchmark():
    profile = _load_profile("RESOURCE_AUTHENTICITY")

    start_time = time.time()
    for _ in range(1000):
        _profile_valid(profile)
    end_time = time.time()

    print(f"Time for 1000 iterations: {end_time - start_time:.4f} seconds")

if __name__ == "__main__":
    benchmark()
