# Dynamic Strategy

Dynamic routing is provider-driven through a tariff abstraction.

Current behavior:
- Mark cheapest/most-expensive intervals using extreme-pair matching.
- Require spread >= minimum delta.
- Respect optional cheap/expensive caps.
- Route now-mark to configured low/high/neutral sub-strategy.
- Fallback to default strategy when provider data is invalid/missing.

Legacy Cheapest Energy Hours behavior is preserved conceptually via provider isolation.
