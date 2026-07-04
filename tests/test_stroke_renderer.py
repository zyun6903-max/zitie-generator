# tests/test_stroke_renderer.py
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas

from engine.stroke_renderer import draw_strokes_on_canvas, render_partial_strokes


def _make_canvas(path):
    return canvas.Canvas(str(path))


def test_draw_single_stroke_creates_pdf():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    c = _make_canvas(path)
    strokes = ["M 0 0 L 100 100"]
    draw_strokes_on_canvas(c, strokes, 50, 50, 100, 100)
    c.showPage()
    c.save()
    assert path.exists()
    assert path.stat().st_size > 100
    path.unlink()


def test_render_partial_first_only():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    c = _make_canvas(path)
    strokes = ["M 0 0 L 50 50", "M 50 50 L 100 0"]
    render_partial_strokes(c, strokes, 1, 50, 50, 100, 100)
    c.showPage()
    c.save()
    assert path.exists()
    path.unlink()


def test_empty_strokes():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    c = _make_canvas(path)
    render_partial_strokes(c, [], 0, 50, 50, 100, 100)
    c.showPage()
    c.save()
    path.unlink()
