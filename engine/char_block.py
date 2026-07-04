# engine/char_block.py
# 在田字格中渲染汉字（描红/空心/空白）
from engine.stroke_renderer import draw_strokes_on_canvas

TRACE_SOLID = (0.88, 0.18, 0.18)   # 实心描红（参考范例）
TRACE_LIGHT = (0.92, 0.42, 0.42)   # 浅色空心描红（供临摹）
OUTLINE_COLOR = (0.85, 0.50, 0.50) # 空心轮廓
BLACK = (0, 0, 0)


def draw_tianzige(canvas, x: float, y: float, size: float,
                  line_width: float = 1.0):
    """绘制田字格，y 为左下角。"""
    canvas.setStrokeColorRGB(0.6, 0.6, 0.6)
    canvas.setLineWidth(line_width)
    canvas.rect(x, y, size, size)
    canvas.setLineWidth(0.5)
    canvas.setDash(2, 3)
    canvas.line(x, y + size / 2, x + size, y + size / 2)
    canvas.line(x + size / 2, y, x + size / 2, y + size)
    canvas.setDash()


def draw_char_in_grid(canvas, char: str, stroke_paths: list[str],
                      x: float, y: float, cell_size: float,
                      mode: str = "trace"):
    """在田字格中绘制汉字。

    Args:
        mode: "solid" — 实心深红描红
              "trace" — 浅红描红
              "outline" — 空心轮廓描红
              "blank" — 空白（不画字）
    """
    if mode == "blank" or not stroke_paths:
        return

    color_map = {
        "solid": TRACE_SOLID,
        "trace": TRACE_LIGHT,
        "outline": OUTLINE_COLOR,
        "full": BLACK,
    }
    color = color_map.get(mode, TRACE_LIGHT)

    margin = cell_size * 0.08
    draw_size = cell_size - margin * 2
    cx = x + (cell_size - draw_size) / 2
    cy = y + (cell_size - draw_size) / 2

    draw_strokes_on_canvas(
        canvas, stroke_paths,
        cx, cy, draw_size, draw_size,
        stroke_width=1.5 if mode == "solid" else 0.6,
        color=color,
        fill=mode == "solid",
    )


def draw_pinyin(canvas, pinyin: str, x: float, y: float, cell_size: float):
    """在田字格上方绘制拼音。"""
    # 使用 LXGW WenKai 显示拼音声调符号，fallback 到 Helvetica
    font_name = "LXGWWenKai"
    try:
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from pathlib import Path
        font_path = Path(__file__).resolve().parent.parent / "data" / "fonts" / "LXGWWenKai-Regular.ttf"
        if font_path.exists():
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
    except Exception:
        font_name = "Helvetica"

    font_size = cell_size * 0.18
    canvas.setFont(font_name, font_size)
    canvas.setFillColorRGB(0.3, 0.3, 0.3)
    tw = canvas.stringWidth(pinyin, font_name, font_size)
    px = x + (cell_size - tw) / 2
    canvas.drawString(px, y + cell_size + 1, pinyin)
    canvas.setFillColorRGB(0, 0, 0)


def draw_stroke_header(canvas, char: str, pinyin: str,
                       stroke_paths: list[str],
                       x: float, y: float, cell_size: float):
    """在笔顺区绘制一个字的笔顺构建。"""
    n = len(stroke_paths) or 1
    sub = cell_size * 0.65

    # 第一个：完整描红
    draw_tianzige(canvas, x, y, sub)
    draw_char_in_grid(canvas, char, stroke_paths, x, y, sub, "solid")

    # 逐笔累加
    for i in range(1, n + 1):
        sx = x + i * sub + 3
        draw_tianzige(canvas, sx, y, sub)
        if i < n:
            draw_strokes_on_canvas(
                canvas, stroke_paths[:i],
                sx + sub * 0.1, y + sub * 0.1,
                sub * 0.8, sub * 0.8,
                stroke_width=1.0, color=BLACK,
            )
        else:
            draw_strokes_on_canvas(
                canvas, stroke_paths,
                sx + sub * 0.1, y + sub * 0.1,
                sub * 0.8, sub * 0.8,
                stroke_width=1.0, color=BLACK,
            )
