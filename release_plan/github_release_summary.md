# GitHub Release Summary

Status: local GitHub-ready subset, not released.

## Package Path

```text
github_release/
```

## Included Files

- `README.md`
- `experiment_layer/experiment_runner_stub.py`
- `experiment_layer/logging_tools.py`
- `analysis_layer/regime_classifier_stub.py`
- `analysis_layer/attractor_mapper_stub.py`
- `demo/minimal_evolution_demo.py`

## Disclosure Level

Public abstraction layer only.

The package is runnable as a toy demonstration:

```bash
python3 github_release/demo/minimal_evolution_demo.py
```

## Boundary

The GitHub subset must remain independent from:

- `saee_v1_0/`
- `kernel/`
- private fitness code;
- private selection code;
- private lineage code;
- private mutation/reproduction code;
- private runtime orchestration.

## Current Release Status

```text
github_release_created: false
git_tag_created: false
git_push_performed: false
package_uploaded: false
```

