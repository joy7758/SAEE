# SAEE First User Success Criteria

## Minimum Sample

```text
minimum_sessions: 5
preferred_sessions: 10
```

## Metrics

```text
understanding_rate
trust_rate
decision_influence_rate
repeat_usage_intent
```

## Go Criteria

Proceed to product hardening if all are true:

```text
understanding_rate >= 0.80
trust_rate >= 0.60
decision_influence_rate >= 0.60
repeat_usage_intent >= 0.40
```

Interpretation:

```text
Users understand the category.
Users believe the result is credible enough for internal discussion.
The recommendation can affect deployment decisions.
Some users want to try their own candidates.
```

## Hold Criteria

Hold feature development and improve messaging if any are true:

```text
understanding_rate < 0.80
trust_rate between 0.40 and 0.60
decision_influence_rate between 0.40 and 0.60
```

Likely response:

```text
Improve explanation copy.
Improve result evidence hierarchy.
Improve demo script.
Do not change core engine first.
```

## Pivot Criteria

Reconsider positioning if any are true:

```text
understanding_rate < 0.50
trust_rate < 0.40
decision_influence_rate < 0.40
repeat_usage_intent < 0.20
```

Likely response:

```text
Narrow target user.
Change wedge.
Reframe around regression testing or deployment review.
Do not claim broad AI decision infrastructure.
```

## Non-Claims

```yaml
customer_validated: false
product_launched: false
production_deployed: false
public_sdk_release: false
user_upload_enabled: false
private_core_exported: false
implementation_disclosed: false
product_market_fit_claimed: false
revenue_validated: false
production_readiness_claimed: false
external_benchmark_claimed: false
```

These flags remain false until real sessions are completed and evidence is
recorded.
