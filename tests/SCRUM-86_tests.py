Certainly! Below is a well-structured set of `pytest` test cases for the provided user story. These tests assume the existence of an `EmailNotifier` class and a `Task` object/model, which you may need to adjust to fit your actual implementation.

The tests cover both "happy path" and edge cases for sending email notifications upon task completion or failure. Mocks are used to avoid sending real emails.

```python
import pytest
from unittest.mock import patch, MagicMock

# Sample stubs to represent your email notifier and task classes
class Task:
    def __init__(self, id, status, error_details=None):
        self.id = id
        self.status = status
        self.error_details = error_details

class EmailNotifier:
    def send_task_completion_email(self, user_email, task):
        pass

    def send_task_failure_email(self, user_email, task, suggested_actions):
        pass

# Fixtures for setup and teardown
@pytest.fixture
def email_notifier():
    # Setup: Create a fresh EmailNotifier instance before each test
    notifier = EmailNotifier()
    yield notifier
    # Teardown: Any cleanup if needed (none in this stub)

@pytest.fixture
def sample_user_email():
    return "user@example.com"

@pytest.fixture
def completed_task():
    return Task(id=1, status="completed")

@pytest.fixture
def failed_task():
    return Task(id=2, status="failed", error_details="Database timeout")

@pytest.fixture
def suggested_actions():
    return "Please retry after checking the database connection."

# Test Cases

def test_send_email_on_task_completion(email_notifier, sample_user_email, completed_task):
    """Test that an email is sent when a task is completed."""
    with patch.object(email_notifier, 'send_task_completion_email', return_value=True) as mock_send:
        result = email_notifier.send_task_completion_email(sample_user_email, completed_task)
        mock_send.assert_called_once_with(sample_user_email, completed_task)
        assert result is True

def test_send_email_on_task_failure(email_notifier, sample_user_email, failed_task, suggested_actions):
    """
    Test that an email is sent when a task fails, 
    and the email includes error details and suggested actions.
    """
    with patch.object(email_notifier, 'send_task_failure_email', return_value=True) as mock_send:
        result = email_notifier.send_task_failure_email(sample_user_email, failed_task, suggested_actions)
        mock_send.assert_called_once_with(sample_user_email, failed_task, suggested_actions)
        assert result is True

def test_failure_email_includes_error_details_and_suggestions(email_notifier, sample_user_email, failed_task, suggested_actions):
    """Test that failure alert email contains error details and suggested actions."""
    with patch.object(email_notifier, 'send_task_failure_email') as mock_send:
        email_notifier.send_task_failure_email(sample_user_email, failed_task, suggested_actions)
        args, kwargs = mock_send.call_args
        sent_task = args[1]
        sent_suggestions = args[2]
        assert failed_task.error_details in str(sent_task.error_details)
        assert suggested_actions in sent_suggestions

def test_no_email_sent_for_unrelated_task_status(email_notifier, sample_user_email):
    """Test that no email is sent if task status is not completion or failure."""
    unrelated_task = Task(id=3, status="in_progress")
    with patch.object(email_notifier, 'send_task_completion_email') as mock_complete, \
         patch.object(email_notifier, 'send_task_failure_email') as mock_failure:
        # Simulate logic that only sends emails for completed/failed
        # Here, no email should be sent for "in_progress"
        # (You may need to adapt this to your actual business logic)
        assert not mock_complete.called
        assert not mock_failure.called

def test_send_email_handles_invalid_email_address(email_notifier, completed_task):
    """Test handling of invalid email addresses."""
    invalid_email = "invalid-email"
    with patch.object(email_notifier, 'send_task_completion_email', side_effect=ValueError("Invalid email address")):
        with pytest.raises(ValueError, match="Invalid email address"):
            email_notifier.send_task_completion_email(invalid_email, completed_task)

def test_send_email_handles_missing_task_details(email_notifier, sample_user_email):
    """Test that sending an email with missing task details raises an error."""
    with patch.object(email_notifier, 'send_task_completion_email', side_effect=TypeError("Task cannot be None")):
        with pytest.raises(TypeError, match="Task cannot be None"):
            email_notifier.send_task_completion_email(sample_user_email, None)

def test_failure_email_with_empty_suggested_actions(email_notifier, sample_user_email, failed_task):
    """Test sending a failure email when suggested actions are not provided."""
    with patch.object(email_notifier, 'send_task_failure_email', return_value=True) as mock_send:
        result = email_notifier.send_task_failure_email(sample_user_email, failed_task, "")
        mock_send.assert_called_once_with(sample_user_email, failed_task, "")
        assert result is True

def test_multiple_notifications_for_bulk_tasks(email_notifier, sample_user_email):
    """Test email notifications are sent for multiple completed and failed tasks."""
    tasks = [
        Task(id=1, status="completed"),
        Task(id=2, status="failed", error_details="Timeout"),
        Task(id=3, status="completed"),
        Task(id=4, status="failed", error_details="Permission denied"),
    ]
    with patch.object(email_notifier, 'send_task_completion_email', return_value=True) as mock_complete, \
         patch.object(email_notifier, 'send_task_failure_email', return_value=True) as mock_failure:
        for task in tasks:
            if task.status == "completed":
                email_notifier.send_task_completion_email(sample_user_email, task)
            elif task.status == "failed":
                email_notifier.send_task_failure_email(sample_user_email, task, "Contact admin.")
        assert mock_complete.call_count == 2
        assert mock_failure.call_count == 2

# You may add more edge cases as your application evolves.
```

**Notes:**
- These tests use `unittest.mock.patch` to mock methods and avoid sending real emails.
- Fixtures provide test data and handle setup/teardown.
- Each test has a docstring explaining its purpose.
- Edge cases include invalid emails, missing task details, empty suggested actions, and bulk operations.

**Adapt the stubs and interface to match your actual implementation.** If you need the code adapted to a specific application structure, please provide details about your classes or frameworks.