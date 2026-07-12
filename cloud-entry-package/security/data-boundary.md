# Data Boundary

- Synthetic or explicitly approved sanitized input only.
- `customer_data_included` must be `false`.
- No credential, secret, personal record, payment record, or production log.
- The local tools do not fetch `source_ref` values or contact external systems.
- Trace authenticity and evidence-source authenticity remain unverified.
