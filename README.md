# aerosmart for Home Assistant (HACS)

A HACS-installable custom integration for the aerosmart ventilation/heat-pump
unit, built on Home Assistant's `modbus_connection` hub integration. Based on
the [`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint)
template.

## Known limitation

This integration depends on `modbus_connection`
(`dependencies: ["modbus_connection"]` in `manifest.json`), which is a very
new Home Assistant Core integration. **It only works on a Home Assistant
installation that already includes `modbus_connection`** -- at the time of
writing that means a recent `dev`/nightly build, not yet a stable numbered
release. `hacs.json`'s `homeassistant` minimum version is a placeholder until
a real stable release ships it; update it once one does.

If you need this to work today on a stable release instead, the alternative
is a self-contained `pymodbus` transport instead of `modbus_connection` --
that was considered and explicitly not chosen for this repository (see the
project history for why: matching the official upstream pattern was
prioritized over immediate compatibility).

## What is this?

The device's register map (137 registers across 16 sub-systems, 2 Modbus
units) is transcribed from a real installation's Home Assistant `modbus:` YAML
config -- there is no official manufacturer register manual behind it. The
core register/component model itself is a **vendored copy** of
[`aerosmart-modbus`](https://github.com/kayloehmann/aerosmart-modbus) (see
`custom_components/aerosmart/aerosmart_modbus/NOTICE.md`), not a PyPI
dependency, so this integration can be installed via HACS from this repo
alone.

## Installation

Via [HACS](https://hacs.xyz/): Add this repository as a custom repository
(category: Integration), then install "aerosmart". Requires a
`modbus_connection` connection to already be configured (Settings ->
Devices & services -> Add integration -> Modbus Connection) before adding
this integration.

## Entities

- ~120 read-only `sensor`/`binary_sensor` entities mirroring the source
  installation's existing register set.
- 14 `number`/`switch` entities for registers whose name suggests they are
  writable setpoints/functions -- **disabled by default**. Writability here
  is a naming heuristic, not a confirmed specification; enable and verify
  each one individually against your real unit before relying on it.

## Development

```bash
./scripts/setup    # install dependencies
./scripts/lint     # ruff format + fix
./scripts/develop  # run a local Home Assistant with this integration loaded
```

Or open this repo in the provided dev container (`.devcontainer.json`).

## Next steps

- Add [brand images](https://github.com/home-assistant/brands) (currently
  `ignore: brands` in `.github/workflows/validate.yml`).
- Add tests -- [`pytest-homeassistant-custom-component`](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component)
  can help get started; the sibling repo's
  [`homeassistant/components/aerosmart`](https://github.com/kayloehmann/core/tree/aerosmart-integration/tests/components/aerosmart)
  tests cover the same logic against the real `homeassistant` test harness and
  can be adapted.
- Verify each disabled-by-default writable entity against the real unit, then
  flip its `entity_registry_enabled_default`.
- Update `hacs.json`'s `homeassistant` minimum version once `modbus_connection`
  ships in a stable release, and drop the "Known limitation" section above.
