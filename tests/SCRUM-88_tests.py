```python
import pytest

# --- Fixtures for Setup and Teardown ---

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """
    Setup and teardown for test cases.
    This may include:
    - Creating a test user with 'Compliance Officer' role.
    - Clearing any previous notifications.
    - Mocking the email sending service.
    - Resetting the review task queue.
    """
    # Setup code here
    create_test_compliance_officer_user()
    clear_notifications_for_user('compliance_officer')
    mock_email_service.start()
    reset_review_tasks()

    yield

    # Teardown code here
    delete_test_compliance_officer_user()
    clear_notifications_for_user('compliance_officer')
    mock_email_service.stop()
    reset_review_tasks()

# --- Helper Functions (to be implemented in your environment) ---

def create_review_task_for_user(user_id, task_data):
    """Simulate creation of a review task assigned to user."""
    pass

def get_email_notifications(user_id):
    """Return list of email notifications sent to user."""
    return mock_email_service.get_sent_emails(user_id)

def get_ui_notifications(user_id):
    """Return list of in-app UI notifications for user."""
    return get_notifications_from_ui(user_id)

def create_test_compliance_officer_user():
    """Creates a test compliance officer user."""
    pass

def delete_test_compliance_officer_user():
    """Deletes the test compliance officer user."""
    pass

def clear_notifications_for_user(user_id):
    """Clears all notifications for the given user."""
    pass

def reset_review_tasks():
    """Resets the review task queue."""
    pass

# Mock email service for testing
class mock_email_service:
    sent_emails = {}

    @classmethod
    def start(cls):
        cls.sent_emails = {}

    @classmethod
    def stop(cls):
        cls.sent_emails = {}

    @classmethod
    def send_email(cls, user_id, subject, body):
        cls.sent_emails.setdefault(user_id, []).append({'subject': subject, 'body': body})

    @classmethod
    def get_sent_emails(cls, user_id):
        return cls.sent_emails.get(user_id, [])

# --- Test Cases ---

def test_email_notification_sent_on_new_review_task():
    """
    Verify that an email notification is sent to the Compliance Officer
    when a new review task is created.
    """
    user_id = 'compliance_officer'
    task_data = {'title': 'Review ABC', 'details': 'Check compliance for ABC'}
    create_review_task_for_user(user_id, task_data)

    emails = get_email_notifications(user_id)
    assert len(emails) == 1, "Email notification should be sent for a new review task."
    assert 'Review ABC' in emails[0]['subject'], "Email subject should contain task title."

def test_ui_notification_present_on_new_review_task():
    """
    Verify that a UI notification is present for the Compliance Officer
    when a new review task is created.
    """
    user_id = 'compliance_officer'
    task_data = {'title': 'Review XYZ', 'details': 'Check compliance for XYZ'}
    create_review_task_for_user(user_id, task_data)

    ui_notifications = get_ui_notifications(user_id)
    assert any('Review XYZ' in n['message'] for n in ui_notifications), \
        "UI notification should be present for the created review task."

def test_no_duplicate_notifications_for_same_task():
    """
    Ensure that duplicate notifications are not sent if the same review task is re-created or re-assigned.
    """
    user_id = 'compliance_officer'
    task_data = {'title': 'Review DEF', 'details': 'Check compliance for DEF'}
    create_review_task_for_user(user_id, task_data)
    create_review_task_for_user(user_id, task_data)  # Attempt duplicate

    emails = get_email_notifications(user_id)
    # Assuming system is designed to avoid duplicates
    assert len(emails) == 1, "Duplicate notifications should not be sent for the same task."

def test_multiple_review_tasks_generate_multiple_notifications():
    """
    Test that multiple new review tasks generate separate notifications (both email and UI).
    """
    user_id = 'compliance_officer'
    task_titles = ['Review GHI', 'Review JKL', 'Review MNO']
    for title in task_titles:
        create_review_task_for_user(user_id, {'title': title, 'details': f'Check compliance for {title}'})

    emails = get_email_notifications(user_id)
    ui_notifications = get_ui_notifications(user_id)

    assert len(emails) == 3, "Each task should trigger a separate email notification."
    assert all(any(title in email['subject'] for email in emails) for title in task_titles), \
        "Each task title should appear in email notifications."

    assert all(any(title in n['message'] for n in ui_notifications) for title in task_titles), \
        "Each task title should appear in UI notifications."

def test_notification_not_sent_to_non_compliance_officer():
    """
    Ensure that users without the Compliance Officer role do not receive notifications for review tasks.
    """
    user_id = 'regular_user'
    create_test_compliance_officer_user()  # Ensure compliance officer exists
    task_data = {'title': 'Review PQR', 'details': 'Check compliance for PQR'}
    create_review_task_for_user(user_id, task_data)

    emails = get_email_notifications(user_id)
    ui_notifications = get_ui_notifications(user_id)
    assert len(emails) == 0, "Non-compliance officer should not receive email notifications."
    assert len(ui_notifications) == 0, "Non-compliance officer should not receive UI notifications."

def test_missing_email_address_edge_case():
    """
    Edge Case: If the compliance officer does not have an email address, ensure system handles gracefully.
    """
    user_id = 'compliance_officer'
    remove_email_address_for_user(user_id)
    task_data = {'title': 'Review STU', 'details': 'Check compliance for STU'}
    create_review_task_for_user(user_id, task_data)

    emails = get_email_notifications(user_id)
    ui_notifications = get_ui_notifications(user_id)
    assert len(emails) == 0, "No email notification should be sent if email is missing."
    assert any('Review STU' in n['message'] for n in ui_notifications), \
        "UI notification should still be present."

    restore_email_address_for_user(user_id)

# --- Additional Helper Functions for Edge Cases ---

def remove_email_address_for_user(user_id):
    """Simulate removal of email address for a user."""
    pass

def restore_email_address_for_user(user_id):
    """Restore email address for a user."""
    pass
```

---

**Notes:**

- Each test case includes a docstring describing its purpose.
- The fixture handles setup/teardown common to all tests.
- Helper functions should be implemented according to your application’s environment or mocked as needed.
- Edge cases include missing email address and role restrictions.
- All assertions have clear error messages for easier debugging.
- `mock_email_service` is a simple in-memory mock for illustration; replace or extend as needed for your real testing environment.