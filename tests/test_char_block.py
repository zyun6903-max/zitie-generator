# tests/test_char_block.py
import tempfile
from pathlib import Path
from reportlab.pdfgen import canvas
from engine.char_block import draw_tianzige, draw_char_in_grid, draw_pinyin


def test_draw_tianzige():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    c = canvas.Canvas(str(path))
    draw_tianzige(c, 100, 100, 80)
    c.showPage()
    c.save()
    assert path.exists() and path.stat().st_size > 100
    path.unlink()


def test_draw_char_in_grid_modes():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    c = canvas.Canvas(str(path))
    strokes = ["M 0 0 L 50 50", "M 50 50 L 100 0"]
    for i, mode in enumerate(["solid", "trace", "outline", "blank"]):
        x = 50 + i * 90
        draw_tianzige(c, x, 50, 80)
        draw_char_in_grid(c, "好", strokes, x, 50, 80, mode)
    c.showPage()
    c.save()
    path.unlink()


def test_draw_pinyin():
    path = Path(tempfile.mktemp(suffix=".pdf"))
    c = canvas.Canvas(str(path))
    draw_tianzige(c, 100, 100, 80)
    draw_pinyin(c, "hǎo", 100, 100, 80)
    c.showPage()
    c.save()
    path.unlink()
