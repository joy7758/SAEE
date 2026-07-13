# Backward Compatibility Map

## v0.1 to v0.3

| v0.1 surface | v0.3 compatibility |
| --- | --- |
| `kernel/examples/seed_genome.json` | Used as the default v0.3 founder genome. |
| `kernel/runtime.py` | Remains runnable; v0.3 does not replace it. |
| `kernel/genome/genome_schema.json` | v0.3 normalizes seed genomes with `schema_version=saee-genome-v0.3` at runtime without editing the seed file. |
| `scripts/kernel_smoke.py` | Still part of `make check`. |

## v0.2 to v0.3

| v0.2 surface | v0.3 compatibility |
| --- | --- |
| Population pool | Preserved and extended with rule-aware mutation pressure. |
| Abstract signal stream | Preserved as abstract local sensorium. |
| Dynamic fitness | Preserved and extended with rule-genome weights. |
| Selection pressure | Preserved and extended under rule-genome thresholds. |
| Lineage graph | Preserved and extended with rule-genome graph. |
| `scripts/kernel_v0_2_smoke.py` | Still part of `make check`. |

## Non-Breaking Policy

v0.3 is additive. It does not remove v0.1 or v0.2 runtime paths. Existing local
commands remain valid:

```bash
python3 -m kernel.runtime --generations 3 --output-dir kernel/output/demo-run
python3 -m kernel_v0_2.runtime_v0_2 --generations 4 --output-dir kernel_v0_2/output/demo-run
```

New v0.3 command:

```bash
python3 saee_v0_3/KERNEL_BOOTSTRAP_SCRIPT.py --generations 3 --output-dir saee_v0_3/output/demo-run
```

