# engine/pdf_generator.py
# PDF 字帖主编排 — 一字三描红布局
import sqlite3
from pathlib import Path
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from engine.grid_layout import PageConfig, PageGrid, generate_char_groups
from engine.char_block import (
    draw_tianzige, draw_char_in_grid, draw_pinyin,
)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "vocab.db"
FONT_PATH = DATA_DIR / "fonts" / "LXGWWenKai-Regular.ttf"

try:
    pdfmetrics.registerFont(TTFont("LXGWWenKai", str(FONT_PATH)))
    _FONT_OK = True
except Exception:
    _FONT_OK = False


def query_chars(grade: int) -> list[dict]:
    """从 vocab.db 查询某年级所有生字。"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.execute(
        "SELECT char, pinyin, stroke_count FROM vocab WHERE grade = ? ORDER BY lesson, id",
        (grade,),
    )
    result = []
    for char, pinyin, stroke_count in cursor.fetchall():
        strokes_cursor = conn.execute(
            "SELECT svg_path FROM strokes WHERE char = ? ORDER BY stroke_index",
            (char,),
        )
        stroke_paths = [row[0] for row in strokes_cursor.fetchall()]
        result.append({
            "char": char,
            "pinyin": pinyin,
            "stroke_paths": stroke_paths,
            "stroke_count": stroke_count or len(stroke_paths),
        })
    conn.close()
    return result


def generate_pdf(output_path: str | Path, grade: int,
                 cols: int = 2, rows: int = 10,
                 title: str = ""):
    """生成字帖 PDF — 一字三描红格式。

    布局：
    1. 标题行
    2. 笔顺区（每个字展示 stroke build-up）
    3. 练习区（每个字 4 个田格：实心描红 → 浅描红 → 浅描红 → 空白）
    """
    chars_info = query_chars(grade)
    if not chars_info:
        raise ValueError(f"年级 {grade} 没有生字数据")

    config = PageConfig(chars_per_row=cols, rows=rows, cells_per_char=8)
    pages = generate_char_groups(chars_info, config)
    grid = PageGrid(config)

    c = rl_canvas.Canvas(str(output_path), pagesize=A4)

    for page_idx, page_chars in enumerate(pages):
        if page_idx > 0:
            c.showPage()

        # --- 标题 ---
        if title:
            font_name = "LXGWWenKai" if _FONT_OK else "Helvetica"
            c.setFont(font_name, 14)
            c.drawCentredString(A4[0] / 2, A4[1] - 28, title)

        # --- 笔顺区 ---
        stroke_y = A4[1] - config.margin - config.header_height + 5
        stroke_h = config.header_height - 10
        header_chars = page_chars[:4]
        if header_chars:
            header_col_w = grid.usable_width / len(header_chars)

            for i, info in enumerate(header_chars):
                n = len(info["stroke_paths"])
                gap = 1
                # (n+1)*sub + n*gap ≤ header_col_w
                max_sub_w = (header_col_w - n * gap) / (n + 1)
                sub = min(max_sub_w, stroke_h, grid.cell_size * 0.45)
                sub = max(sub, 6)

                start_x = config.margin + header_col_w * i
                total_w = (n + 1) * sub + n * gap
                gx = start_x + (header_col_w - total_w) / 2
                gy = stroke_y + (stroke_h - sub) / 2

                # 完整描红
                draw_tianzige(c, gx, gy, sub)
                draw_char_in_grid(c, info["char"], info["stroke_paths"],
                                  gx, gy, sub, "solid")

                # 逐笔构建
                for j in range(1, n + 1):
                    sx = gx + j * (sub + gap)
                    draw_tianzige(c, sx, gy, sub)
                    paths = info["stroke_paths"][:j]
                    from engine.stroke_renderer import draw_strokes_on_canvas
                    draw_strokes_on_canvas(
                        c, paths,
                        sx + sub * 0.1, gy + sub * 0.1,
                        sub * 0.8, sub * 0.8,
                        stroke_width=0.8, color=(0, 0, 0),
                    )

        # --- 练习区（2字一组，每组4行） ---
        cs = grid.cell_size
        margin = config.margin
        # 第一行练习区的 y 坐标（田字格左下角）
        row0_y = (A4[1] - config.margin - config.header_height - cs)

        for pair_idx in range(0, len(page_chars), 2):
            pair = page_chars[pair_idx:pair_idx + 2]
            if not pair:
                break

            for local_idx, info in enumerate(pair):
                paths = info["stroke_paths"]
                n = len(paths)
                # 每字占2行，base_y = row0_y - (pair中的第几个) * 2 * cs
                base_y = row0_y - (pair_idx + local_idx) * 2 * cs

                if local_idx == 0:
                    # === 第一个字：4笔顺 + 4描红／8描红 ===
                    b = min(4, n)
                    # Row 1: 4列笔顺构建
                    for col in range(b):
                        x = margin + col * cs
                        draw_tianzige(c, x, base_y, cs)
                        draw_char_in_grid(c, info["char"], paths[:col + 1],
                                          x, base_y, cs, "solid")
                    for col in range(b, 4):
                        x = margin + col * cs
                        draw_tianzige(c, x, base_y, cs)
                        draw_char_in_grid(c, info["char"], paths,
                                          x, base_y, cs, "trace")
                    # 4列描红
                    for col in range(4, 8):
                        x = margin + col * cs
                        draw_pinyin(c, info["pinyin"], x, base_y, cs)
                        draw_tianzige(c, x, base_y, cs)
                        draw_char_in_grid(c, info["char"], paths,
                                          x, base_y, cs, "trace")
                    # Row 2: 8列描红
                    row2_y = base_y - cs
                    for col in range(8):
                        x = margin + col * cs
                        draw_tianzige(c, x, row2_y, cs)
                        draw_char_in_grid(c, info["char"], paths,
                                          x, row2_y, cs, "trace")

                else:
                    # === 第二个字：6笔顺 + 2描红／8描红 ===
                    b = min(6, n)
                    # Row 3: 6列笔顺构建
                    for col in range(b):
                        x = margin + col * cs
                        draw_tianzige(c, x, base_y, cs)
                        draw_char_in_grid(c, info["char"], paths[:col + 1],
                                          x, base_y, cs, "solid")
                    for col in range(b, 6):
                        x = margin + col * cs
                        draw_tianzige(c, x, base_y, cs)
                        draw_char_in_grid(c, info["char"], paths,
                                          x, base_y, cs, "trace")
                    # 2列描红
                    for col in range(6, 8):
                        x = margin + col * cs
                        draw_pinyin(c, info["pinyin"], x, base_y, cs)
                        draw_tianzige(c, x, base_y, cs)
                        draw_char_in_grid(c, info["char"], paths,
                                          x, base_y, cs, "trace")
                    # Row 4: 8列描红
                    row4_y = base_y - cs
                    for col in range(8):
                        x = margin + col * cs
                        draw_tianzige(c, x, row4_y, cs)
                        draw_char_in_grid(c, info["char"], paths,
                                          x, row4_y, cs, "trace")

    c.save()
