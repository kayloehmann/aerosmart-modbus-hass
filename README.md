# aerosmart for Home Assistant (HACS)

[![Release](https://img.shields.io/github/v/release/kayloehmann/aerosmart-modbus-hass)](https://github.com/kayloehmann/aerosmart-modbus-hass/releases/latest)
[![Test](https://github.com/kayloehmann/aerosmart-modbus-hass/actions/workflows/test.yml/badge.svg)](https://github.com/kayloehmann/aerosmart-modbus-hass/actions/workflows/test.yml)
[![Validate](https://github.com/kayloehmann/aerosmart-modbus-hass/actions/workflows/validate.yml/badge.svg)](https://github.com/kayloehmann/aerosmart-modbus-hass/actions/workflows/validate.yml)

A HACS-installable custom integration for the aerosmart ventilation/heat-pump
unit. It uses Home Assistant 2026.9's official shared Modbus connection API
and the backend-neutral
[`modbus-connection`](https://home-assistant-libs.github.io/modbus-connection/)
library supplied by Home Assistant. Based on
the [`ludeeus/integration_blueprint`](https://github.com/ludeeus/integration_blueprint)
template.

## What is this?

The device's register map (137 registers across 16 sub-systems, 2 Modbus
units) is transcribed from a real installation's Home Assistant `modbus:` YAML
config -- there is no official manufacturer register manual behind it. The
core register/component model itself is a **vendored copy** of
[`aerosmart-modbus`](https://github.com/kayloehmann/aerosmart-modbus) (see
`custom_components/aerosmart/aerosmart_modbus/NOTICE.md`), not a PyPI
dependency, so this integration can be installed via HACS from this repo
alone.

## Supported devices

One aerosmart ventilation/heat-pump installation, addressed as **two Modbus
units behind a single connection**: a ventilation controller (default unit
ID 1) and a heat pump / hot water controller (default unit ID 2). Both unit
IDs are configurable in case a different installation numbers them
differently. Only one physical installation has been used to transcribe the
register map so far -- if your unit reports different values than expected
for a given entity, treat the naming as a heuristic to verify, not a
guarantee (see "Known limitations").

## Supported functions

- ~120 read-only `sensor`/`binary_sensor` entities mirroring the source
  installation's existing register set: temperatures, filter runtimes,
  operating-hour counters, fault/problem indicators, fan speeds, heat-pump
  state, hot water temperatures.
- 14 `number`/`switch`/`select` entities for registers whose name suggests
  they are writable setpoints or functions -- **disabled by default**, since
  writability was inferred from the register's name rather than a confirmed
  manufacturer specification (see "Known limitations").
- Diagnostics (`custom_components/aerosmart/diagnostics.py`): a full dump of
  every known register's current value, downloadable from the integration's
  device page for troubleshooting or filing an issue.
- A reconfigure flow: change the gateway host/port or either unit ID from the
  integration's "Configure" menu without removing and re-adding it.

## Prerequisites / installation instructions

Home Assistant **2026.9.0 or newer** is required. The integration uses the
Modbus connection provided by Home Assistant; no separate `modbus_connection`
integration, YAML hub, or manually installed Python package is required.

1. Via [HACS](https://hacs.xyz/): add this repository as a custom repository
   (category: Integration), then install "aerosmart" and restart Home
   Assistant if prompted.
2. Settings -> Devices & services -> Add integration -> "aerosmart", then
   enter the Modbus TCP gateway host and port plus the two station addresses
   (defaults: port 502, unit 1 for ventilation, unit 2 for heat pump).

### Updating from v0.4.x

1. Update Home Assistant to 2026.9.0 or newer.
2. Update aerosmart to v0.5.0 or newer in HACS.
3. Restart Home Assistant.

Existing aerosmart configuration entries are retained. The integration now
hands connection creation, reconnects, sharing, and teardown to Home Assistant.
The previous private connection module and direct `tmodbus` dependency have
been removed.

### Configuration parameters

| Parameter | Description |
| --- | --- |
| Host | Hostname or IP address of the Modbus TCP gateway. |
| Port | TCP port of the gateway (default 502). |
| Ventilation unit | The ventilation controller's Modbus station address (default 1). |
| Heat pump unit | The heat pump / hot water controller's Modbus station address (default 2). |

All four can be changed later via the integration's "Configure" menu
(reconfigure flow) -- for example if the installation's station addresses
turn out to differ from the defaults.

## Removal instructions

Settings -> Devices & services -> aerosmart -> the three-dot menu -> Delete.
This removes the aerosmart config entry and its entities/device. Home Assistant
releases the shared Modbus connection when its last consumer unloads.

## How data updates

All entities share one `DataUpdateCoordinator` that polls both units every
30 seconds (`SCAN_INTERVAL` in `const.py`) -- adding or removing entities
never changes what gets polled, since the coordinator always fans out to
every sub-system. Each 32-bit datapoint is read separately because real
aerosmart controllers reject larger combined reads even across adjacent
addresses. If a poll fails, entities go `unavailable`; Home Assistant
logs an error once (not on every failed poll) and an info message once
connectivity recovers.

Requests are serialized across both station addresses with a 300 ms gap. This
is required by the reference installation's slow serial-to-TCP gateway. A
single register value spans at most two Modbus registers; the integration does
not combine adjacent values into larger reads because the controller rejects
such requests with Modbus exception code 2.

## Known limitations

- Home Assistant shares the Modbus TCP connection with other integrations using
  identical link settings. External clients can still compete with that shared
  connection unless the gateway supports multiple independent clients.
- The register map is transcribed from one real installation's existing
  `modbus:` YAML, not an official manufacturer specification. Entity names,
  units, and especially **writability of `number`/`switch`/`select`
  entities are naming heuristics** -- verify each one against your own unit
  before relying on it, particularly before automating anything that writes.
- Only one HA device represents the whole installation; ventilation and heat
  pump are not split into separate devices even though they're separate
  Modbus units.

## Troubleshooting

- **`No module named 'tmodbus'` or `Invalid handler specified`:** update to
  aerosmart v0.5.0 or newer, verify that Home Assistant 2026.9.0 or newer is
  installed, and restart Home Assistant. Do not manually install `tmodbus`.
- **Modbus exception code 2:** the controller rejected an invalid register
  range. v0.5.0 limits reads to a maximum of two registers. If this still
  occurs, include the failing address and count from the log in the issue.
- **Entities go `unavailable` intermittently, or the log shows Modbus
  timeouts/mismatched responses:** if your unit sits behind a slow
  RS232-to-Modbus-TCP gateway (as the reference installation does), sending
  requests back-to-back with no pacing can make the gateway return responses
  under stale or mismatched transaction IDs. v0.5.0 configures a 300 ms message
  spacing and waits another 300 ms when switching from the ventilation unit to
  the heat-pump unit.
- **"Failed to connect" during setup or reconfigure:** check the gateway host,
  port and both station addresses. The config flow reads one component from
  each unit before creating or updating the entry. Also ensure that another
  external Modbus client is not occupying a gateway that accepts only one TCP
  client at a time.
- **Something looks wrong with a specific entity's value:** download
  diagnostics (device page -> Download diagnostics) to get every register's
  raw value in one file; useful both for your own debugging and for
  attaching to a GitHub issue.

## Use cases / examples

- Dashboard cards for supply/exhaust air temperature, fan speed, and heat
  pump state alongside the rest of your climate dashboard.
- Automations on the fault (`device_class: problem`) binary sensors --
  e.g. notify on `binary_sensor.aerosmart_stoerung_*` turning on.
- Filter-change reminders from the `_wechseln` ("needs changing") binary
  sensors instead of a fixed calendar schedule.
- Once individually verified against your unit, automating setpoints (target
  room temperature, boost functions) via the disabled-by-default
  `number`/`switch`/`select` entities.

## Brand icon

Added: `custom_components/aerosmart/brand/icon.png` (256x256) and
`icon@2x.png` (512x512). Home Assistant (since 2026.3, the "Brands Proxy
API") serves a custom integration's brand icon straight from its own repo --
no PR against [`home-assistant/brands`](https://github.com/home-assistant/brands)
required. Detection is purely file-presence-based
(`Integration.has_branding` in HA core checks for a `brand/` subdirectory),
no manifest.json change needed. Supported files:

```
custom_components/aerosmart/
└── brand/
    ├── icon.png            # done: 256x256 PNG, square, transparent bg
    ├── icon@2x.png         # done: 512x512 hDPI
    ├── logo.png            # not added -- icon.png serves as fallback
    ├── logo@2x.png
    ├── dark_icon.png        # not added -- optional dark-theme variant
    ├── dark_icon@2x.png
    ├── dark_logo.png
    └── dark_logo@2x.png
```

Missing files fall back sensibly (e.g. `logo.png` falls back to `icon.png`,
`dark_*` falls back to the non-dark version) -- `icon.png` alone is enough to
get a working icon everywhere. Image requirements mirror the classic
`home-assistant/brands` spec: PNG, lossless/optimized, trimmed (no padding),
transparent or white-background preferred, and must not reuse Home
Assistant's own branding (would misleadingly suggest an official/internal
integration). A separate PR against `home-assistant/brands` is still
optionally worth doing later for store-browsing UIs (e.g. HACS) that pull
from the public CDN before installation, but isn't required for the icon to
show up inside Home Assistant itself.

## Development

```bash
./scripts/setup    # install dependencies
./scripts/lint     # ruff format + fix
./scripts/develop  # run a local Home Assistant with this integration loaded
```

Or open this repo in the provided dev container (`.devcontainer.json`).

## Quality-scale status

This integration's code quality is tracked informally against Home
Assistant's [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/)
checklist as a quality bar, even though this repo targets HACS rather than
`home-assistant/core` inclusion. Done: config-flow test coverage (incl. a
reconfigure flow), coordinator/number/switch/select/binary_sensor tests,
translated exceptions, `diagnostics.py`, per-entity translation keys,
`PARALLEL_UPDATES`, a brand icon, and a full `entity_category`/`device_class`
pass: `DIAGNOSTIC` on 64 entities (presence sensors, fault/"Störung" sensors,
internal "Anforderung" signals, configured thresholds/limits like frost- and
summer-bypass setpoints, operating-hour/lifetime counters, the device's
clock/sync fields), `CONFIG` on all 11 `number` setpoints, `device_class` on
fault sensors (`PROBLEM`) and CO2 (`CO2`). Left uncategorized on purpose:
live measurements/status (temperatures, fan speeds, current operating mode)
and the `select`/`switch` entities (their state *is* the primary function,
not configuration of it). `strict-typing`: `pyproject.toml` has a `[tool.mypy]`
`strict = true` config (vendored `aerosmart_modbus` excluded -- separately
maintained, separately typed, see its own `NOTICE.md`); a manual pass found
the two gaps already fixed (an untyped `**kwargs` in `switch.py`, an untyped
`_subsystem` property in `entity.py`) and no others. Ruff, strict mypy and the
full test suite pass in CI. The suite is verified against Home Assistant
2026.9.0 on Python 3.14. Still open: icon translations for the rest of the
entity set.

The integration uses `homeassistant.components.modbus.async_get_unit` and
`async_get_temporary_unit`; Home Assistant owns connection sharing, reconnects,
and teardown. The test workflow is enabled for pushes and pull requests as well
as manual dispatches on Python 3.14.

A parallel reference implementation was also built against
`home-assistant/core`'s conventions (fork:
[`kayloehmann/core@aerosmart-integration`](https://github.com/kayloehmann/core/tree/aerosmart-integration)),
mainly as a way to validate patterns (reconfigure-flow duplicate-ID handling,
translated exceptions) against the stricter core test harness before porting
them here. It's not an active target for a `home-assistant/core` submission.

## Next steps

- Keep the test suite and `mypy --strict` green in CI.
- Confirm v0.5.x against additional physical aerosmart installations and
  gateway models.
- Add sensor-platform tests (only binary_sensor/number/select/switch/
  coordinator are covered so far).
- Add icon translations for the rest of the entity set (`icons.json`
  currently only covers filter/fan/heat-pump/CO2/boost-switch entities).
- Verify each disabled-by-default writable entity against the real unit, then
  flip its `entity_registry_enabled_default`.
