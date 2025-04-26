Certainly! Below are comprehensive **pytest** test cases for the given user story, covering both main functionalities and edge cases for sending email notifications on task completion or failure. The code assumes the existence of a function `send_task_notification(task_id, status, error_details=None)` and uses fixtures for setup/teardown. You should replace the mock implementations with your actual logic as needed.

```python
import pytest

# Mock email outbox to capture sent emails for assertions
class EmailOutbox:
    def __init__(self):
        self.emails = []

    def send_email(self, to, subject, body):
        self.emails.append({"to": to, "subject": subject, "body": body})

    def clear(self):
        self.emails.clear()

    def get_last_email(self):
        return self.emails[-1] if self.emails else None

# Fixture to provide a fresh outbox for each test
@pytest.fixture
def email_outbox():
    outbox = EmailOutbox()
    yield outbox
    outbox.clear()

# Mock send_task_notification function (replace with real implementation)
def send_task_notification(task_id, status, error_details=None, email_outbox=None):
    to = "ops-team@example.com"
    if status == "completed":
        subject = f"Task {task_id} Completed"
        body = f"The dormant account review task {task_id} has been completed successfully."
        email_outbox.send_email(to, subject, body)
    elif status == "failed":
        subject = f"Task {task_id} Failed"
        body = f"The dormant account review task {task_id} has failed.\n"
        if error_details:
            body += f"Error: {error_details['error']}\nSuggested Action: {error_details.get('suggested_action', 'None')}"
        else:
            body += "No error details provided."
        email_outbox.send_email(to, subject, body)
    # No-op for other statuses

# ---------------------- Test Cases ----------------------

def test_email_sent_on_task_completion(email_outbox):
    """
    Test that an email notification is sent when a task is completed successfully.
    """
    send_task_notification(task_id=101, status="completed", email_outbox=email_outbox)
    assert len(email_outbox.emails) == 1
    last_email = email_outbox.get_last_email()
    assert last_email['subject'] == "Task 101 Completed"
    assert "completed successfully" in last_email['body']

def test_email_sent_on_task_failure_with_error_details(email_outbox):
    """
    Test that an email notification is sent when a task fails, 
    and that it includes error details and suggested actions.
    """
    error_details = {"error": "Database connection lost", "suggested_action": "Check DB server"}
    send_task_notification(task_id=102, status="failed", error_details=error_details, email_outbox=email_outbox)
    assert len(email_outbox.emails) == 1
    last_email = email_outbox.get_last_email()
    assert last_email['subject'] == "Task 102 Failed"
    assert "failed" in last_email['body']
    assert "Database connection lost" in last_email['body']
    assert "Check DB server" in last_email['body']

def test_email_sent_on_task_failure_without_error_details(email_outbox):
    """
    Edge Case: Email is still sent on failure even if error details are missing,
    and a sensible message is included.
    """
    send_task_notification(task_id=103, status="failed", email_outbox=email_outbox)
    assert len(email_outbox.emails) == 1
    last_email = email_outbox.get_last_email()
    assert last_email['subject'] == "Task 103 Failed"
    assert "No error details provided" in last_email['body']

def test_no_email_sent_for_unrelated_status(email_outbox):
    """
    Edge Case: No email should be sent for statuses other than 'completed' or 'failed'.
    """
    send_task_notification(task_id=104, status="in_progress", email_outbox=email_outbox)
    assert len(email_outbox.emails) == 0

def test_multiple_notifications(email_outbox):
    """
    Test that multiple notifications can be sent in sequence without interference.
    """
    send_task_notification(task_id=105, status="completed", email_outbox=email_outbox)
    send_task_notification(task_id=106, status="failed", error_details={"error": "Timeout"}, email_outbox=email_outbox)
    assert len(email_outbox.emails) == 2
    assert email_outbox.emails[0]['subject'] == "Task 105 Completed"
    assert email_outbox.emails[1]['subject'] == "Task 106 Failed"

def test_email_contains_task_id(email_outbox):
    """
    Test that the task ID is included in both the subject and body of the email.
    """
    send_task_notification(task_id=107, status="completed", email_outbox=email_outbox)
    last_email = email_outbox.get_last_email()
    assert "107" in last_email['subject']
    assert "107" in last_email['body']

def test_email_sent_to_correct_recipient(email_outbox):
    """
    Test that emails are sent to the designated operations team recipient.
    """
    send_task_notification(task_id=108, status="completed", email_outbox=email_outbox)
    last_email = email_outbox.get_last_email()
    assert last_email['to'] == "ops-team@example.com"

# ---------------------- End of Test Cases ----------------------
```

**Notes:**
- The above code covers notifications for both task completion and failure (with and without error details), as well as various edge cases.
- Each test is isolated and uses a fresh `email_outbox`.
- Add/adjust imports and mock logic as per your actual project structure.
- Replace the mock `send_task_notification` function with your actual implementation when integrating these tests.