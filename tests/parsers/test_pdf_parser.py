from pathlib import Path

from src.parsers.pdf_parser import extract_links,extract_text,extract_text_blocks


def test_extract_links():
    pdf_path = Path("tests/fixtures/HARSHIT_WEBDEV.pdf")
    content = pdf_path.read_bytes()

    result = extract_links(content)

    assert result

    assert result[0]["url"].startswith("https://")
    assert "bbox" in result[0]
    assert "page" in result[0]

    assert isinstance(result[0]["bbox"], tuple)
    assert len(result[0]["bbox"]) == 4
    assert isinstance(result[0]["page"], int)

def test_extract_text_blocks():
    pdf_path = Path("tests/fixtures/HARSHIT_WEBDEV.pdf")
    content = pdf_path.read_bytes()

    result = extract_text_blocks(content)

    assert result

    block = result[0]
    texts = [block["text"] for block in result]

    assert any(
                  "Bloger - A Full Stack Blog App" in text
                 for text in texts
         )
    assert "text" in block
    assert "bbox" in block
    assert "page" in block
  
    assert isinstance(block["text"], str)
    assert isinstance(block["bbox"], tuple)
    assert len(block["bbox"]) == 4
    assert isinstance(block["page"], int)