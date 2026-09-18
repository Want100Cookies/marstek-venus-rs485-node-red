# Self-Consumption and PID

PID behavior includes:
- Input dampening
- P/I/D terms
- Integral clamp
- Ki bumpless update support
- Output dampening
- Hysteresis deadband

Internal sign convention:
- Positive grid power = import
- Positive battery command = charge
- Negative battery command = discharge

Diagnostics are exposed through integration sensors and diagnostics payload.
