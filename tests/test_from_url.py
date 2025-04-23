import pytest
from unittest.mock import MagicMock

class DocumentGenerator:
    def __init__(self, templates):
        self.templates = templates
    def generate(self, doc_type, data):
        if doc_type not in self.templates:
            raise ValueError('Unknown document type')
        if not data or not isinstance(data, dict):
            raise ValueError('Invalid data')
        return self.templates[doc_type].format(**data)
    def generate_jira_user_story(self, data):
        required_fields = ['title', 'description', 'acceptance_criteria']
        if not all(field in data for field in required_fields):
            raise ValueError('Missing required fields')
        return f"Summary: {data['title']}\nDescription: {data['description']}\nAcceptance Criteria: {data['acceptance_criteria']}"

@pytest.fixture(scope='function')
def templates():
    return {
        'SRS': 'SRS Document\nTitle: {title}\nDetails: {details}',
        'BRD': 'BRD Document\nBusiness Need: {business_need}\nScope: {scope}'
    }

@pytest.fixture(scope='function')
def generator(templates):
    return DocumentGenerator(templates)

def test_generate_srs_document_with_valid_data(generator):
    data = {'title': 'Login Feature', 'details': 'User can log in with email and password.'}
    result = generator.generate('SRS', data)
    assert result.startswith('SRS Document')
    assert 'Login Feature' in result
    assert 'User can log in with email and password.' in result

def test_generate_brd_document_with_valid_data(generator):
    data = {'business_need': 'Improve onboarding', 'scope': 'User registration and login'}
    result = generator.generate('BRD', data)
    assert result.startswith('BRD Document')
    assert 'Improve onboarding' in result
    assert 'User registration and login' in result

def test_generate_document_with_invalid_type(generator):
    data = {'title': 'Test', 'details': 'Test details'}
    with pytest.raises(ValueError) as exc:
        generator.generate('UNKNOWN', data)
    assert 'Unknown document type' in str(exc.value)

def test_generate_document_with_missing_data(generator):
    with pytest.raises(ValueError) as exc:
        generator.generate('SRS', None)
    assert 'Invalid data' in str(exc.value)

def test_generate_document_with_incomplete_data(generator):
    data = {'title': 'Incomplete'}
    with pytest.raises(KeyError):
        generator.generate('SRS', data)

def test_generate_jira_user_story_with_valid_data(generator):
    data = {
        'title': 'Enable password reset',
        'description': 'As a user, I want to reset my password.',
        'acceptance_criteria': 'User receives reset email.'
    }
    result = generator.generate_jira_user_story(data)
    assert result.startswith('Summary: Enable password reset')
    assert 'As a user, I want to reset my password.' in result
    assert 'User receives reset email.' in result

def test_generate_jira_user_story_with_missing_fields(generator):
    data = {
        'title': 'Enable password reset',
        'description': 'As a user, I want to reset my password.'
    }
    with pytest.raises(ValueError) as exc:
        generator.generate_jira_user_story(data)
    assert 'Missing required fields' in str(exc.value)

def test_generated_documents_follow_templates(generator, templates):
    data = {'title': 'Feature X', 'details': 'Details X'}
    srs = generator.generate('SRS', data)
    assert templates['SRS'].split('\n')[0] in srs
    data_brd = {'business_need': 'Need Y', 'scope': 'Scope Y'}
    brd = generator.generate('BRD', data_brd)
    assert templates['BRD'].split('\n')[0] in brd

def test_jira_user_story_format_for_integration(generator):
    data = {
        'title': 'User logout',
        'description': 'As a user, I want to log out.',
        'acceptance_criteria': 'Session ends and user is redirected.'
    }
    user_story = generator.generate_jira_user_story(data)
    assert user_story.startswith('Summary: User logout')
    assert '\nDescription: As a user, I want to log out.' in user_story
    assert '\nAcceptance Criteria: Session ends and user is redirected.' in user_story
