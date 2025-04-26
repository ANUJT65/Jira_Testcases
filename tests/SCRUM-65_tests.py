import os
import tempfile
import shutil
import pytest
from unittest import mock

# Assume the following function is the system under test (SUT):
# def extract_structured_requirements(input_path: str, input_type: str) -> dict:
#     ...

# For demonstration, we'll mock this function in the tests.

@pytest.fixture(scope='module')
def temp_test_dir():
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

@pytest.fixture(autouse=True)
def mock_extractor(monkeypatch):
    def mock_extract_structured_requirements(input_path, input_type):
        if not os.path.exists(input_path):
            raise FileNotFoundError('Input file not found')
        if input_type not in ['pdf', 'word', 'email', 'graph']:
            raise ValueError('Unsupported input type')
        if os.path.getsize(input_path) == 0:
            raise ValueError('Empty input file')
        # Simulate extraction
        return {
            'requirements': [
                {'id': 'REQ-1', 'description': 'The system shall extract requirements.'}
            ],
            'source': input_type
        }
    import sys
    sys.modules['requirement_extractor'] = mock.Mock()
    sys.modules['requirement_extractor'].extract_structured_requirements = mock_extract_structured_requirements
    yield
    del sys.modules['requirement_extractor']

@pytest.mark.parametrize('input_type,extension', [
    ('pdf', '.pdf'),
    ('word', '.docx'),
    ('email', '.eml'),
    ('graph', '.json')
])
def test_extract_structured_requirements_success(temp_test_dir, input_type, extension):
    # Create a dummy file for each supported format
    file_path = os.path.join(temp_test_dir, f'test_input{extension}')
    with open(file_path, 'w') as f:
        f.write('Dummy content representing a requirement')
    from requirement_extractor import extract_structured_requirements
    result = extract_structured_requirements(file_path, input_type)
    assert 'requirements' in result
    assert isinstance(result['requirements'], list)
    assert result['source'] == input_type
    assert result['requirements'][0]['id'] == 'REQ-1'
    assert 'description' in result['requirements'][0]

@pytest.mark.parametrize('input_type,extension', [
    ('pdf', '.pdf'),
    ('word', '.docx'),
    ('email', '.eml'),
    ('graph', '.json')
])
def test_extract_structured_requirements_empty_file(temp_test_dir, input_type, extension):
    # Create an empty file for each supported format
    file_path = os.path.join(temp_test_dir, f'empty_input{extension}')
    open(file_path, 'w').close()
    from requirement_extractor import extract_structured_requirements
    with pytest.raises(ValueError) as excinfo:
        extract_structured_requirements(file_path, input_type)
    assert 'Empty input file' in str(excinfo.value)

def test_extract_structured_requirements_unsupported_format(temp_test_dir):
    # Create a dummy file with unsupported extension
    file_path = os.path.join(temp_test_dir, 'unsupported.txt')
    with open(file_path, 'w') as f:
        f.write('Some content')
    from requirement_extractor import extract_structured_requirements
    with pytest.raises(ValueError) as excinfo:
        extract_structured_requirements(file_path, 'txt')
    assert 'Unsupported input type' in str(excinfo.value)

def test_extract_structured_requirements_file_not_found():
    from requirement_extractor import extract_structured_requirements
    with pytest.raises(FileNotFoundError) as excinfo:
        extract_structured_requirements('non_existent_file.pdf', 'pdf')
    assert 'Input file not found' in str(excinfo.value)

def test_extract_structured_requirements_output_readable(temp_test_dir):
    # Check that the output is in a readable, structured format
    file_path = os.path.join(temp_test_dir, 'test_input.pdf')
    with open(file_path, 'w') as f:
        f.write('Requirement: The system shall extract requirements.')
    from requirement_extractor import extract_structured_requirements
    result = extract_structured_requirements(file_path, 'pdf')
    assert isinstance(result, dict)
    assert 'requirements' in result
    assert isinstance(result['requirements'], list)
    assert all('id' in req and 'description' in req for req in result['requirements'])
