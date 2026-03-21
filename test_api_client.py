import pytest
import json
import requests
from ergo_api_client import ErgoApiClient

# Fixture to provide a mocked client instance
@pytest.fixture
def client():
    # Use a dummy URL and token for setup
    return ErgoApiClient("http://test.local:8089", "TEST_TOKEN_123")

# Fixture to provide a requests_mock object (assuming requests-mock is installed)
@pytest.fixture
def m(mocker):
    import requests_mock
    with requests_mock.Mocker() as m:
        yield m

def test_client_initialization(client):
    assert client.base_url == "http://test.local:8089"
    assert client.headers["Authorization"] == "Bearer TEST_TOKEN_123"

# --- /v1/status tests ---
def test_get_server_status_success(client, m):
    m.post(f"{client.base_url}/v1/status", json={"success": True, "version": "v1.0", "users": {"total": 5}}, status_code=200)
    result = client.get_server_status()
    assert result["success"] is True
    assert result["version"] == "v1.0"

def test_get_server_status_api_error(client, m):
    m.post(f"{client.base_url}/v1/status", json={"success": False, "error": "Maintenance Mode"}, status_code=200)
    result = client.get_server_status()
    assert result["success"] is False
    assert "Maintenance Mode" in result["error"]

# --- /v1/check_auth tests ---
def test_check_auth_success(client, m):
    m.post(f"{client.base_url}/v1/check_auth", json={"success": True, "accountName": "TestUser"}, status_code=200)
    result = client.check_auth("user", "pass")
    assert result["success"] is True
    assert result["accountName"] == "TestUser"

# --- /v1/account_details tests ---
def test_get_account_details_success(client, m):
    expected_response = {
        "success": True,
        "accountName": "CanonicalName",
        "email": "a@b.com",
        "registeredAt": "2024-01-01T00:00:00Z",
        "channels": ["#general"]
    }
    m.post(f"{client.base_url}/v1/account_details", json=expected_response, status_code=200)
    result = client.get_account_details("TestUser")
    assert result["success"] is True
    assert result["email"] == "a@b.com"

def test_get_account_details_not_found(client, m):
    m.post(f"{client.base_url}/v1/account_details", json={"success": False, "error": "ACCOUNT_NOT_FOUND"}, status_code=200)
    result = client.get_account_details("GhostUser")
    assert result["success"] is False

# --- /v1/rehash tests ---
def test_rehash_server_success(client, m):
    m.post(f"{client.base_url}/v1/rehash", json={"success": True}, status_code=200)
    result = client.rehash_server()
    assert result["success"] is True

def test_rehash_server_failure(client, m):
    m.post(f"{client.base_url}/v1/rehash", json={"success": False, "error": "Permissions Denied"}, status_code=200)
    result = client.rehash_server()
    assert result["success"] is False
    assert "Permissions Denied" in result["error"]

# --- /v1/saregister tests ---
def test_register_account_success(client, m):
    m.post(f"{client.base_url}/v1/saregister", json={"success": True, "errorCode": "OK"}, status_code=200)
    result = client.register_account("NewUser", "securepass")
    assert result["success"] is True
    assert result["errorCode"] == "OK"

def test_register_account_exists_error(client, m):
    m.post(f"{client.base_url}/v1/saregister", json={"success": False, "errorCode": "ACCOUNT_EXISTS"}, status_code=200)
    result = client.register_account("ExistingUser", "pass")
    assert result["success"] is False
    assert result["errorCode"] == "ACCOUNT_EXISTS"

# --- /v1/account_list tests ---
def test_account_list_success(client, m):
    expected_response = {
        "success": True, 
        "totalCount": 2,
        "accounts": [
            {"success": True, "accountName": "USER1"},
            {"success": True, "accountName": "USER2"}
        ]
    }
    m.post(f"{client.base_url}/v1/account_list", json=expected_response, status_code=200)
    result = client.list_accounts()
    assert result["success"] is True
    assert result["totalCount"] == 2
    assert len(result["accounts"]) == 2

def test_account_list_empty(client, m):
    expected_response = {"success": True, "totalCount": 0, "accounts": []}
    m.post(f"{client.base_url}/v1/account_list", json=expected_response, status_code=200)
    result = client.list_accounts()
    assert result["totalCount"] == 0

# --- General Resilience Tests (HTTP Errors & Network Errors) ---
def test_http_error_status_code(client, m):
    # Test for non-200 status codes
    m.post(f"{client.base_url}/v1/status", status_code=403, text="Forbidden Access")
    result = client.get_server_status()
    assert result["success"] is False
    assert "HTTP Error 403" in result["error"]

def test_json_decode_error(client, m):
    # Test case where status is 200 but body is invalid/empty JSON
    m.post(f"{client.base_url}/v1/status", status_code=200, text="This is not JSON")
    result = client.get_server_status()
    assert result["success"] is False
    assert "Failed to decode JSON response" in result["error"]
    
def test_network_connection_error(client, mocker):
    # Test network failure
    def raise_conn_error(*args, **kwargs):
        raise requests.exceptions.ConnectionError("Connection timed out")

    mocker.patch("requests.post", side_effect=raise_conn_error)
    
    result = client.get_server_status()
    
    assert result["success"] is False
    assert "Network/Request Error" in result["error"]
