#!/usr/bin/env python3
"""运行百度千帆真实推理模型的 SAEE 本地合成世界演练。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.controlled_reasoning_rehearsal import (  # noqa: E402
    ControlledRehearsalError,
    run_controlled_reasoning_rehearsal,
)
from scripts.saee_qianfan_mcp_host import ProviderError, QianfanClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="运行一个千帆真实推理模型参与的 SAEE 受控合成演练。")
    parser.add_argument("--scenario", required=True, type=Path, help="allowlist 内的 v0.2 合成场景")
    parser.add_argument("--write-run", type=Path, help="可选：写入不含凭据的结构化运行结果")
    args = parser.parse_args()
    try:
        run = run_controlled_reasoning_rehearsal(
            args.scenario,
            QianfanClient(),
            external_reasoning_model_called=True,
        )
        if args.write_run is not None:
            target = args.write_run.resolve()
            allowed = (ROOT / "output/controlled-rehearsal").resolve()
            if target.parent != allowed:
                raise ControlledRehearsalError("CONTROLLED_REHEARSAL_OUTPUT_OUTSIDE_ALLOWLIST", str(args.write_run))
            allowed.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (ControlledRehearsalError, ProviderError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        code = getattr(exc, "code", getattr(exc, "category", "CONTROLLED_REHEARSAL_FAILED"))
        print(json.dumps({"status": "FAIL", "reason_code": code, "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS", "result_type": "SAEE_CONTROLLED_REASONING_RUN", "run": run}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

