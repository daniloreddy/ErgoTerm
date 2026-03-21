import requests
import json
from typing import Dict, Any, Optional

class ErgoApiClient:
    """
    Client for interacting with the Ergo IRCd HTTP API.
    """
    def __init__(self, base_url: str, bearer_token: str):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json"
        }

    def _request(self, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/{endpoint}"
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=10)
            
            if response.status_code == 200:
                try:
                    response_json = response.json()
                    # Application-level success check based on API documentation
                    if isinstance(response_json, dict) and response_json.get("success") is False:
                        if "error" not in response_json:
                            response_json["error"] = "Unknown application failure"
                        response_json["error"] = f"API Logic Error: {response_json['error']}"
                    return response_json
                except json.JSONDecodeError:
                    return {"success": False, "error": "Failed to decode JSON response."}
            else:
                # HTTP error response (status_code != 200)
                return {"success": False, "error": f"HTTP Error {response.status_code}: {response.text[:100]}"}

        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network/Request Error: {e}"}

    # --- Endpoint Implementations ---

    def check_auth(self, account_name: str, passphrase: str) -> Dict[str, Any]:
        """Verifies account credentials."""
        data = {
            "accountName": account_name,
            "passphrase": passphrase
        }
        return self._request("check_auth", data=data)

    def get_account_details(self, account_name: str) -> Dict[str, Any]:
        """Fetches details for a specific account."""
        data = {"accountName": account_name}
        return self._request("account_details", data=data)

    def get_server_status(self) -> Dict[str, Any]:
        """Fetches the current status of the Ergo server."""
        return self._request("status")

    def rehash_server(self) -> Dict[str, Any]:
        """Triggers a server rehash (configuration reload)."""
        return self._request("rehash")

    def register_account(self, account_name: str, passphrase: str) -> Dict[str, Any]:
        """Registers a new NickServ account."""
        data = {
            "accountName": account_name,
            "passphrase": passphrase
        }
        return self._request("saregister", data=data)

    def list_accounts(self) -> Dict[str, Any]:
        """Fetches a list of all registered accounts."""
        return self._request("account_list")
