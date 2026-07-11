# Contributing

This custom component is based on the
[integration_blueprint](https://github.com/ludeeus/integration_blueprint)
template.

## Getting started

1. Fork and clone the repository.
2. Run `./scripts/setup` to install dependencies.
3. Run `./scripts/develop` to start a local Home Assistant instance with this
   integration loaded (via `PYTHONPATH`, no symlink needed).
4. Run `./scripts/lint` before committing.

## Vendored dependency

`custom_components/aerosmart/aerosmart_modbus/` is a vendored copy of the
[`aerosmart-modbus`](https://github.com/kayloehmann/aerosmart-modbus) PyPI
library, not a regular dependency -- see that directory's `NOTICE.md`. Changes
to the register model itself should go upstream in that repository first,
then be re-vendored here, rather than diverging locally.
