# tests/test_pdf_generator.py
import tempfile
from pathlib import Path
from engine.pdf_generator import query_chars, generate_pdf


def test_query_chars_returns_data():
    chars = query_chars(1)
    assert len(chars) > 0
    assert "char" in chars[0]
    assert "pinyin" in chars[0]
    assert "stroke_paths" in chars[0]


def test_generate_pdf_creates_file():
    output = Path(tempfile.mktemp(suffix=".pdf"))
    try:
        generate_pdf(str(output), grade=1, cols=2, rows=8)
        assert output.exists()
        assert output.stat().st_size > 1000
    finally:
        if output.exists():
            output.unlink()


def test_generate_pdf_grade_2():
    output = Path(tempfile.mktemp(suffix=".pdf"))
    try:
        generate_pdf(str(output), grade=2, cols=2, rows=6)
        assert output.exists() and output.stat().st_size > 1000
    finally:
        if output.exists():
            output.unlink()
