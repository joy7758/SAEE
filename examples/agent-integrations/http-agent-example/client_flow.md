# HTTP Client Flow

```text
discover capability-package/manifest.json
-> choose localhost HTTP transport
-> POST /capabilities/evaluate-evidence
-> inspect HTTP status and Runtime status
-> map SUPPORTED to bounded CONTINUE
-> preserve all false authorization/certification/safety fields
```

