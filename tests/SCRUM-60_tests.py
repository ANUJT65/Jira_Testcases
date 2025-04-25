import os
import shutil
import tempfile
import pytest
from unittest.mock import patch, MagicMock

from requirement_extractor import RequirementExtractor, ExtractionError

def create_temp_file(suffix, content=None):
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, f"input{suffix}")
    mode = 'wb' if isinstance(content, bytes) else 'w'
    with open(file_path, mode) as f:
        if content:
            f.write(content)
    return file_path, temp_dir

@pytest.fixture(scope="function")
def extractor():
    extractor = RequirementExtractor()
    yield extractor

@pytest.fixture(scope="function")
def cleanup_temp_dirs():
    dirs = []
    yield dirs
    for d in dirs:
        shutil.rmtree(d, ignore_errors=True)

def test_extract_requirements_from_pdf_positive(extractor, cleanup_temp_dirs):
    pdf_content = b'%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n'  # minimal PDF
    file_path, temp_dir = create_temp_file('.pdf', pdf_content)
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_pdf', return_value=[{'id': 1, 'requirement': 'System shall extract requirements from PDF'}]):
        result = extractor.extract(file_path)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract requirements from PDF'

def test_extract_requirements_from_word_positive(extractor, cleanup_temp_dirs):
    docx_content = b'PK\x03\x04'  # minimal DOCX header
    file_path, temp_dir = create_temp_file('.docx', docx_content)
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_word', return_value=[{'id': 2, 'requirement': 'System shall extract requirements from Word'}]):
        result = extractor.extract(file_path)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract requirements from Word'

def test_extract_requirements_from_excel_positive(extractor, cleanup_temp_dirs):
    xlsx_content = b'PK\x03\x04'  # minimal XLSX header
    file_path, temp_dir = create_temp_file('.xlsx', xlsx_content)
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_excel', return_value=[{'id': 3, 'requirement': 'System shall extract requirements from Excel'}]):
        result = extractor.extract(file_path)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract requirements from Excel'

def test_extract_requirements_from_image_positive(extractor, cleanup_temp_dirs):
    image_content = b'\x89PNG\r\n\x1a\n'  # minimal PNG header
    file_path, temp_dir = create_temp_file('.png', image_content)
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_image', return_value=[{'id': 4, 'requirement': 'System shall extract requirements from image'}]):
        result = extractor.extract(file_path)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract requirements from image'

def test_extract_requirements_from_unsupported_format_negative(extractor, cleanup_temp_dirs):
    file_path, temp_dir = create_temp_file('.txt', 'This is a plain text file.')
    cleanup_temp_dirs.append(temp_dir)
    with pytest.raises(ExtractionError):
        extractor.extract(file_path)

def test_extract_requirements_from_corrupted_pdf_negative(extractor, cleanup_temp_dirs):
    pdf_content = b'not a real pdf'
    file_path, temp_dir = create_temp_file('.pdf', pdf_content)
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_pdf', side_effect=ExtractionError('Corrupted PDF')):
        with pytest.raises(ExtractionError):
            extractor.extract(file_path)

def test_extract_requirements_from_empty_file_negative(extractor, cleanup_temp_dirs):
    file_path, temp_dir = create_temp_file('.pdf', b'')
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_pdf', side_effect=ExtractionError('Empty file')):
        with pytest.raises(ExtractionError):
            extractor.extract(file_path)

def test_extract_requirements_from_large_file_positive(extractor, cleanup_temp_dirs):
    pdf_content = b'%PDF-1.4\n' + b'0' * 1024 * 1024  # 1MB PDF-like content
    file_path, temp_dir = create_temp_file('.pdf', pdf_content)
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_pdf', return_value=[{'id': 5, 'requirement': 'System shall extract requirements from large PDF'}]):
        result = extractor.extract(file_path)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract requirements from large PDF'

def test_extract_requirements_from_email_html_positive(extractor, cleanup_temp_dirs):
    file_path, temp_dir = create_temp_file('.eml', 'Subject: Requirements\n\n<html><body>Requirement: System shall extract from email</body></html>')
    cleanup_temp_dirs.append(temp_dir)
    with patch.object(extractor, '_extract_from_email', return_value=[{'id': 6, 'requirement': 'System shall extract from email'}]):
        result = extractor.extract(file_path)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract from email'

def test_extract_requirements_from_web_data_positive(extractor):
    url = 'https://example.com/requirements'
    with patch.object(extractor, '_extract_from_web', return_value=[{'id': 7, 'requirement': 'System shall extract from web data'}]):
        result = extractor.extract(url)
        assert isinstance(result, list)
        assert result[0]['requirement'] == 'System shall extract from web data'
