# Strategies

Implemented strategy set:
- Full stop
- Self-consumption
- Timed
- Dynamic
- Charge
- Charge PV
- Sell
- Zero import
- Standby / peak shave

Parity highlights:
- Full stop is hard-stop and never overridden.
- EV charging can override selected strategy.
- Peak shave direction latches during release window.
- Timed strategy evaluation order: A, B, C, D, E, default.
