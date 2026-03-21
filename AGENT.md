# AI Agent Technical Brief - Ergo IRCd API Client

This document provides technical details for AI agents maintaining or extending this project.

## Project Architecture

- **`ergo_api_client.py`**: Core API logic. Uses `requests`.
    - All calls are `POST`.
    - Authentication via `Authorization: Bearer <token>`.
    - Handles JSON serialization/deserialization.
    - Intercepts `success: false` from the server to inject a descriptive `error` field while preserving original keys (e.g., `errorCode`).
- **`main.py`**: Textual TUI Application.
    - Uses `Horizontal` and `Vertical` containers for layout.
    - Persists config to `~/.ergo_api_config.json`.
    - Methods starting with `on_button_pressed` handle UI interactions.
    - `call_api_method` is the generic bridge to the API client.
- **`tui.css`**: Stylesheet for the TUI.
    - Defines class-based styling (`.title`, `.status_green`, etc.) and ID-based layout (`#config_pane`, `#endpoint_buttons`).

## Common Tasks for Agents

### Adding a New API Endpoint
1.  **Client Update**: Add a method to `ErgoApiClient` in `ergo_api_client.py`. Use `self._request(endpoint_name, data=...)`.
2.  **TUI Update**: 
    - Add a `Button` to the `endpoint_buttons` container in `main.py`'s `compose` method.
    - Update `on_button_pressed` to catch the button ID and call `self.call_api_method`.
3.  **Testing**: Add a corresponding test case in `test_api_client.py` using the `m` fixture (requests-mock).

### Modifying TUI Layout
- Check `compose` in `main.py` for structural changes.
- Update `tui.css` for visual changes. Note: Textual uses a CSS-like language but not all standard CSS properties are supported (e.g., use `width: 1fr` for flexible spacing).

## Persistence Details
- Credentials are saved automatically whenever the **"Load Config"** button is successfully triggered.
- File location: `Path.home() / ".ergo_api_config.json"`.

## Testing Environment
- Run tests with `pytest test_api_client.py`.
- Requires `pytest-mock` and `requests-mock`.
