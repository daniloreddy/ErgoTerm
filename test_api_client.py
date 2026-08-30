import httpx
import pytest
import respx

from ergo_api_client import ErgoApiClient


# Fixture to provide a client instance
@pytest.fixture
def client():
    # Use a dummy URL and token for setup
    return ErgoApiClient("http://test.local:8089", "TEST_TOKEN_123")


# Fixture to provide a respx router for mocking httpx requests
@pytest.fixture
def m():
    with respx.mock(assert_all_called=False) as respx_mock:
        yield respx_mock


def test_client_initialization(client):
    assert client.base_url == "http://test.local:8089"
    assert client.headers["Authorization"] == "Bearer TEST_TOKEN_123"


# --- /v1/status tests ---
async def test_get_server_status_success(client, m):
    m.post(f"{client.base_url}/v1/status").mock(
        return_value=httpx.Response(
            200, json={"success": True, "version": "v1.0", "users": {"total": 5}}
        )
    )
    result = await client.get_server_status()
    assert result["success"] is True
    assert result["version"] == "v1.0"


async def test_get_server_status_api_error(client, m):
    m.post(f"{client.base_url}/v1/status").mock(
        return_value=httpx.Response(
            200, json={"success": False, "error": "Maintenance Mode"}
        )
    )
    result = await client.get_server_status()
    assert result["success"] is False
    assert "Maintenance Mode" in result["error"]


# --- /v1/check_auth tests ---
async def test_check_auth_success(client, m):
    m.post(f"{client.base_url}/v1/check_auth").mock(
        return_value=httpx.Response(
            200, json={"success": True, "accountName": "TestUser"}
        )
    )
    result = await client.check_auth("user", "pass")
    assert result["success"] is True
    assert result["accountName"] == "TestUser"


async def test_check_auth_failure(client, m):
    m.post(f"{client.base_url}/v1/check_auth").mock(
        return_value=httpx.Response(200, json={"success": False})
    )
    result = await client.check_auth("user", "wrongpass")
    assert result["success"] is False
    assert "error" in result
    assert "Unknown" not in result["error"]


# --- /v1/account_details tests ---
async def test_get_account_details_success(client, m):
    expected_response = {
        "success": True,
        "accountName": "CanonicalName",
        "email": "a@b.com",
        "registeredAt": "2024-01-01T00:00:00Z",
        "channels": ["#general"],
    }
    m.post(f"{client.base_url}/v1/account_details").mock(
        return_value=httpx.Response(200, json=expected_response)
    )
    result = await client.get_account_details("TestUser")
    assert result["success"] is True
    assert result["email"] == "a@b.com"


async def test_get_account_details_not_found(client, m):
    m.post(f"{client.base_url}/v1/account_details").mock(
        return_value=httpx.Response(
            200, json={"success": False, "error": "ACCOUNT_NOT_FOUND"}
        )
    )
    result = await client.get_account_details("GhostUser")
    assert result["success"] is False


# --- /v1/rehash tests ---
async def test_rehash_server_success(client, m):
    m.post(f"{client.base_url}/v1/rehash").mock(
        return_value=httpx.Response(200, json={"success": True})
    )
    result = await client.rehash_server()
    assert result["success"] is True


async def test_rehash_server_failure(client, m):
    m.post(f"{client.base_url}/v1/rehash").mock(
        return_value=httpx.Response(
            200, json={"success": False, "error": "Permissions Denied"}
        )
    )
    result = await client.rehash_server()
    assert result["success"] is False
    assert "Permissions Denied" in result["error"]


# --- /v1/saregister tests ---
async def test_register_account_success(client, m):
    m.post(f"{client.base_url}/v1/saregister").mock(
        return_value=httpx.Response(200, json={"success": True, "errorCode": "OK"})
    )
    result = await client.register_account("NewUser", "securepass")
    assert result["success"] is True
    assert result["errorCode"] == "OK"


async def test_register_account_exists_error(client, m):
    m.post(f"{client.base_url}/v1/saregister").mock(
        return_value=httpx.Response(
            200, json={"success": False, "errorCode": "ACCOUNT_EXISTS"}
        )
    )
    result = await client.register_account("ExistingUser", "pass")
    assert result["success"] is False
    assert result["errorCode"] == "ACCOUNT_EXISTS"
    assert "ACCOUNT_EXISTS" in result["error"]


# --- /v1/account_list tests ---
async def test_account_list_success(client, m):
    expected_response = {
        "success": True,
        "totalCount": 2,
        "accounts": [
            {"success": True, "accountName": "USER1"},
            {"success": True, "accountName": "USER2"},
        ],
    }
    m.post(f"{client.base_url}/v1/account_list").mock(
        return_value=httpx.Response(200, json=expected_response)
    )
    result = await client.list_accounts()
    assert result["success"] is True
    assert result["totalCount"] == 2
    assert len(result["accounts"]) == 2


async def test_account_list_empty(client, m):
    expected_response = {"success": True, "totalCount": 0, "accounts": []}
    m.post(f"{client.base_url}/v1/account_list").mock(
        return_value=httpx.Response(200, json=expected_response)
    )
    result = await client.list_accounts()
    assert result["totalCount"] == 0


# --- General Resilience Tests (HTTP Errors & Network Errors) ---
async def test_http_error_status_code(client, m):
    # Test for non-200 status codes
    m.post(f"{client.base_url}/v1/status").mock(
        return_value=httpx.Response(403, text="Forbidden Access")
    )
    result = await client.get_server_status()
    assert result["success"] is False
    assert "HTTP Error 403" in result["error"]


async def test_json_decode_error(client, m):
    # Test case where status is 200 but body is invalid/empty JSON
    m.post(f"{client.base_url}/v1/status").mock(
        return_value=httpx.Response(200, text="This is not JSON")
    )
    result = await client.get_server_status()
    assert result["success"] is False
    assert "Failed to decode JSON response" in result["error"]


async def test_non_dict_json_response(client, m):
    # Test case where status is 200 and body is valid JSON but not an object
    m.post(f"{client.base_url}/v1/status").mock(
        return_value=httpx.Response(200, json=[1, 2, 3])
    )
    result = await client.get_server_status()
    assert result["success"] is False
    assert "Unexpected response type" in result["error"]


async def test_network_connection_error(client, m):
    # Test network failure
    m.post(f"{client.base_url}/v1/status").mock(
        side_effect=httpx.ConnectError("Connection timed out")
    )
    result = await client.get_server_status()
    assert result["success"] is False
    assert "Network/Request Error" in result["error"]
