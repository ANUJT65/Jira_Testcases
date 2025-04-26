Certainly! Below is a **comprehensive pytest test suite** that covers the main functionality and edge cases for your user story:

- **Story:** Send email notifications for task completion or failures
- **Role:** Operations Team
- **Goal:** Notify users about dormant account review task status
- **Acceptance Criteria:**  
  1. Email notifications are sent for task completion.  
  2. Failure alerts include error details and suggested actions.

**Assumptions:**
- There is a function `send_task_notification(task_id, status, error=None)` responsible for sending emails.
- There is an email sending module/class (`EmailService`) that is mocked during tests.
- The email content is constructed with required details.
- We use pytest fixtures for setup/teardown.

---

```python
import pytest
from unittest.mock import patch, MagicMock

# Assuming these are our modules under test
from notifications import send_task_notification, EmailService

# Sample data for tests
task_id_success = "TASK12345"
task_id_failure = "TASK54321"
user_email = "ops_team@example.com"
error_detail = "Database connection timeout"
suggested_action = "Check network connectivity and retry the operation."

@pytest.fixture(autouse=True)
def mock_email_service(monkeypatch):
    """
    Fixture to mock the EmailService's send_email method for all tests.
    """
    mock_send = MagicMock(return_value=True)
    monkeypatch.setattr(EmailService, "send_email", mock_send)
    yield mock_send  # provide the mock to test functions if needed

def test_email_sent_on_task_completion(mock_email_service):
    """
    Test that an email is sent when a dormant account review task completes successfully.
    """
    status = "completed"
    result = send_task_notification(task_id=task_id_success, status=status)

    # Assert email was sent
    assert result is True
    mock_email_service.assert_called_once()
    args, kwargs = mock_email_service.call_args
    # Check that email content mentions completion and task id
    assert "completed" in kwargs['subject'].lower()
    assert task_id_success in kwargs['body']

def test_email_sent_on_task_failure_with_details_and_suggestion(mock_email_service):
    """
    Test that a detailed failure alert email is sent with error and suggestion on failure.
    """
    status = "failed"
    error = {
        "detail": error_detail,
        "suggested_action": suggested_action
    }
    result = send_task_notification(task_id=task_id_failure, status=status, error=error)

    # Assert email was sent
    assert result is True
    mock_email_service.assert_called_once()
    args, kwargs = mock_email_service.call_args
    # Check that email content covers failure, task_id, error details, and suggested actions
    assert "failed" in kwargs['subject'].lower()
    assert task_id_failure in kwargs['body']
    assert error_detail in kwargs['body']
    assert suggested_action in kwargs['body']

def test_no_email_sent_on_invalid_status(mock_email_service):
    """
    Test that no email is sent if the status is invalid (neither 'completed' nor 'failed').
    """
    status = "in_progress"
    result = send_task_notification(task_id=task_id_success, status=status)
    assert result is False
    mock_email_service.assert_not_called()

def test_failure_email_missing_error_info(mock_email_service):
    """
    Edge Case: If status is 'failed' but error info is missing, email should still be sent with a generic message.
    """
    status = "failed"
    result = send_task_notification(task_id=task_id_failure, status=status, error=None)
    assert result is True
    mock_email_service.assert_called_once()
    args, kwargs = mock_email_service.call_args
    # Should mention generic failure
    assert "failed" in kwargs['subject'].lower()
    assert "details were not provided" in kwargs['body'].lower()

def test_email_service_exception_handling(mock_email_service):
    """
    Edge Case: If the email service fails (e.g., SMTP server is down), function should handle and return False.
    """
    mock_email_service.side_effect = Exception("SMTP server not reachable")
    status = "completed"
    result = send_task_notification(task_id=task_id_success, status=status)
    assert result is False

def test_multiple_email_recipients(monkeypatch):
    """
    Edge Case: Ensure the function can handle multiple recipients if required.
    """
    mock_send = MagicMock(return_value=True)
    monkeypatch.setattr(EmailService, "send_email", mock_send)
    recipients = ["ops_team@example.com", "lead@example.com"]
    status = "completed"

    # Assuming send_task_notification can take recipients as a parameter
    result = send_task_notification(task_id=task_id_success, status=status, recipients=recipients)
    assert result is True
    mock_send.assert_called_once()
    args, kwargs = mock_send.call_args
    assert set(kwargs['to']) == set(recipients)

# Additional teardown can be handled via fixtures if needed
```

---

**Test Suite Features:**

- **Setup/Teardown:** All email calls are mocked using a fixture (`mock_email_service`).
- **Main Functionality:**
    - Emails are sent for completion and failure.
    - Failure emails contain mandatory error details and suggestions.
- **Edge Cases:**
    - Invalid status: No email sent.
    - Missing error info: Generic failure message sent.
    - Email service failure: Function handles exception and returns failure.
    - Multiple recipients: Function supports more than one recipient.
- **Comments:** Each test case is clearly commented with its intent.

**Modify the import paths and function signatures as per your actual implementation.**