import pytest

class MockRAGEngine:
    def __init__(self, knowledge_base):
        self.knowledge_base = knowledge_base
    def fill_missing_data(self, requirement):
        if not isinstance(requirement, dict):
            raise ValueError('Requirement must be a dictionary')
        filled = requirement.copy()
        for key, value in requirement.items():
            if value is None:
                if key in self.knowledge_base:
                    filled[key] = self.knowledge_base[key]
                else:
                    filled[key] = None
        return filled

@pytest.fixture(scope='function')
def knowledge_base():
    return {
        'title': 'User login functionality',
        'description': 'The system shall allow users to log in using email and password.',
        'priority': 'High',
        'source': 'srs'
    }

@pytest.fixture(scope='function')
def rag_engine(knowledge_base):
    return MockRAGEngine(knowledge_base)

@pytest.fixture(autouse=True)
def setup_and_teardown():
    yield

def test_rag_fills_single_missing_field(rag_engine):
    requirement = {
        'title': None,
        'description': 'The system shall allow users to log in using email and password.',
        'priority': 'High',
        'source': 'srs'
    }
    filled = rag_engine.fill_missing_data(requirement)
    assert filled['title'] == 'User login functionality'
    assert filled['description'] == requirement['description']
    assert filled['priority'] == requirement['priority']
    assert filled['source'] == requirement['source']

def test_rag_fills_multiple_missing_fields(rag_engine):
    requirement = {
        'title': None,
        'description': None,
        'priority': None,
        'source': 'srs'
    }
    filled = rag_engine.fill_missing_data(requirement)
    assert filled['title'] == 'User login functionality'
    assert filled['description'] == 'The system shall allow users to log in using email and password.'
    assert filled['priority'] == 'High'
    assert filled['source'] == 'srs'

def test_rag_handles_no_missing_fields(rag_engine):
    requirement = {
        'title': 'User login functionality',
        'description': 'The system shall allow users to log in using email and password.',
        'priority': 'High',
        'source': 'srs'
    }
    filled = rag_engine.fill_missing_data(requirement)
    assert filled == requirement

def test_rag_handles_unavailable_data(rag_engine):
    requirement = {
        'title': None,
        'description': None,
        'priority': None,
        'source': None,
        'unknown_field': None
    }
    filled = rag_engine.fill_missing_data(requirement)
    assert filled['title'] == 'User login functionality'
    assert filled['description'] == 'The system shall allow users to log in using email and password.'
    assert filled['priority'] == 'High'
    assert filled['source'] == 'srs'
    assert filled['unknown_field'] is None

def test_rag_raises_error_on_invalid_input(rag_engine):
    with pytest.raises(ValueError):
        rag_engine.fill_missing_data(['not', 'a', 'dict'])

def test_rag_partial_fill_when_partial_knowledge(rag_engine):
    partial_engine = MockRAGEngine({'title': 'User login functionality'})
    requirement = {
        'title': None,
        'description': None,
        'priority': None,
        'source': None
    }
    filled = partial_engine.fill_missing_data(requirement)
    assert filled['title'] == 'User login functionality'
    assert filled['description'] is None
    assert filled['priority'] is None
    assert filled['source'] is None
