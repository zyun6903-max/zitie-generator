# engine/grid_layout.py
# 一字三描红布局：每字占 4 个田字格（3 描红 + 1 空白临写）
from dataclasses import dataclass

A4_PORTRAIT = (595.27, 841.89)  # pt
MARGIN = 48  # 边距


@dataclass
class PageConfig:
    """页面配置。每个字占 cols 个格子（标准：4格一字三描红）。"""
    chars_per_row: int = 2           # 每行几个字
    cells_per_char: int = 4          # 每字几个田格
    rows: int = 10                   # 练习区行数
    margin: float = MARGIN
    page_width: float = A4_PORTRAIT[0]
    page_height: float = A4_PORTRAIT[1]
    header_height: float = 80        # 笔顺区高度


class PageGrid:
    """田字格网格布局。"""

    def __init__(self, config: PageConfig):
        self.config = config

    @property
    def cols(self) -> int:
        """总列数 = 每行字数 × 每字格数"""
        return self.config.chars_per_row * self.config.cells_per_char

    @property
    def usable_width(self) -> float:
        return self.config.page_width - 2 * self.config.margin

    @property
    def cell_size(self) -> float:
        """田字格方形边长。"""
        return self.usable_width / self.cols

    @property
    def usable_height(self) -> float:
        return self.config.page_height - 2 * self.config.margin

    def get_header_cell(self, index: int) -> tuple[float, float, float]:
        """笔顺头部的田字格位置。每字占 stroke_count+1 个格子。"""
        cell_size = self.cell_size * 0.55
        total_w = (index + 1) * cell_size
        x_start = (self.config.page_width - total_w) / 2
        y = self.config.page_height - self.config.margin - cell_size
        return x_start, y, cell_size

    def get_char_cells(self, char_index: int) -> list[tuple[float, float, float]]:
        """返回一个字占的 N 个田字格位置列表 [x, y, size]。"""
        row = char_index // self.config.chars_per_row
        col_in_row = char_index % self.config.chars_per_row
        start_col = col_in_row * self.config.cells_per_char
        y = (self.config.page_height - self.config.margin
             - self.config.header_height
             - (row + 1) * self.cell_size)
        result = []
        for i in range(self.config.cells_per_char):
            x = self.config.margin + (start_col + i) * self.cell_size
            result.append((x, y, self.cell_size))
        return result

    def get_pinyin_pos(self, x: float, y: float, size: float) -> tuple[float, float]:
        """拼音位置（田字格正上方）。"""
        return x, y + size + 2


def generate_char_groups(chars_info: list, config: PageConfig) -> list[list[dict]]:
    """将生字分组为每页的字符列表。"""
    per_page = config.chars_per_row * config.rows
    pages = []
    for i in range(0, len(chars_info), per_page):
        pages.append(chars_info[i:i + per_page])
    return pages
