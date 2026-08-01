# Vendored dependency

This directory is a vendored copy of [`aerosmart-modbus`](https://github.com/kayloehmann/aerosmart-modbus),
version `0.2.1`, embedded so the custom integration can be installed from this
HACS repository without publishing the device model separately. The model is
backend-neutral; the surrounding integration owns one Modbus TCP connection
and supplies its two unit handles.

No modifications were made to the vendored source beyond removing the
`py.typed` marker (irrelevant once embedded) and this file.

Original license: Apache-2.0, Copyright 2026 Kay Löhmann (same author as
this integration) -- see `LICENSE` at the repository root.
