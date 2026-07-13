# Calibration Import And Score Guide

After human fills `CALIBRATION_RESULT_ENTRY.json`, run:

```bash
python3 scripts/import_external_ai_calibration_results.py
python3 scripts/score_external_ai_calibration_results.py
python3 scripts/saee_external_ai_calibration_run_smoke.py
python3 scripts/mainline_guard.py
make check
```

The import step copies human-entered results into `CALIBRATION_RESULTS.json`.
The scoring step computes calibration metrics.

No external calls are made by scripts.
