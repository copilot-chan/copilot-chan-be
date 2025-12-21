import os

import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi.testclient import TestClient
from unittest.mock import patch

from dotenv import load_dotenv
load_dotenv()

from app.main import app # noqa: E402
from app.config import settings # noqa: E402

client = TestClient(app)

def test_webhook_auth_success():
    """Test webhook with correct secret"""
    # Mocking settings to ensure the secret is set
    with patch.object(settings, 'MEM0_WEBHOOK_SECRET', 'test-secret'):
        # Mock background tasks to avoid actual execution
        with patch('app.routers.memory.mem0.reset_cache'):
            response = client.post(
                "/memory/webhook?secret=test-secret",
                json={"event_details": {"user_id": "test-user"}}
            )
            assert response.status_code == 200
            assert response.json() == {"status": "success"}

def test_webhook_auth_failure_wrong_secret():
    """Test webhook with incorrect secret"""
    with patch.object(settings, 'MEM0_WEBHOOK_SECRET', 'test-secret'):
        response = client.post(
            "/memory/webhook?secret=wrong-secret",
            json={"event_details": {"user_id": "test-user"}}
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}

def test_webhook_auth_failure_missing_secret():
    """Test webhook with missing secret"""
    with patch.object(settings, 'MEM0_WEBHOOK_SECRET', 'test-secret'):
        response = client.post(
            "/memory/webhook",
            json={"event_details": {"user_id": "test-user"}}
        )
        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden"}

def test_webhook_no_secret_configured():
    """Test webhook when no secret is configured on server"""
    with patch.object(settings, 'MEM0_WEBHOOK_SECRET', None):
         with patch('app.routers.memory.mem0.reset_cache'):
            response = client.post(
                "/memory/webhook",
                json={"event_details": {"user_id": "test-user"}}
            )
            assert response.status_code == 200
            assert response.json() == {"status": "success"}

if __name__ == "__main__":
    # Manually run tests if pytest is not used directly
    try:
        test_webhook_auth_success()
        print("test_webhook_auth_success passed")
        test_webhook_auth_failure_wrong_secret()
        print("test_webhook_auth_failure_wrong_secret passed")
        test_webhook_auth_failure_missing_secret()
        print("test_webhook_auth_failure_missing_secret passed")
        test_webhook_no_secret_configured()
        print("test_webhook_no_secret_configured passed")
        print("All tests passed!")
    except AssertionError as e:
        print(f"Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"An error occurred: {e}")
        exit(1)
