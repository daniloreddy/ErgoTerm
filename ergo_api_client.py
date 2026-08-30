import json
from typing import Any

import httpx


class ErgoApiClient:
    """
    Client for interacting with the Ergo IRCd HTTP API.
    """

    def __init__(self, base_url: str, bearer_token: str):
        self.base_url = base_url.rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {bearer_token}",
            "Content-Type": "application/json",
        }

    async def _request(
        self, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        url = f"{self.base_url}/v1/{endpoint}"

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(url, headers=self.headers, json=data)

            if response.status_code == 200:
                try:
                    response_json = response.json()
                    if not isinstance(response_json, dict):
                        return {
                            "success": False,
                            "error": (
                                "Unexpected response type: "
                                f"{type(response_json).__name__}"
                            ),
                        }
                    # Application-level success check based on API documentation
                    if response_json.get("success") is False:
                        if "error" not in response_json:
                            response_json["error"] = (
                                response_json.get("errorCode") or "Request unsuccessful"
                            )
                        response_json["error"] = (
                            f"API Logic Error: {response_json['error']}"
                        )
                    return response_json
                except json.JSONDecodeError:
                    return {
                        "success": False,
                        "error": "Failed to decode JSON response.",
                    }
            else:
                # HTTP error response (status_code != 200)
                return {
                    "success": False,
                    "error": f"HTTP Error {response.status_code}: {response.text[:100]}",
                }

        except httpx.HTTPError as e:
            return {"success": False, "error": f"Network/Request Error: {e}"}

    # --- Endpoint Implementations ---

    async def check_auth(self, account_name: str, passphrase: str) -> dict[str, Any]:
        """Verifies account credentials."""
        data = {"accountName": account_name, "passphrase": passphrase}
        return await self._request("check_auth", data=data)

    async def get_account_details(self, account_name: str) -> dict[str, Any]:
        """Fetches details for a specific account."""
        data = {"accountName": account_name}
        return await self._request("account_details", data=data)

    async def get_server_status(self) -> dict[str, Any]:
        """Fetches the current status of the Ergo server."""
        return await self._request("status")

    async def rehash_server(self) -> dict[str, Any]:
        """Triggers a server rehash (configuration reload)."""
        return await self._request("rehash")

    async def register_account(
        self, account_name: str, passphrase: str
    ) -> dict[str, Any]:
        """Registers a new NickServ account."""
        data = {"accountName": account_name, "passphrase": passphrase}
        return await self._request("saregister", data=data)

    async def list_accounts(self) -> dict[str, Any]:
        """Fetches a list of all registered accounts."""
        return await self._request("account_list")
