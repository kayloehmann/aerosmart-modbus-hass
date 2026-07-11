# Vendored dependency

This directory is a vendored copy of [`aerosmart-modbus`](https://github.com/kayloehmann/aerosmart-modbus),
version `0.1.0`, embedded here because this custom integration targets
current stable Home Assistant releases via HACS, and the standard path (a
`manifest.json` PyPI `requirements` entry) would still work for the library
itself but the integration additionally depends on the very new
`modbus_connection` hub integration, which is not guaranteed to exist on the
Home Assistant release a HACS user has installed. Vendoring the *device
library* here does not change that -- see the top-level README's "Known
limitation" section.

No modifications were made to the vendored source beyond removing the
`py.typed` marker (irrelevant once embedded) and this file.

Original license: Apache-2.0, Copyright 2026 Kay Löhmann (same author as
this integration) -- see `LICENSE` at the repository root.
