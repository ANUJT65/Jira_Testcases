import pytest
from pathlib import Path

class MockDocumentGenerator:
    def __init__(self, templates):
        self.templates = templates
    def generate_document(self, doc_type, data):
        if doc_type not in self.templates:
            raise ValueError('Unsupported document type')
        if not isinstance(data, dict) or not data:
            raise ValueError('Invalid data for document generation')
        template = self.templates[doc_type]
        return template.format(**data)
    def generate_jira_user_story(self, user_story_data):
        required_fields = {'title', 'description', 'acceptance_criteria'}
        if not required_fields.issubset(user_story_data):
            raise ValueError('Missing required fields for JIRA user story')
        return f"Summary: {user_story_data['title']}\nDescription: {user_story_data['description']}\nAcceptance Criteria: {user_story_data['acceptance_criteria']}"

def setup_module(module):
    module.templates = {
        'SRS': 'SRS Title: {title}\nDetails: {details}',
        'BRD': 'BRD Title: {title}\nBusiness Need: {business_need}'
    }
    module.generator = MockDocumentGenerator(module.templates)

def teardown_module(module):
    del module.templates
    del module.generator

def test_generate_srs_document_valid():
    data = {'title': 'Login Feature', 'details': 'User can log in using email and password.'}
    doc = generator.generate_document('SRS', data)
    assert doc.startswith('SRS Title: Login Feature')
    assert 'User can log in' in doc

def test_generate_brd_document_valid():
    data = {'title': 'Payment Integration', 'business_need': 'Enable users to pay online.'}
    doc = generator.generate_document('BRD', data)
    assert doc.startswith('BRD Title: Payment Integration')
    assert 'Enable users to pay online.' in doc

def test_generate_document_invalid_type():
    data = {'title': 'Invalid', 'details': 'N/A'}
    with pytest.raises(ValueError) as exc:
        generator.generate_document('PRD', data)
    assert 'Unsupported document type' in str(exc.value)

def test_generate_document_invalid_data():
    with pytest.raises(ValueError) as exc:
        generator.generate_document('SRS', None)
    assert 'Invalid data for document generation' in str(exc.value)
    with pytest.raises(ValueError) as exc2:
        generator.generate_document('SRS', {})
    assert 'Invalid data for document generation' in str(exc2.value)

def test_generate_jira_user_story_valid():
    user_story_data = {
        'title': 'User Registration',
        'description': 'As a user, I want to register so I can access the system.',
        'acceptance_criteria': 'User can register with email and password.'
    }
    story = generator.generate_jira_user_story(user_story_data)
    assert story.startswith('Summary: User Registration')
    assert 'Description: As a user' in story
    assert 'Acceptance Criteria: User can register' in story

def test_generate_jira_user_story_missing_fields():
    incomplete_data = {
        'title': 'Incomplete',
        'description': 'Missing acceptance criteria.'
    }
    with pytest.raises(ValueError) as exc:
        generator.generate_jira_user_story(incomplete_data)
    assert 'Missing required fields for JIRA user story' in str(exc.value)
