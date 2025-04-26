Certainly! Below are well-structured pytest test cases for the user story: **Send email notifications for task completion or failures**.  
Each test case uses appropriate setup and teardown, covers main and edge cases, and contains descriptive comments.

Assumptions:

- The code under test provides a function like `send_task_notification(status, user_email, task_id, error_details=None, suggested_actions=None)`.
- There is an email sending service or class, which can be mocked.
- The notification can have either a "completed" or "failed" status.
- For failures, error details and suggested actions must be included.

Here is the code:

```python
import pytest
from unittest.mock import patch, MagicMock

# Example notification function to be tested (to be replaced with the actual one)
def send_task_notification(status, user_email, task_id, error_details=None, suggested_actions=None):
    # Placeholder for the real implementation
    pass

@pytest.fixture(autouse=True)
def setup_and_teardown():
    # Setup: Could initialize test data, mock services, etc.
    yield
    # Teardown: Clean up resources, reset mocks, etc.

# Helper fixture to patch the email sending service
@pytest.fixture
def mock_email_service():
    with patch('path.to.email_service.send_email') as mock_send:
        yield mock_send

# 1. Test email notification for successful task completion
def test_email_sent_on_task_completion(mock_email_service):
    """
    Test that an email is sent when a task is completed successfully.
    """
    user_email = "user@example.com"
    task_id = "task_123"
    status = "completed"

    send_task_notification(status, user_email, task_id)

    # Assert that send_email was called once
    assert mock_email_service.call_count == 1
    # Extract arguments to check email content
    args, kwargs = mock_email_service.call_args
    assert user_email in kwargs['to']
    assert "completed" in kwargs['subject'].lower()
    assert task_id in kwargs['body']

# 2. Test email notification for task failure with error details and suggestions
def test_email_sent_on_task_failure_with_details(mock_email_service):
    """
    Test that an email is sent on task failure, including error details and suggested actions.
    """
    user_email = "user@example.com"
    task_id = "task_456"
    status = "failed"
    error_details = "Database connection timeout"
    suggested_actions = "Check DB server connectivity."

    send_task_notification(status, user_email, task_id, error_details, suggested_actions)

    # Assert that send_email was called once
    assert mock_email_service.call_count == 1
    args, kwargs = mock_email_service.call_args
    assert user_email in kwargs['to']
    assert "failure" in kwargs['subject'].lower()
    assert error_details in kwargs['body']
    assert suggested_actions in kwargs['body']

# 3. Edge case: Invalid email address
def test_email_not_sent_with_invalid_email(mock_email_service):
    """
    Test that no email is sent if the user email is invalid.
    """
    invalid_email = "invalid-email"
    task_id = "task_789"
    status = "completed"

    with pytest.raises(ValueError):
        send_task_notification(status, invalid_email, task_id)

    # Assert that send_email was never called
    mock_email_service.assert_not_called()

# 4. Edge case: Missing error details on failure
def test_failure_email_requires_error_details(mock_email_service):
    """
    Test that an exception is raised if error details are missing on failure notification.
    """
    user_email = "user@example.com"
    task_id = "task_987"
    status = "failed"
    # error_details is None

    with pytest.raises(ValueError):
        send_task_notification(status, user_email, task_id)

    mock_email_service.assert_not_called()

# 5. Edge case: Empty suggested actions on failure (should still send email)
def test_failure_email_without_suggested_actions(mock_email_service):
    """
    Test that failure email sends even if suggested actions are not provided, but error details are included.
    """
    user_email = "user@example.com"
    task_id = "task_654"
    status = "failed"
    error_details = "File not found"

    send_task_notification(status, user_email, task_id, error_details)

    assert mock_email_service.call_count == 1
    args, kwargs = mock_email_service.call_args
    assert error_details in kwargs['body']

# 6. Edge case: Unknown status value
def test_notification_with_unknown_status(mock_email_service):
    """
    Test that an exception is raised if an unknown status is provided.
    """
    user_email = "user@example.com"
    task_id = "task_321"
    status = "in_progress"  # Invalid

    with pytest.raises(ValueError):
        send_task_notification(status, user_email, task_id)

    mock_email_service.assert_not_called()
```

---

**Explanations:**

- **Setup/Teardown:** The `setup_and_teardown` fixture is ready for any needed resource management.
- **Mocking:** The `mock_email_service` fixture patches the email sending method to intercept and inspect calls.
- **Test Cases:**  
  - Main flows: successful completion and failure notifications.
  - Edge cases: invalid email, missing error details, missing suggested actions, and invalid status.
- **Assertions:**  
  - Confirm correct calls, email content, and proper handling of invalid input.

You can adapt `send_task_notification` and patch path according to your actual implementation. Each test is clear, isolated, and self-descriptive for maintainability.