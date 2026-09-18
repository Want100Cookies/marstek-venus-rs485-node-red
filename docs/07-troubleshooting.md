# Troubleshooting

## Integration does not control batteries
- Check `control_enabled` switch.
- Check master mode is `full_control`.
- Check mapping for mode/power command entities.

## Grid sensor unavailable
- Confirm selected entity exists and is numeric.

## Dynamic strategy not switching
- Verify provider data source and min spread settings.
- Check diagnostics for fallback trace.

## Dashboard not loading
- Clear browser cache and reload Home Assistant frontend assets.
- Confirm integration panel is enabled.
