import os
import shutil
import tempfile
import pytest
from unittest.mock import patch
from requirement_extractor import extract_requirements

def create_temp_file(suffix, content=b''):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'wb') as tmp:
        tmp.write(content)
    return path

@pytest.fixture(scope='function')
def temp_files():
    files = {}
    pdf_content = b'%PDF-1.4 example pdf content'
    docx_content = b'PK\x03\x04 example docx content'
    xlsx_content = b'PK\x03\x04 example xlsx content'
    image_content = b'\x89PNG\r\n\x1a\n example image content'
    files['pdf'] = create_temp_file('.pdf', pdf_content)
    files['docx'] = create_temp_file('.docx', docx_content)
    files['xlsx'] = create_temp_file('.xlsx', xlsx_content)
    files['image'] = create_temp_file('.png', image_content)
    yield files
    for f in files.values():
        os.remove(f)

@pytest.fixture(scope='function')
def invalid_file():
    path = create_temp_file('.txt', b'Just a plain text file')
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def corrupted_pdf():
    path = create_temp_file('.pdf', b'not a real pdf')
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def empty_file():
    path = create_temp_file('.pdf', b'')
    yield path
    os.remove(path)

def test_extract_requirements_from_pdf(temp_files):
    result = extract_requirements(temp_files['pdf'])
    assert isinstance(result, dict)
    assert 'requirements' in result
    assert isinstance(result['requirements'], list)

def test_extract_requirements_from_docx(temp_files):
    result = extract_requirements(temp_files['docx'])
    assert isinstance(result, dict)
    assert 'requirements' in result
    assert isinstance(result['requirements'], list)

def test_extract_requirements_from_xlsx(temp_files):
    result = extract_requirements(temp_files['xlsx'])
    assert isinstance(result, dict)
    assert 'requirements' in result
    assert isinstance(result['requirements'], list)

def test_extract_requirements_from_image(temp_files):
    result = extract_requirements(temp_files['image'])
    assert isinstance(result, dict)
    assert 'requirements' in result
    assert isinstance(result['requirements'], list)

def test_extract_requirements_from_unsupported_format(invalid_file):
    with pytest.raises(ValueError):
        extract_requirements(invalid_file)

def test_extract_requirements_from_corrupted_pdf(corrupted_pdf):
    with pytest.raises(Exception):
        extract_requirements(corrupted_pdf)

def test_extract_requirements_from_empty_file(empty_file):
    with pytest.raises(ValueError):
        extract_requirements(empty_file)

def test_extract_requirements_with_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extract_requirements('nonexistentfile.pdf')

def test_extract_requirements_with_mocked_ai_model(temp_files):
    with patch('requirement_extractor.call_generative_ai') as mock_ai:
        mock_ai.return_value = {'requirements': ['Req1', 'Req2']}
        result = extract_requirements(temp_files['pdf'])
        assert result['requirements'] == ['Req1', 'Req2']

def test_extract_requirements_with_large_file(temp_files):
    large_content = b'A' * (10 * 1024 * 1024)
    path = create_temp_file('.pdf', large_content)
    try:
        result = extract_requirements(path)
        assert isinstance(result, dict)
        assert 'requirements' in result
    finally:
        os.remove(path)
