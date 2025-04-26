Certainly! Below are comprehensive pytest test cases for the described user story. These tests assume you have a module (e.g., `notifications.py`) with a function (e.g., `send_task_notification`) that sends emails for task completion and failures.

**Assumptions:**
- You use an email sending service that can be mocked.
- `send_task_notification(task, status, error_details=None)` is the function to test.
- On success, `status="completed"`. On failure, `status="failed"`, and `error_details` is a dictionary with `"error"` and `"suggested_actions"`.
- The function is expected to send emails to the task owner.

Below is the pytest code:

```python
import pytest
from unittest.mock import patch, MagicMock
from notifications import send_task_notification, EmailServiceError

# Sample data for use in tests
TASK_SAMPLE = {
    "id": 123,
    "name": "Dormant Account Review",
    "owner_email": "ops.user@example.com"
}

ERROR_DETAILS = {
    "error": "Database connection timeout",
    "suggested_actions": "Please check your network settings or contact DB admin."
}

@pytest.fixture
def mock_email_service():
    with patch("notifications.EmailService") as MockService:
        instance = MockService.return_value
        instance.send_email = MagicMock()
        yield instance

@pytest.fixture
def completed_task():
    return TASK_SAMPLE.copy()

@pytest.fixture
def failed_task():
    return TASK_SAMPLE.copy()

# --- Test Cases ---

def setup_module(module):
    """Setup resources before any tests run."""
    print("\n[SETUP] Starting notification tests.")

def teardown_module(module):
    """Cleanup resources after all tests have run."""
    print("\n[TEARDOWN] Completed notification tests.")

def test_send_completion_email_success(mock_email_service, completed_task):
    """
    Test that an email is sent when a task is completed successfully.
    """
    send_task_notification(completed_task, status="completed")
    # Check that an email was sent
    mock_email_service.send_email.assert_called_once()
    args, kwargs = mock_email_service.send_email.call_args
    assert completed_task["owner_email"] in kwargs["to"]
    assert "completed" in kwargs["subject"].lower()
    assert completed_task["name"] in kwargs["body"]

def test_send_failure_email_with_error_details(mock_email_service, failed_task):
    """
    Test that a failure email includes error details and suggested actions.
    """
    send_task_notification(failed_task, status="failed", error_details=ERROR_DETAILS)
    mock_email_service.send_email.assert_called_once()
    args, kwargs = mock_email_service.send_email.call_args
    assert failed_task["owner_email"] in kwargs["to"]
    assert "failed" in kwargs["subject"].lower()
    assert ERROR_DETAILS["error"] in kwargs["body"]
    assert ERROR_DETAILS["suggested_actions"] in kwargs["body"]

def test_send_failure_email_no_error_details(mock_email_service, failed_task):
    """
    Test that a failure email is still sent if error details are missing.
    """
    send_task_notification(failed_task, status="failed", error_details=None)
    mock_email_service.send_email.assert_called_once()
    args, kwargs = mock_email_service.send_email.call_args
    assert "failed" in kwargs["subject"].lower()
    # The body should handle the absence of error details gracefully
    assert "Details not available" in kwargs["body"] or "error" not in kwargs["body"].lower()

def test_email_service_error_handling(mock_email_service, completed_task):
    """
    Test that an exception in the email service is handled gracefully.
    """
    mock_email_service.send_email.side_effect = EmailServiceError("SMTP server down")
    with pytest.raises(EmailServiceError):
        send_task_notification(completed_task, status="completed")

def test_no_email_sent_for_unknown_status(mock_email_service, completed_task):
    """
    Test that no email is sent if status is not 'completed' or 'failed'.
    """
    send_task_notification(completed_task, status="in_progress")
    mock_email_service.send_email.assert_not_called()

def test_empty_email_address_handling(mock_email_service, completed_task):
    """
    Test that no email is sent if the owner's email address is missing.
    """
    completed_task["owner_email"] = ""
    send_task_notification(completed_task, status="completed")
    mock_email_service.send_email.assert_not_called()

def test_multiple_recipients_supported(mock_email_service, completed_task):
    """
    Test that notifications can be sent to multiple recipients if configured.
    """
    completed_task["owner_email"] = ["ops.user@example.com", "manager@example.com"]
    send_task_notification(completed_task, status="completed")
    mock_email_service.send_email.assert_called_once()
    args, kwargs = mock_email_service.send_email.call_args
    assert "ops.user@example.com" in kwargs["to"]
    assert "manager@example.com" in kwargs["to"]

```

---

**Key Points:**

- **Setup/Teardown:** Uses `setup_module` and `teardown_module` for global setup/cleanup; fixtures handle mocks.
- **Mocks:** All email sending is mocked, so no real emails are sent.
- **Comprehensive coverage:** Includes normal and edge cases (missing email, missing error details, service errors, unknown status, multiple recipients).
- **Descriptive comments:** Each test is documented for clarity.

You can adjust paths, error classes, and function signatures to match your actual implementation.