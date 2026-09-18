# Modbus / Battery Mapping

The integration uses generic battery mapping.

Required per battery:
- SoC sensor
- Current power sensor
- Max charge number
- Max discharge number
- Command power number

Optional:
- Command mode select
- Remaining capacity sensor
- Total energy sensor
- RS485 mode entity
- User work mode entity
- Inverter state sensor

Use Marstek preset to prefill common `marstek_mN_*` entities.
