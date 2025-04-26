Certainly! Below is a comprehensive set of pytest test cases for the given user story. The test suite is designed to cover both main functionalities (notifications for task completion and failures) as well as relevant edge cases. Setup and teardown procedures are included, with clear comments for each test case.

Assumptions:

- There exists a function send_task_notification(task_status, user_email, details=None) that sends the email.
- The email sending is mocked for testability.
- The mock_email_service is used to capture sent emails for assertions.

```python
import pytest

# Mock email service to capture sent emails
class MockEmailService:
    def __init__(self):
        self.sent_emails = []

    def send_email(self, to, subject, body):
        self.sent_emails.append({'to': to, 'subject': subject, 'body': body})

    def reset(self):
        self.sent_emails = []

# System under test (to be replaced with actual implementation)
def send_task_notification(task_status, user_email, details=None, email_service=None):
    """
    Simulated function to send notifications.
    - task_status: 'completed' or 'failed'
    - details: dict with keys 'error' and 'suggested_action' when task_status is 'failed'
    """
    if not user_email:
        raise ValueError("User email must be provided.")
    if task_status == 'completed':
        email_service.send_email(
            to=user_email,
            subject="Dormant Account Review Task Completed",
            body="Your dormant account review task has been completed successfully."
        )
    elif task_status == 'failed':
        if not details or 'error' not in details or 'suggested_action' not in details:
            raise ValueError("Failure details must include 'error' and 'suggested_action'.")
        body = (
            f"The dormant account review task has failed.\n"
            f"Error: {details['error']}\n"
            f"Suggested action: {details['suggested_action']}"
        )
        email_service.send_email(
            to=user_email,
            subject="Dormant Account Review Task Failed",
            body=body
        )
    else:
        raise ValueError("Invalid task status.")

@pytest.fixture
def email_service():
    # Setup: create a fresh mock email service before each test
    service = MockEmailService()
    yield service
    # Teardown: reset the mock email service after each test
    service.reset()

def test_email_sent_on_task_completion(email_service):
    """
    Test that an email is sent when a task completes successfully.
    """
    user_email = "user@example.com"
    send_task_notification("completed", user_email, email_service=email_service)
    assert len(email_service.sent_emails) == 1
    email = email_service.sent_emails[0]
    assert email['to'] == user_email
    assert "Completed" in email['subject']
    assert "completed successfully" in email['body']

def test_email_sent_on_task_failure_with_details(email_service):
    """
    Test that an email is sent with error details and suggested actions when a task fails.
    """
    user_email = "user@example.com"
    error_details = {
        'error': 'Database timeout',
        'suggested_action': 'Please retry the task or contact IT support.'
    }
    send_task_notification("failed", user_email, details=error_details, email_service=email_service)
    assert len(email_service.sent_emails) == 1
    email = email_service.sent_emails[0]
    assert email['to'] == user_email
    assert "Failed" in email['subject']
    assert "Database timeout" in email['body']
    assert "Please retry the task" in email['body']

def test_no_email_sent_for_invalid_status(email_service):
    """
    Test that no email is sent and an exception is raised for an invalid task status.
    """
    user_email = "user@example.com"
    with pytest.raises(ValueError, match="Invalid task status."):
        send_task_notification("unknown_status", user_email, email_service=email_service)
    assert len(email_service.sent_emails) == 0

def test_failure_alert_missing_error_detail(email_service):
    """
    Test the edge case where failure alert is missing error detail.
    """
    user_email = "user@example.com"
    incomplete_details = {
        'suggested_action': 'Restart the process.'
    }
    with pytest.raises(ValueError, match="Failure details must include 'error' and 'suggested_action'."):
        send_task_notification("failed", user_email, details=incomplete_details, email_service=email_service)
    assert len(email_service.sent_emails) == 0

def test_failure_alert_missing_suggested_action(email_service):
    """
    Test the edge case where failure alert is missing suggested action.
    """
    user_email = "user@example.com"
    incomplete_details = {
        'error': 'Unexpected exception'
    }
    with pytest.raises(ValueError, match="Failure details must include 'error' and 'suggested_action'."):
        send_task_notification("failed", user_email, details=incomplete_details, email_service=email_service)
    assert len(email_service.sent_emails) == 0

def test_no_email_sent_when_user_email_missing(email_service):
    """
    Test that no email is sent and an exception is raised when user_email is missing.
    """
    with pytest.raises(ValueError, match="User email must be provided."):
        send_task_notification("completed", "", email_service=email_service)
    assert len(email_service.sent_emails) == 0

def test_multiple_notifications(email_service):
    """
    Test sending multiple notifications in sequence.
    """
    user_email = "user@example.com"
    send_task_notification("completed", user_email, email_service=email_service)
    error_details = {
        'error': 'API rate limit exceeded',
        'suggested_action': 'Wait 5 minutes before retrying.'
    }
    send_task_notification("failed", user_email, details=error_details, email_service=email_service)
    assert len(email_service.sent_emails) == 2
    assert email_service.sent_emails[0]['subject'].startswith("Dormant Account Review Task Completed")
    assert email_service.sent_emails[1]['subject'].startswith("Dormant Account Review Task Failed")

# Additional edge case: unusual but valid user email
def test_email_sent_with_unusual_email_address(email_service):
    """
    Test that notification works with a valid, but unusual, email address.
    """
    user_email = "user+alias@sub.domain-example.co.uk"
    send_task_notification("completed", user_email, email_service=email_service)
    assert len(email_service.sent_emails) == 1
    assert email_service.sent_emails[0]['to'] == user_email
```

**How to Use:**
- Place this code in your test file (e.g., `test_notifications.py`).
- Replace the `send_task_notification` function with your actual implementation.
- Adjust the mock email service as needed to match your production email sending abstraction.
- Run with `pytest`.

**What’s Covered:**
- Notification on successful completion.
- Notification on failure with required error and action details.
- Edge cases: missing details, invalid status, missing email, unusual email addresses.
- Multiple notifications in sequence.
- Clean setup/teardown for isolation.

Let me know if you need the code adapted for a different function signature or email sending abstraction!