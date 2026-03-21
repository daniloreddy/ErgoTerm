import json
import os
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button, Log, Static
from textual.containers import Container, Vertical, Horizontal
from textual.binding import Binding
from ergo_api_client import ErgoApiClient
from typing import Optional
import webbrowser

# --- Configuration ---
DEFAULT_API_URL = "http://127.0.0.1:8089"
DEFAULT_TOKEN = "YOUR_BEARER_TOKEN_HERE" 
CONFIG_FILE = Path.home() / ".ergo_api_config.json"

class ErgoTUI(App):
    """Textual User Interface for the Ergo IRCd API."""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+t", "open_docs", "Open Docs"),
    ]

    CSS_PATH = "tui.css"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        with Container(id="main_layout"):
            # --- Configuration Pane ---
            with Vertical(id="config_pane"):
                yield Static("API Configuration", classes="title")
                yield Input(value=DEFAULT_API_URL, placeholder="API Base URL (e.g., http://127.0.0.1:8089)", id="api_url_input")
                yield Input(value=DEFAULT_TOKEN, placeholder="Bearer Token", id="token_input", password=True)
                yield Button("Load Config", id="load_config_btn", variant="primary")
                yield Button("Open Ergo Docs (Web)", id="open_docs_btn_pane", variant="default")
                yield Static("Client Loaded: No", id="client_status")

            # --- Interaction Pane ---
            with Vertical(id="interaction_pane"):
                yield Static("API Interaction", classes="title")
                
                # Endpoint Selection/Inputs
                with Horizontal(id="endpoint_buttons"):
                    yield Button("Status", id="get_status_btn", variant="success")
                    yield Button("Check Auth", id="check_auth_btn", variant="success")
                    yield Button("Register", id="register_btn", variant="warning")
                    yield Button("Rehash", id="rehash_btn", variant="default")
                    yield Button("Acc List", id="list_accounts_btn", variant="default")

                with Horizontal(id="input_fields"):
                    yield Input(placeholder="Username / Account", id="input_arg_1")
                    yield Input(placeholder="Password / Passphrase", id="input_arg_2", password=True)
                
                yield Static("Last Response:", classes="subtitle")
                yield Log(id="api_log", highlight=True)
                
        yield Footer()

    def on_mount(self) -> None:
        self.api_client: Optional[ErgoApiClient] = None
        # Initialize status class
        self.query_one("#client_status").add_class("status_red")
        self.load_saved_config()

    def load_saved_config(self) -> None:
        """Loads the configuration from the user's home directory if it exists."""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    config = json.load(f)
                
                api_url = config.get("api_url")
                token = config.get("bearer_token")
                
                if api_url:
                    self.query_one("#api_url_input", Input).value = api_url
                if token:
                    self.query_one("#token_input", Input).value = token
                
            except Exception:
                # Silently fail if config is corrupt
                pass

    def save_current_config(self, api_url: str, token: str) -> None:
        """Saves the configuration to the user's home directory."""
        try:
            config = {
                "api_url": api_url,
                "bearer_token": token
            }
            with open(CONFIG_FILE, "w") as f:
                json.dump(config, f, indent=4)
        except Exception:
            # Silently fail if save fails
            pass

    def action_open_docs(self) -> None:
        """Opens the Ergo API documentation URL in the default web browser."""
        webbrowser.open("https://ergo.chat/docs/api")
        self.query_one(Log).write("[blue]Opened Ergo API documentation in browser.[/blue]")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one(Log)
        
        if event.button.id == "load_config_btn":
            self.load_config(log)
        
        elif event.button.id == "open_docs_btn_pane":
            self.action_open_docs()

        elif event.button.id == "get_status_btn":
            self.call_api_method(log, "get_server_status", [], "Server Status")

        elif event.button.id == "check_auth_btn":
            arg1 = self.query_one("#input_arg_1", Input).value
            arg2 = self.query_one("#input_arg_2", Input).value
            self.call_api_method(log, "check_auth", [arg1, arg2], "Check Auth")
            
        elif event.button.id == "register_btn":
            arg1 = self.query_one("#input_arg_1", Input).value
            arg2 = self.query_one("#input_arg_2", Input).value
            self.call_api_method(log, "register_account", [arg1, arg2], "Register Account")

        elif event.button.id == "rehash_btn":
            self.call_api_method(log, "rehash_server", [], "Rehash")

        elif event.button.id == "list_accounts_btn":
            self.call_api_method(log, "list_accounts", [], "Account List")

    def load_config(self, log: Log) -> None:
        api_url = self.query_one("#api_url_input", Input).value
        token = self.query_one("#token_input", Input).value
        
        if not api_url or not token or token == DEFAULT_TOKEN:
            log.write("[yellow]Warning:[/yellow] URL and Token are required. Token is at default value.")
            return

        # Save successfully entered configuration for the next run
        self.save_current_config(api_url, token)

        try:
            self.api_client = ErgoApiClient(api_url, token)
            status_widget = self.query_one("#client_status", Static)
            status_widget.update("Client Loaded: Yes")
            status_widget.remove_class("status_red")
            status_widget.add_class("status_green")
            log.write(f"[green]Client configured successfully for URL: {api_url}[/green]")
        except Exception as e:
            log.write(f"[red]Configuration Error:[/red] {e}")
            status_widget = self.query_one("#client_status", Static)
            status_widget.update("Client Loaded: No")
            status_widget.remove_class("status_green")
            status_widget.add_class("status_red")


    def call_api_method(self, log: Log, method_name: str, args: list, display_name: str) -> None:
        if not self.api_client:
            log.write("[yellow]Warning:[/yellow] API client not loaded. Please load configuration first.")
            return

        log.write(f"-> Calling {display_name}...")
        
        try:
            method = getattr(self.api_client, method_name)
            
            # Synchronous call blocking the TUI - Needs AsyncIO for production, 
            response = method(*args)
            
            log.write(f"<- {display_name} Response:")
            log.write(json.dumps(response, indent=2))
            
        except AttributeError:
            log.write(f"[red]Error:[/red] API method '{method_name}' not found in client.")
        except Exception as e:
            log.write(f"[red]Execution Error:[/red] {e}")


if __name__ == "__main__":
    app = ErgoTUI()
    app.run()
