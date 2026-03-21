# Ergo IRCd API Client (TUI)

A modern Python-based Text User Interface (TUI) client for interacting with the [Ergo IRCd](https://ergo.chat/) HTTP API.

## Purpose

This application provides a user-friendly way for server administrators to manage their Ergo IRCd instance through its experimental HTTP API. It eliminates the need for manual `curl` commands by providing an interactive interface for common administrative tasks.

## Features

- **Interactive TUI**: Built with the `textual` framework for a responsive and visually appealing terminal experience.
- **Credential Persistence**: Automatically saves and reloads your API URL and Bearer Token from your home directory (`~/.ergo_api_config.json`).
- **Endpoint Support**:
    - **Status**: View server version, user counts, and channel statistics.
    - **Check Auth**: Verify NickServ account credentials.
    - **Register**: Perform SAREGISTER operations for new accounts.
    - **Rehash**: Trigger a server configuration reload.
    - **Account List**: Retrieve a list of all registered accounts.
- **JSON Logging**: All API responses are displayed in a scrollable, syntax-highlighted log area.
- **Documentation Access**: Quick shortcut (`Ctrl+T`) to open official Ergo API documentation.

## Requirements

The project requires Python 3.8+ and the following dependencies:

### Runtime
- `requests`: For handling HTTP communication.
- `textual`: For the terminal user interface.

### Development/Testing
- `pytest`: Testing framework.
- `requests-mock`: For mocking API responses.
- `pytest-mock`: For advanced mocking capabilities.

## Installation

1.  **Clone the repository** (or copy the files).
2.  **Create a virtual environment**:
    ```powershell
    python -m venv venv
    ```
3.  **Activate the environment**:
    - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
    - Windows (CMD): `.\venv\Scripts\activate.bat`
    - Linux/macOS: `source venv/bin/activate`
4.  **Install dependencies**:
    ```powershell
    pip install -r requirements.txt
    pip install -r requirements.dev.txt
    ```

## Usage

1.  Start the application:
    ```powershell
    python main.py
    ```
2.  In the **API Configuration** pane:
    - Enter your Ergo API Base URL (e.g., `http://127.0.0.1:8089`).
    - Enter your Bearer Token.
    - Click **Load Config**.
3.  Interact with the API using the buttons in the **API Interaction** pane. Results will appear in the log area.

## Testing

To run the unit test suite:
```powershell
pytest test_api_client.py
```

## License

This project is licensed under the MIT License - see the [LICENSE.txt](LICENSE.txt) file for details.
