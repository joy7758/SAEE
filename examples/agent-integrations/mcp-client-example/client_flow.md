# MCP Client Flow

```text
initialize
-> notifications/initialized
-> tools/list
-> select evaluate_rehearsal_run
-> tools/call with request_id, payload and caller_context
-> read structuredContent.status and result.assessment
-> preserve limitations
-> CONTINUE only inside the caller's separately authorized workflow
```

`Tool availability != authorization`，`SUPPORTED != safe`。

