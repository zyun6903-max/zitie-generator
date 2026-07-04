# tests/test_grid_layout.py
from engine.grid_layout import PageGrid, PageConfig, generate_char_groups


def test_cell_size():
    config = PageConfig(chars_per_row=2)
    grid = PageGrid(config)
    # 2 chars × 4 cells = 8 columns
    assert grid.cols == 8
    assert grid.cell_size > 0


def test_get_char_cells():
    config = PageConfig(chars_per_row=2)
    grid = PageGrid(config)
    cells = grid.get_char_cells(0)
    assert len(cells) == 4  # 一字三描红 = 4 格
    for x, y, size in cells:
        assert size == grid.cell_size


def test_generate_char_groups_single():
    chars = [{"char": str(i)} for i in range(10)]
    pages = generate_char_groups(chars, PageConfig(chars_per_row=2, rows=10))
    assert len(pages) == 1
    assert len(pages[0]) == 10


def test_generate_char_groups_split():
    chars = [{"char": str(i)} for i in range(30)]
    pages = generate_char_groups(chars, PageConfig(chars_per_row=2, rows=10))
    assert len(pages) == 2
    assert len(pages[0]) == 20
    assert len(pages[1]) == 10
