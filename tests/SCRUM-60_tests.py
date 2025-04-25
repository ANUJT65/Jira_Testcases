import os
import shutil
import tempfile
import pytest
from unittest.mock import patch
from requirement_extractor import extract_requirements

def create_temp_file(suffix, content):
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'wb') as tmp:
        tmp.write(content)
    return path

@pytest.fixture(scope='function')
def temp_pdf_file():
    content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'  # Minimal PDF header
    path = create_temp_file('.pdf', content)
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def temp_docx_file():
    content = b'PK\x03\x04'  # Minimal DOCX header
    path = create_temp_file('.docx', content)
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def temp_xlsx_file():
    content = b'PK\x03\x04'  # Minimal XLSX header
    path = create_temp_file('.xlsx', content)
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def temp_image_file():
    content = b'\x89PNG\r\n\x1a\n'  # Minimal PNG header
    path = create_temp_file('.png', content)
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def temp_txt_file():
    content = b'This is a plain text file.'
    path = create_temp_file('.txt', content)
    yield path
    os.remove(path)

@pytest.fixture(scope='function')
def invalid_file():
    content = b''
    path = create_temp_file('.pdf', content)
    yield path
    os.remove(path)

def test_extract_requirements_from_pdf(temp_pdf_file):
    with patch('requirement_extractor._extract_from_pdf') as mock_pdf:
        mock_pdf.return_value = [{"requirement": "System shall support PDF extraction."}]
        result = extract_requirements(temp_pdf_file)
        assert isinstance(result, list)
        assert any('requirement' in r for r in result)

def test_extract_requirements_from_docx(temp_docx_file):
    with patch('requirement_extractor._extract_from_docx') as mock_docx:
        mock_docx.return_value = [{"requirement": "System shall support DOCX extraction."}]
        result = extract_requirements(temp_docx_file)
        assert isinstance(result, list)
        assert any('requirement' in r for r in result)

def test_extract_requirements_from_xlsx(temp_xlsx_file):
    with patch('requirement_extractor._extract_from_xlsx') as mock_xlsx:
        mock_xlsx.return_value = [{"requirement": "System shall support XLSX extraction."}]
        result = extract_requirements(temp_xlsx_file)
        assert isinstance(result, list)
        assert any('requirement' in r for r in result)

def test_extract_requirements_from_image(temp_image_file):
    with patch('requirement_extractor._extract_from_image') as mock_img:
        mock_img.return_value = [{"requirement": "System shall support image extraction."}]
        result = extract_requirements(temp_image_file)
        assert isinstance(result, list)
        assert any('requirement' in r for r in result)

def test_extract_requirements_from_unsupported_format(temp_txt_file):
    with pytest.raises(ValueError):
        extract_requirements(temp_txt_file)

def test_extract_requirements_from_corrupted_pdf(invalid_file):
    with pytest.raises(Exception):
        extract_requirements(invalid_file)

def test_extract_requirements_with_empty_path():
    with pytest.raises(FileNotFoundError):
        extract_requirements('')

def test_extract_requirements_with_nonexistent_file():
    with pytest.raises(FileNotFoundError):
        extract_requirements('/nonexistent/path/to/file.pdf')

def test_extract_requirements_returns_structured_output(temp_pdf_file):
    with patch('requirement_extractor._extract_from_pdf') as mock_pdf:
        mock_pdf.return_value = [
            {"requirement": "System shall extract requirements.", "priority": "High", "source": "srs"}
        ]
        result = extract_requirements(temp_pdf_file)
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)
        assert all('requirement' in r for r in result)
        assert all('priority' in r for r in result)
        assert all('source' in r for r in result)
