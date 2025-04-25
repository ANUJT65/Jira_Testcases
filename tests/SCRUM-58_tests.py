

class MockDocumentGenerator:
    def __init__(self, templates):
        self.templates = templates
        self.generated_docs = {}

    def generate_document(self, doc_type, data):
        if doc_type not in self.templates:
            raise ValueError('Unsupported document type')
        if not isinstance(data, dict) or not data:
            raise ValueError('Invalid data for document generation')
        template = self.templates[doc_type]
        content = template.format(**data)
        self.generated_docs[doc_type] = content
        return content

    def generate_jira_user_stories(self, stories_data):
        if not isinstance(stories_data, list) or not stories_data:
            raise ValueError('Invalid stories data')
        formatted_stories = []
        for story in stories_data:
            if not all(k in story for k in ('title', 'description', 'acceptance_criteria')):
                raise ValueError('Incomplete user story data')
            formatted = f"Summary: {story['title']}\nDescription: {story['description']}\nAcceptance Criteria: {story['acceptance_criteria']}"
            formatted_stories.append(formatted)
        return formatted_stories

@pytest.fixture(scope='function')
def doc_generator():
    templates = {
        'SRS': 'SRS Document\nTitle: {title}\nContent: {content}',
        'BRD': 'BRD Document\nTitle: {title}\nContent: {content}'
    }
    generator = MockDocumentGenerator(templates)
    yield generator
    generator.generated_docs.clear()

def test_generate_srs_document_success(doc_generator):
    data = {'title': 'Login Feature', 'content': 'The system shall allow users to log in.'}
    content = doc_generator.generate_document('SRS', data)
    assert content.startswith('SRS Document')
    assert 'Login Feature' in content
    assert 'The system shall allow users to log in.' in content

def test_generate_brd_document_success(doc_generator):
    data = {'title': 'User Registration', 'content': 'Users must be able to register accounts.'}
    content = doc_generator.generate_document('BRD', data)
    assert content.startswith('BRD Document')
    assert 'User Registration' in content
    assert 'Users must be able to register accounts.' in content

def test_generate_document_invalid_type(doc_generator):
    data = {'title': 'Invalid', 'content': 'Test'}
    with pytest.raises(ValueError) as exc:
        doc_generator.generate_document('PRD', data)
    assert 'Unsupported document type' in str(exc.value)

def test_generate_document_invalid_data(doc_generator):
    with pytest.raises(ValueError) as exc:
        doc_generator.generate_document('SRS', None)
    assert 'Invalid data for document generation' in str(exc.value)

    with pytest.raises(ValueError) as exc2:
        doc_generator.generate_document('SRS', {})
    assert 'Invalid data for document generation' in str(exc2.value)

def test_generate_jira_user_stories_success(doc_generator):
    stories_data = [
        {
            'title': 'User can reset password',
            'description': 'As a user, I want to reset my password so that I can regain access.',
            'acceptance_criteria': 'Given a registered user, when they request a reset, then an email is sent.'
        }
    ]
    formatted = doc_generator.generate_jira_user_stories(stories_data)
    assert isinstance(formatted, list)
    assert formatted[0].startswith('Summary: User can reset password')
    assert 'Description: As a user, I want to reset my password' in formatted[0]
    assert 'Acceptance Criteria: Given a registered user' in formatted[0]

def test_generate_jira_user_stories_invalid_data(doc_generator):
    with pytest.raises(ValueError) as exc:
        doc_generator.generate_jira_user_stories(None)
    assert 'Invalid stories data' in str(exc.value)

    with pytest.raises(ValueError) as exc2:
        doc_generator.generate_jira_user_stories([])
    assert 'Invalid stories data' in str(exc2.value)

def test_generate_jira_user_stories_incomplete_story(doc_generator):
    incomplete_data = [
        {
            'title': 'Missing fields',
            'description': 'No acceptance criteria.'
        }
    ]
    with pytest.raises(ValueError) as exc:
        doc_generator.generate_jira_user_stories(incomplete_data)
    assert 'Incomplete user story data' in str(exc.value)
