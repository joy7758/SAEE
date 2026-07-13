#!/usr/bin/env python3
"""运行百度千帆参与的 SAEE 有状态合成业务世界演练。"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_backend.services.stateful_business_rehearsal import StatefulRehearsalError, run_stateful_business_rehearsal  # noqa: E402
from scripts.saee_qianfan_mcp_host import ProviderError, QianfanClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="运行一个千帆真实推理模型参与的有状态合成业务演练。")
    parser.add_argument("--scenario", required=True, type=Path)
    parser.add_argument("--write-run", type=Path)
    args = parser.parse_args()
    try:
        run = run_stateful_business_rehearsal(args.scenario, QianfanClient(), real_reasoning_model_called=True)
        if args.write_run is not None:
            target = args.write_run.resolve()
            allowed = (ROOT / "output/stateful-business-rehearsal").resolve()
            if target.parent != allowed:
                raise StatefulRehearsalError("STATEFUL_REHEARSAL_OUTPUT_OUTSIDE_ALLOWLIST", str(args.write_run))
            allowed.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (StatefulRehearsalError, ProviderError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        code = getattr(exc, "code", getattr(exc, "category", "STATEFUL_REHEARSAL_FAILED"))
        print(json.dumps({"status": "FAIL", "reason_code": code, "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS", "result_type": "SAEE_STATEFUL_BUSINESS_REHEARSAL_RUN", "run": run}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

