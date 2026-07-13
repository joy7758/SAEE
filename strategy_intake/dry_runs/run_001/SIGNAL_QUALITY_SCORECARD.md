# Signal Quality Scorecard

| Dimension | Score | Interpretation |
| --- | ---: | --- |
| signal_quality | 2 | Existing recommendation signals are concrete; market and competitor logs currently contain no fresh external data. |
| task_candidate_quality | 4 | Candidates are bounded and mostly actionable, but some depend on future manual results. |
| duplicate_rate_score | 4 | Some candidates overlap with already prepared scheduled-intake work. |
| boundary_safety | 5 | No forbidden runtime/backend/kernel/private-core intent was detected. |
| commercial_relevance | 4 | Candidates are relevant to recommendation, validation, market sensing, or buyer understanding. |

## Missing Optional Signal Sources

- missing_signal_source: strategy_intake/USER_QUESTION_SIGNAL_LOG.md
- missing_signal_source: strategy_intake/GITHUB_ECOSYSTEM_SIGNAL_LOG.md
