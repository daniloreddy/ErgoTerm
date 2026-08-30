# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```powershell
# Run the TUI app
scripts\run.bat          # Windows
bash scripts/run.sh      # Unix

# Lint, format, type-check, test (all-in-one)
scripts\checks.bat       # Windows
bash scripts/checks.sh   # Unix

# Run a single test
./venv/Scripts/python.exe -m pytest test_api_client.py::test_check_auth_success -v

# Install runtime deps
./venv/Scripts/pip.exe install -r requirements.txt

# Install dev deps (pytest, pytest-asyncio, respx, ruff, mypy)
./venv/Scripts/pip.exe install -r requirements.dev.txt
```

`scripts/run.*` and `scripts/checks.*` auto-create `venv` and install deps on first run.

## Architecture

Two-layer design:

**`ergo_api_client.py` — `ErgoApiClient`**
- All HTTP calls go through the async `_request(endpoint, data)`, which always uses `POST` regardless of endpoint semantics (`httpx.AsyncClient`, 10s timeout).
- Returns `dict[str, Any]`. On `success: false` from the server, injects/prefixes an `error` field while preserving other keys (e.g., `errorCode`).
- Never raises — all errors (network, HTTP, JSON, non-object body) return `{"success": False, "error": "..."}`.

**`main.py` — `ErgoTUI(App)`**
- Textual app with two panes: config (left) and interaction (right).
- `on_mount` sets up the rotating file logger (`~/.ergoterm.log`) and calls `load_saved_config()` to pre-fill inputs from `~/.ergo_api_config.json`.
- `on_button_pressed` is `async`; dispatches to either `load_config()` or `await call_api_method()`.
- `call_api_method(log, method_name, args, display_name)` looks up the method by name via `getattr` and `await`s it, keeping the TUI responsive during API calls.
- Config is saved to `~/.ergo_api_config.json` (owner-only, `chmod 600`) only on successful "Load Config" (not on app exit).

**`tui.css`** — Textual CSS (subset of CSS; no standard CSS properties like `display:flex`). Uses `1fr` for flexible width.

## Adding a New Endpoint

1. Add an `async` method to `ErgoApiClient`: `return await self._request("endpoint_name", data={...})`.
2. In `main.py` `compose()`, add a `Button` inside `#endpoint_buttons`.
3. In `on_button_pressed`, add an `elif` branch calling `await self.call_api_method(log, "method_name", [args], "Display Name")`.
4. Add `async` tests in `test_api_client.py` using the `m` (respx) and `client` fixtures.

## Project Decisions (Golden Rule — scenarios not covered by global guidelines)

- **Python version**: target is 3.12+ (`pyproject.toml` `requires-python`,
  `ruff target-version = "py312"`). Recreate the local `venv` with a 3.12+
  interpreter if the checked-in one is older.
- **Credential storage**: this TUI tool persists `api_url` + `bearer_token` in cleartext
  in `~/.ergo_api_config.json`, restricted to the owner with `chmod 600` (no-op on
  Windows). Deliberate choice for a local single-user admin tool — `CredentialFilter`
  (global rule §4) covers logging, not at-rest storage; OS keyring was judged
  disproportionate here. The file is gitignored.

## Known Issues

- **Hardcoded default**: `DEFAULT_TOKEN = "YOUR_BEARER_TOKEN_HERE"` is checked in `load_config()` to prevent accidental use.
