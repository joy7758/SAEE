#!/usr/bin/env python3
"""Run the local Phase 9 commercial assessment projection."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from saee_backend.services.commercial_assessment_service import generate_commercial_assessment_path


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    response=generate_commercial_assessment_path(args.input)
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(response,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SAEE_COMMERCIAL_ASSESSMENT_SERVICE_RESULT")
    print(f"selected_runs={response['scope_summary']['selected_runs']}")
    print(f"evidence_supported={response['evidence_summary']['supported']}")
    print(f"evidence_insufficient={response['evidence_summary']['insufficient']}")
    print(f"evidence_not_assessed={response['evidence_summary']['not_assessed']}")
    print("commercial_delivery_completed=false")
    print("deployment_authorized=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
