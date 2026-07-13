# Backward Compatibility Map

## v0.1 to v0.5

| v0.1 surface | v0.5 compatibility |
| --- | --- |
| `kernel/examples/seed_genome.json` | Used as the default v0.5 founder genome. |
| `kernel/runtime.py` | Remains runnable; v0.5 does not replace it. |
| `scripts/kernel_smoke.py` | Still part of `make check`. |

## v0.2 to v0.5

| v0.2 surface | v0.5 compatibility |
| --- | --- |
| Population pool | Preserved as multi-lineage population state. |
| Abstract signal stream | Preserved as abstract signal objects only. |
| Dynamic fitness | Lifted into internally generated fitness functions. |
| Selection pressure | Lifted into generated selection mechanisms. |
| Lineage graph | Lifted into a generated physics hypergraph. |

## v0.3 to v0.5

| v0.3 surface | v0.5 compatibility |
| --- | --- |
| Rule genome | Lifted into generated evolution law records. |
| Drift boundary | Preserved as runtime safety boundaries. |
| Counterfactual framing | Preserved as local observation-driven generation, without external execution. |

## v0.4 to v0.5

| v0.4 surface | v0.5 compatibility |
| --- | --- |
| Evolution space mutation | Lifted into generated laws, dimensions, regimes, and selection mechanisms. |
| Fitness geometry | Lifted into generated fitness expression terms. |
| Selection topology | Lifted into evolvable selection mechanisms. |
| Phase transition | Extended with irreversible phase emergence records. |

## Non-Breaking Policy

v0.5 is additive. Existing local commands remain valid:

```bash
python3 -m kernel.runtime --generations 3 --output-dir kernel/output/demo-run
python3 -m kernel_v0_2.runtime_v0_2 --generations 4 --output-dir kernel_v0_2/output/demo-run
python3 saee_v0_3/KERNEL_BOOTSTRAP_SCRIPT.py --generations 3 --output-dir saee_v0_3/output/demo-run
python3 saee_v0_4/KERNEL_BOOTSTRAP_SCRIPT.py --generations 5 --output-dir saee_v0_4/output/demo-run
```

New v0.5 command:

```bash
python3 saee_v0_5/bootstrap/v0_5_bootstrap.py --generations 6 --output-dir saee_v0_5/output/demo-run
```
