# Backward Compatibility Map

## v0.1 to v0.4

| v0.1 surface | v0.4 compatibility |
| --- | --- |
| `kernel/examples/seed_genome.json` | Used as the default v0.4 founder genome. |
| `kernel/runtime.py` | Remains runnable; v0.4 does not replace it. |
| `scripts/kernel_smoke.py` | Still part of `make check`. |

## v0.2 to v0.4

| v0.2 surface | v0.4 compatibility |
| --- | --- |
| Population pool | Preserved as multi-lineage population state. |
| Abstract signal stream | Preserved as abstract signal objects in local runtime. |
| Dynamic fitness | Lifted into mutable fitness geometry. |
| Selection pressure | Lifted into mutable selection topology. |
| Lineage graph | Extended with evolution-space graph, phase events, and regime events. |
| `scripts/kernel_v0_2_smoke.py` | Still part of `make check`. |

## v0.3 to v0.4

| v0.3 surface | v0.4 compatibility |
| --- | --- |
| Meta-evolution boundary | Preserved, but mutable object shifts from rule genome to evolution space. |
| Population mode | Preserved; v0.4 smoke rejects population collapse. |
| Drift boundary | Preserved as hard runtime boundaries in run record. |
| Counterfactual framing | Not removed; v0.4 adds phase-transition space dynamics as a new local runtime. |
| `scripts/saee_v0_3_smoke.py` | Still part of `make check`. |

## Non-Breaking Policy

v0.4 is additive. Existing local commands remain valid:

```bash
python3 -m kernel.runtime --generations 3 --output-dir kernel/output/demo-run
python3 -m kernel_v0_2.runtime_v0_2 --generations 4 --output-dir kernel_v0_2/output/demo-run
python3 saee_v0_3/KERNEL_BOOTSTRAP_SCRIPT.py --generations 3 --output-dir saee_v0_3/output/demo-run
```

New v0.4 command:

```bash
python3 saee_v0_4/KERNEL_BOOTSTRAP_SCRIPT.py --generations 5 --output-dir saee_v0_4/output/demo-run
```
