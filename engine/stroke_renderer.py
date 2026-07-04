# engine/stroke_renderer.py
# 将 SVG path 字符串渲染到 reportlab canvas 上，支持逐笔累加
from __future__ import annotations

from svg.path import parse_path
from svg.path.path import Move, Line, QuadraticBezier, CubicBezier, Close


def _compute_bounds(stroke_paths: list[str]):
    """计算一组笔画的 bounding box。"""
    all_points = []
    for svg_str in stroke_paths:
        path = parse_path(svg_str)
        for seg in path:
            for attr in ("start", "end", "control", "control1", "control2"):
                pt = getattr(seg, attr, None)
                if pt is not None:
                    all_points.append((pt.real, pt.imag))
    if not all_points:
        return 0, 0, 1, 1
    xs = [p[0] for p in all_points]
    ys = [p[1] for p in all_points]
    return min(xs), min(ys), max(xs), max(ys)


def _draw_svg_path_on_canvas(canvas, svg_str: str,
                              offset_x: float, offset_y: float,
                              scale: float, *, fill: bool = True):
    """将单个 SVG path 字符串绘制到 canvas 上。

    makeahanzi 数据使用 y-up 坐标系（y=0 底部，y=1024 顶部），
    与 reportlab y-up 一致，因此不需要 y 翻转。
    """
    path = parse_path(svg_str)
    p = canvas.beginPath()
    for seg in path:
        if isinstance(seg, Move):
            p.moveTo(offset_x + seg.start.real * scale,
                     offset_y + seg.start.imag * scale)
        elif isinstance(seg, Line):
            p.lineTo(offset_x + seg.end.real * scale,
                     offset_y + seg.end.imag * scale)
        elif isinstance(seg, QuadraticBezier):
            # Q 命令转换为 C 命令：C = (S+2*C)/3, (2*C+E)/3, E
            sx, sy = seg.start.real, seg.start.imag
            cx, cy = seg.control.real, seg.control.imag
            ex, ey = seg.end.real, seg.end.imag
            p.curveTo(
                offset_x + (sx + 2 * cx) / 3 * scale,
                offset_y + (sy + 2 * cy) / 3 * scale,
                offset_x + (2 * cx + ex) / 3 * scale,
                offset_y + (2 * cy + ey) / 3 * scale,
                offset_x + ex * scale,
                offset_y + ey * scale,
            )
        elif isinstance(seg, CubicBezier):
            p.curveTo(
                offset_x + seg.control1.real * scale,
                offset_y + seg.control1.imag * scale,
                offset_x + seg.control2.real * scale,
                offset_y + seg.control2.imag * scale,
                offset_x + seg.end.real * scale,
                offset_y + seg.end.imag * scale,
            )
        elif isinstance(seg, Close):
            p.close()
    canvas.drawPath(p, stroke=not fill, fill=fill)


def draw_strokes_on_canvas(canvas, stroke_paths: list[str],
                           x: float, y: float,
                           width: float, height: float,
                           stroke_width: float = 2.0,
                           color=(0, 0, 0),
                           *, fill: bool = True):
    """在 canvas 上绘制一组笔画。

    Args:
        fill: True 填充笔画，False 仅描边（用于空心描红）
    """
    if not stroke_paths:
        return

    min_x, min_y, max_x, max_y = _compute_bounds(stroke_paths)
    data_w = max_x - min_x
    data_h = max_y - min_y
    if data_w == 0:
        data_w = 1
    if data_h == 0:
        data_h = 1

    scale = min(width / data_w, height / data_h) * 0.85
    ox = x + (width - data_w * scale) / 2 - min_x * scale
    # makeahanzi 使用 y-up 坐标系，与 reportlab 一致，无需翻转
    oy = y + (height - data_h * scale) / 2 - min_y * scale

    canvas.setStrokeColorRGB(*color)
    canvas.setFillColorRGB(*color)
    canvas.setLineWidth(stroke_width if not fill else stroke_width)
    canvas.setLineCap(1)  # round cap
    canvas.setLineJoin(1)  # round join

    for svg_str in stroke_paths:
        _draw_svg_path_on_canvas(canvas, svg_str, ox, oy, scale, fill=fill)


def render_partial_strokes(canvas, stroke_paths: list[str],
                           count: int, x: float, y: float,
                           width: float, height: float,
                           stroke_width: float = 2.0,
                           color=(0, 0, 0)):
    """渲染前 count 笔（0 <= count <= len(stroke_paths)）。"""
    draw_strokes_on_canvas(canvas, stroke_paths[:count],
                           x, y, width, height, stroke_width, color)
