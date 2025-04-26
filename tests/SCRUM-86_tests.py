Certainly! Below are **comprehensive pytest test cases** for the given user story. The tests assume the existence of a core function, e.g., `send_task_notification(task, status, error_details=None)`, and a mockable email-sending backend (e.g., via a function/class `EmailSender`). You may need to adapt names to fit your actual implementation.

The tests cover:

1. **Success notification** (task completed)
2. **Failure notification** (with error details & suggested actions)
3. **Edge cases** (missing info, invalid emails, email backend failure, empty recipient list)

```python
import pytest
from unittest.mock import patch, MagicMock

# Example Task and EmailSender classes for context
class Task:
    def __init__(self, id, owner_email, name):
        self.id = id
        self.owner_email = owner_email
        self.name = name

class EmailSender:
    def send_email(self, to_address, subject, body):
        pass  # Actual implementation sends email

# System under test (SUT)
def send_task_notification(task, status, error_details=None, email_sender=None):
    """
    Sends an email notification based on task status.
    status: 'success'|'failure'
    error_details: dict with 'error' and 'suggested_action' if status=='failure'
    """
    if not task or not task.owner_email:
        raise ValueError("Invalid Task or missing owner email")
    if email_sender is None:
        raise ValueError("Email sender required")

    if status == 'success':
        subject = f"Task '{task.name}' Completed"
        body = f"Task ID {task.id} has been completed successfully."
    elif status == 'failure':
        subject = f"Task '{task.name}' Failed"
        if not error_details or 'error' not in error_details or 'suggested_action' not in error_details:
            raise ValueError("Error details required for failure notifications")
        body = (f"Task ID {task.id} failed with error: {error_details['error']}\n"
                f"Suggested Action: {error_details['suggested_action']}")
    else:
        raise ValueError("Unknown status")

    email_sender.send_email(task.owner_email, subject, body)

# Pytest fixtures for setup/teardown
@pytest.fixture
def mock_email_sender():
    with patch('__main__.EmailSender.send_email', autospec=True) as mock_send:
        yield mock_send

@pytest.fixture
def sample_task():
    return Task(id=123, owner_email="user@example.com", name="Dormant Account Review")

# Test Cases

def test_success_email_sent(sample_task, mock_email_sender):
    """Test that a completion email is sent with correct content."""
    email_sender = EmailSender()
    send_task_notification(sample_task, status='success', email_sender=email_sender)
    mock_email_sender.assert_called_once()
    args, kwargs = mock_email_sender.call_args
    assert args[1] == sample_task.owner_email
    assert "Completed" in args[2]
    assert str(sample_task.id) in args[3]

def test_failure_email_sent_with_error_details(sample_task, mock_email_sender):
    """Test that a failure email includes error details and suggested actions."""
    email_sender = EmailSender()
    error_details = {"error": "Timeout while connecting to DB", "suggested_action": "Check DB connectivity"}
    send_task_notification(sample_task, status='failure', error_details=error_details, email_sender=email_sender)
    mock_email_sender.assert_called_once()
    args, kwargs = mock_email_sender.call_args
    assert args[1] == sample_task.owner_email
    assert "Failed" in args[2]
    assert error_details["error"] in args[3]
    assert error_details["suggested_action"] in args[3]

def test_failure_missing_error_details(sample_task):
    """Test that missing error details for failure raises ValueError."""
    email_sender = EmailSender()
    with pytest.raises(ValueError, match="Error details required for failure notifications"):
        send_task_notification(sample_task, status='failure', email_sender=email_sender)

def test_invalid_status_raises(sample_task):
    """Test that invalid status raises ValueError."""
    email_sender = EmailSender()
    with pytest.raises(ValueError, match="Unknown status"):
        send_task_notification(sample_task, status='unknown', email_sender=email_sender)

def test_missing_email_address_raises():
    """Test that missing recipient email raises ValueError."""
    task = Task(id=456, owner_email=None, name="Dormant Account Review")
    email_sender = EmailSender()
    with pytest.raises(ValueError, match="Invalid Task or missing owner email"):
        send_task_notification(task, status='success', email_sender=email_sender)

def test_empty_recipient_email(sample_task):
    """Edge case: empty string as recipient email raises ValueError."""
    sample_task.owner_email = ""
    email_sender = EmailSender()
    with pytest.raises(ValueError, match="Invalid Task or missing owner email"):
        send_task_notification(sample_task, status='success', email_sender=email_sender)

def test_email_backend_failure(sample_task):
    """Test that exceptions from email backend are propagated."""
    email_sender = EmailSender()
    with patch.object(email_sender, "send_email", side_effect=Exception("SMTP Failure")):
        with pytest.raises(Exception, match="SMTP Failure"):
            send_task_notification(sample_task, status='success', email_sender=email_sender)

def test_no_email_sender_provided(sample_task):
    """Test that not providing an email sender raises ValueError."""
    with pytest.raises(ValueError, match="Email sender required"):
        send_task_notification(sample_task, status='success')

# Additional edge case: malformed error details
def test_failure_with_incomplete_error_details(sample_task):
    """Test that incomplete error_details dict raises ValueError."""
    email_sender = EmailSender()
    bad_details = {"error": "Disk Full"}
    with pytest.raises(ValueError, match="Error details required for failure notifications"):
        send_task_notification(sample_task, status='failure', error_details=bad_details, email_sender=email_sender)
```

---

### **Notes:**
- **Fixtures** (`sample_task`, `mock_email_sender`) handle **setup/teardown**.
- Tests cover both **happy path** and **edge/error cases**.
- **Comments** describe the intent of each test.
- **Mocking** is used to avoid sending real emails.
- **Adapt class/function names as per your codebase**.

Let me know if you need test cases for a different language or further breakdown!