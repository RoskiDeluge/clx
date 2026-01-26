# Change: Remove pod/actor routing support

## Why
Pod/actor routing is specific to Paseo and we want the library fully backend-agnostic with a single `/v1/query` contract.

## What Changes
- **BREAKING** Remove pod/actor routing support and related env vars/parameters.
- Remove pod/actor references from documentation and config examples.
- Keep the request payload and response handling focused on `/v1/query` only.

## Impact
- Affected specs: core
- Affected code: `clx/core.py`, `README.md`, `.env.example`, `clx_cli.egg-info/PKG-INFO`, `openspec/project.md`
