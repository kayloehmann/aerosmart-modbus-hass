# aerosmart for Home Assistant (HACS)

A HACS-installable custom integration for the aerosmart ventilation/heat-pump
unit, built on Home Assistant's `modbus_connection` hub integration. Based on
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
- A reconfigure flow: change the Modbus connection or either unit ID from the
  integration's "Configure" menu without removing and re-adding it.

## Prerequisites / installation instructions

1. A `modbus_connection` connection must already be configured (Settings ->
   Devices & services -> Add integration -> Modbus Connection) before adding
   this integration -- aerosmart borrows its Modbus units from that
   connection rather than owning one itself.
2. Via [HACS](https://hacs.xyz/): add this repository as a custom repository
   (category: Integration), then install "aerosmart" and restart Home
   Assistant if prompted.
3. Settings -> Devices & services -> Add integration -> "aerosmart", then
   pick the Modbus connection and the two station addresses (defaults: 1 for
   ventilation, 2 for heat pump).

### Configuration parameters

| Parameter | Description |
| --- | --- |
| Modbus connection | Which existing `modbus_connection` entry to borrow units from. |
| Ventilation unit | The ventilation controller's Modbus station address (default 1). |
| Heat pump unit | The heat pump / hot water controller's Modbus station address (default 2). |

All three can be changed later via the integration's "Configure" menu
(reconfigure flow) -- for example if the installation's station addresses
turn out to differ from the defaults.

## Removal instructions

Settings -> Devices & services -> aerosmart -> the three-dot menu -> Delete.
This only removes the aerosmart config entry and its entities/device; it does
not affect the underlying `modbus_connection` entry, which other
integrations (or another aerosmart entry) may still be using.

## How data updates

All entities share one `DataUpdateCoordinator` that polls both units every
30 seconds (`SCAN_INTERVAL` in `const.py`) -- adding or removing entities
never changes what gets polled, since the coordinator always fans out to
every sub-system. If a poll fails, entities go `unavailable`; Home Assistant
logs an error once (not on every failed poll) and an info message once
connectivity recovers.

## Known limitations

- This integration depends on `modbus_connection`
  (`dependencies: ["modbus_connection"]` in `manifest.json`), which is a very
  new Home Assistant Core integration. **It only works on a Home Assistant
  installation that already includes `modbus_connection`** -- at the time of
  writing that means a recent `dev`/nightly build, not yet a stable numbered
  release. `hacs.json`'s `homeassistant` minimum version is a placeholder
  until a real stable release ships it; update it once one does.

  If you need this to work today on a stable release instead, the
  alternative is a self-contained `pymodbus` transport instead of
  `modbus_connection` -- that was considered and explicitly not chosen for
  this repository (see the project history for why: matching the official
  upstream pattern was prioritized over immediate compatibility).
- The register map is transcribed from one real installation's existing
  `modbus:` YAML, not an official manufacturer specification. Entity names,
  units, and especially **writability of `number`/`switch`/`select`
  entities are naming heuristics** -- verify each one against your own unit
  before relying on it, particularly before automating anything that writes.
- Only one HA device represents the whole installation; ventilation and heat
  pump are not split into separate devices even though they're separate
  Modbus units.

## Troubleshooting

- **Entities go `unavailable` intermittently, or the log shows Modbus
  timeouts/mismatched responses:** if your unit sits behind a slow
  RS232-to-Modbus-TCP gateway (as the reference installation does), sending
  requests back-to-back with no pacing can make the gateway return responses
  under stale or mismatched transaction IDs. `MESSAGE_SPACING_SECONDS` in
  `const.py` (currently 0.3s) adds spacing between requests to the
  `modbus_connection` unit specifically to work around this; if you still see
  the issue, try increasing it.
- **"Failed to connect" during setup or reconfigure:** confirms the chosen
  `modbus_connection` entry is loaded and both station addresses are
  reachable through it -- the config flow probes the ventilation unit's
  general sub-system once before creating/updating the entry.
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
`_subsystem` property in `entity.py`) and no others. Still open: icon
translations for the rest of the entity set.

**Neither the test suite nor `mypy --strict` have actually been run** --
both need `homeassistant` installed to resolve `modbus_connection`-dependent
imports, which hits the exact same blocker either way (see below). Treat the
mypy config as a declared target, not a verified pass.

**Test suite is currently unverified in CI, and this is a genuine
chicken-and-egg blocker, not just a config problem**: `.github/workflows/test.yml`
is `workflow_dispatch`-only rather than running on every push. The tests
themselves were written against real register addresses/enum tables pulled
from the vendored `aerosmart_modbus` source and the actual `modbus_connection`
mock API (not guessed), and two real bugs in the pre-existing config_flow
tests were found and fixed along the way (a missing
`enable_custom_integrations` fixture and a `homeassistant.components.aerosmart`
import that can't resolve at collection time) -- but nothing here has
actually run end-to-end. What was tried:

1. Plain `pip install -r requirements_test.txt`: fails immediately --
   `modbus_connection` (a hard dependency, see "Known limitations") isn't in
   any stable/beta `homeassistant` release yet, so
   `homeassistant.components.modbus_connection` can't be imported.
2. Installing `homeassistant` from `home-assistant/core`'s `dev` branch
   instead (which does have `modbus_connection`): got further -- needed
   Python 3.14 (dev's current minimum) and the `modbus-connection[tmodbus]`
   extra (`homeassistant.components.modbus_connection`'s own manifest
   requirement) -- but then every test fails at `hass`-fixture setup with
   `AttributeError: <module 'homeassistant.components.http' ...> does not
   have the attribute 'start_http_server_and_save_config'`.
   `pytest-homeassistant-custom-component`'s fixtures are *generated* against
   a specific published homeassistant release (currently 2026.7.2, per its
   own `ha_version` file) -- they don't track `dev` directly, so a `dev`-only
   internal refactor (that function no longer exists there) breaks them,
   independent of anything in this repo.

Net result: this can't be tested end-to-end until `modbus_connection` lands
in a release or beta that `pytest-homeassistant-custom-component` has
already picked up. At that point, drop back to plain
`pip install -r requirements_test.txt` (no dev-branch override needed) and
re-enable the `push`/`pull_request` triggers.

A parallel reference implementation was also built against
`home-assistant/core`'s conventions (fork:
[`kayloehmann/core@aerosmart-integration`](https://github.com/kayloehmann/core/tree/aerosmart-integration)),
mainly as a way to validate patterns (reconfigure-flow duplicate-ID handling,
translated exceptions) against the stricter core test harness before porting
them here. It's not an active target for a `home-assistant/core` submission.

## Next steps

- Get the test suite *and* `mypy --strict` actually running in CI once
  `modbus_connection` lands in a release/beta `pytest-homeassistant-custom-component`
  has picked up (see "Quality-scale status" above for why both are blocked on
  the same thing, not just unconfigured) and confirm they're green -- neither
  has actually been run.
- Add sensor-platform tests (only binary_sensor/number/select/switch/
  coordinator are covered so far).
- Add icon translations for the rest of the entity set (`icons.json`
  currently only covers filter/fan/heat-pump/CO2/boost-switch entities).
- Verify each disabled-by-default writable entity against the real unit, then
  flip its `entity_registry_enabled_default`.
- Update `hacs.json`'s `homeassistant` minimum version once `modbus_connection`
  ships in a stable release, and drop the corresponding "Known limitations"
  bullet above.
