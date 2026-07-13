# Backward Compatibility Map

## v0.1 to v0.6

| v0.1 surface | v0.6 compatibility |
| --- | --- |
| `kernel/examples/seed_genome.json` | Used as the default founder genome through v0.5 runtime. |
| `kernel/runtime.py` | Remains runnable; v0.6 does not replace it. |
| `scripts/kernel_smoke.py` | Still part of `make check`. |

## v0.5 to v0.6

| v0.5 surface | v0.6 compatibility |
| --- | --- |
| Generated evolution laws | Observed through rule genesis records and rule ancestry graph. |
| Generated fitness functions | Explained through fitness interpretability records. |
| Selection mechanisms | Explained through selection outcome records. |
| Dimensions | Observed through dimension birth/merge/collapse causes. |
| Regimes | Observed through semantic lineage and self-description. |
| Hypergraph | Extended with semantic lineage graph, not modified in place. |

## Non-Breaking Policy

v0.6 is additive. Existing local commands remain valid:

```bash
python3 -m kernel.runtime --generations 3 --output-dir kernel/output/demo-run
python3 -m kernel_v0_2.runtime_v0_2 --generations 4 --output-dir kernel_v0_2/output/demo-run
python3 saee_v0_3/KERNEL_BOOTSTRAP_SCRIPT.py --generations 3 --output-dir saee_v0_3/output/demo-run
python3 saee_v0_4/KERNEL_BOOTSTRAP_SCRIPT.py --generations 5 --output-dir saee_v0_4/output/demo-run
python3 saee_v0_5/bootstrap/v0_5_bootstrap.py --generations 6 --output-dir saee_v0_5/output/demo-run
```

New v0.6 command:

```bash
python3 saee_v0_6/bootstrap/v0_6_bootstrap.py --generations 6 --output-dir saee_v0_6/output/demo-run
```
