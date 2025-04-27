Certainly! Below are comprehensive pytest test cases for the user story: "Extract structured requirements from diverse input formats". The tests cover main functionality, acceptance criteria, and edge cases.

Assumptions:
- There is a function called extract_requirements(document_path: str) -> dict that extracts requirements in structured format from any supported document.
- Supported formats: PDF, DOCX/Word, emails (EML/MSG), and graph files (assumed as a custom format, e.g., JSON, GraphML, etc.).
- There is a function is_structured(data: dict) -> bool that validates if extraction output is structured as expected.
- The code uses temporary files for setup/teardown and sample documents for input.

Here is the code:

```python
import pytest
import tempfile
import shutil
import os

# Assume these are implemented in your source code
from requirement_extractor import extract_requirements, is_structured

# Fixtures for setup and teardown

@pytest.fixture(scope="module")
def sample_documents(tmp_path_factory):
    """
    Setup: Create sample documents of each supported type with known structured content.
    Teardown: Remove temporary files after the tests.
    """
    base_dir = tmp_path_factory.mktemp("docs")
    samples = {}

    # Create a sample PDF
    pdf_path = base_dir / "sample.pdf"
    with open(pdf_path, "wb") as f:
        f.write(b"%PDF-1.4\n% Sample PDF content for requirements\n")  # Minimal PDF header

    # Create a sample DOCX
    docx_path = base_dir / "sample.docx"
    with open(docx_path, "wb") as f:
        f.write(b"PK\x03\x04...")  # Minimal DOCX header (not valid, but suffices for test context)

    # Create a sample EML (Email)
    eml_path = base_dir / "sample.eml"
    with open(eml_path, "w") as f:
        f.write("Subject: Requirement\n\nRequirement ID: REQ-001\nDescription: The system shall...")

    # Create a sample Graph (assuming JSON format for the test)
    graph_path = base_dir / "sample_graph.json"
    with open(graph_path, "w") as f:
        f.write('{"nodes":[{"id":"REQ-001","label":"Requirement"}],"edges":[]}')

    samples['pdf'] = str(pdf_path)
    samples['docx'] = str(docx_path)
    samples['eml'] = str(eml_path)
    samples['graph'] = str(graph_path)
    return samples

# Main functionality: Test extraction for all formats
@pytest.mark.parametrize("doc_type", ["pdf", "docx", "eml", "graph"])
def test_extract_supported_formats(sample_documents, doc_type):
    """
    Test extraction of requirements from each supported file format.
    """
    doc_path = sample_documents[doc_type]
    result = extract_requirements(doc_path)
    assert is_structured(result), f"Extracted data from {doc_type} is not structured as expected"
    assert result, f"No requirements extracted from {doc_type}"

def test_extraction_accuracy(sample_documents):
    """
    Test that the extraction succeeds for at least 95% of uploaded documents (acceptance criteria).
    Here, we simulate with 20 documents (5 of each type), 1 known bad PDF.
    """
    total = 20
    success = 0
    # Simulate 4 valid docs of each type, total 16, and 4 invalid ones
    for i in range(4):
        for doc_type, path in sample_documents.items():
            result = extract_requirements(path)
            if is_structured(result):
                success += 1

    # Add 4 invalid docs (simulate corrupted/unsupported files)
    for i in range(4):
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"Not a real PDF")
            path = f.name
        result = extract_requirements(path)
        if is_structured(result):
            success += 1
        os.unlink(path)

    assert success / total >= 0.95, f"Extraction succeeded for only {success}/{total} documents"

# Edge case: Empty document
def test_empty_document(tmp_path):
    """
    Test extraction from an empty file should return empty or error, not crash.
    """
    empty_file = tmp_path / "empty.pdf"
    empty_file.write_bytes(b"")
    result = extract_requirements(str(empty_file))
    assert result == {} or result is None, "Extractor should return empty for empty document"

# Edge case: Corrupted/unsupported file
def test_corrupted_document(tmp_path):
    """
    Test extraction from a corrupted file should handle error gracefully.
    """
    bad_file = tmp_path / "corrupted.docx"
    bad_file.write_bytes(b"This is not a real docx file")
    result = extract_requirements(str(bad_file))
    assert result == {} or result is None, "Extractor should return empty for corrupted document"

# Edge case: Unsupported format
def test_unsupported_format(tmp_path):
    """
    Test extracting from an unsupported file type should raise an error or return None/empty.
    """
    unsupported_file = tmp_path / "unsupported.txt"
    unsupported_file.write_text("This is a plain text file.")
    with pytest.raises(Exception):
        extract_requirements(str(unsupported_file))

# Edge case: Large document
def test_large_document(tmp_path):
    """
    Test extraction from a very large document (simulate by repeating content).
    """
    large_file = tmp_path / "large.pdf"
    content = b"%PDF-1.4\n" + b"Requirement: The system shall...\n" * 10000
    large_file.write_bytes(content)
    result = extract_requirements(str(large_file))
    assert is_structured(result), "Extractor failed to handle large document"
    assert result, "Extractor failed to extract requirements from large document"

# Edge case: Document with mixed content (e.g., images, tables, text)
def test_mixed_content_document(tmp_path):
    """
    Test extraction from a document with mixed content types.
    """
    mixed_file = tmp_path / "mixed.docx"
    # Simulate by writing a placeholder header
    mixed_file.write_bytes(b"PK\x03\x04...Mixed content with tables and images...")
    result = extract_requirements(str(mixed_file))
    assert is_structured(result), "Extractor failed on mixed content document"

# Optional: Teardown handled by pytest fixtures and temporary files.

```

**Notes:**

- Replace the dummy implementations and file contents with proper mocks or fixtures as needed for your actual application.
- If extract_requirements raises exceptions for bad files, replace assertions with `pytest.raises` as appropriate.
- The test files are minimal and may not be valid for real extraction functions; for integration tests, use actual sample files.
- The test for 95% extraction uses a simple simulation; adapt it for your real document corpus as required.

Let me know if you need mocks or further customization!