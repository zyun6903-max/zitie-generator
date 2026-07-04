# data_prep/build_db.py
# 构建 vocab.db：包含生字、拼音、逐笔笔顺数据
import json
import sqlite3
import sys
import urllib.request
from pathlib import Path

import pypinyin

from grade_vocab import get_all_chars

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "vocab.db"
GRAPHICS_URL = "https://raw.githubusercontent.com/skishore/makemeahanzi/master/graphics.txt"


def fetch_stroke_data() -> dict[str, list[str]]:
    """下载 makemeahanzi 笔顺数据，返回 {char: [svg_path_strings]}"""
    print("正在下载笔顺数据...")
    response = urllib.request.urlopen(GRAPHICS_URL)
    data: dict[str, list[str]] = {}
    total_lines = 0
    for line_bytes in response:
        line = line_bytes.decode("utf-8").strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
            char = obj["character"]
            strokes = obj["strokes"]
            data[char] = strokes
            total_lines += 1
        except (json.JSONDecodeError, KeyError):
            continue
    print(f"已获取 {total_lines} 个汉字的笔顺数据")
    return data


def build_db():
    stroke_data = fetch_stroke_data()
    chars = get_all_chars()
    seen = set()

    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE vocab (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            char TEXT NOT NULL UNIQUE,
            pinyin TEXT NOT NULL,
            grade INTEGER NOT NULL CHECK(grade BETWEEN 1 AND 6),
            lesson INTEGER,
            stroke_count INTEGER
        )
    """)
    conn.execute("""
        CREATE TABLE strokes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            char TEXT NOT NULL REFERENCES vocab(char),
            stroke_index INTEGER NOT NULL,
            svg_path TEXT NOT NULL
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_vocab_grade ON vocab(grade)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_strokes_char ON strokes(char)")

    inserted = 0
    for char_info in chars:
        char = char_info["char"]
        if char in seen:
            continue
        seen.add(char)

        # 拼音
        pinyins = pypinyin.pinyin(char, style=pypinyin.Style.TONE)
        pinyin = " ".join([p[0] for p in pinyins])

        # 笔顺
        strokes = stroke_data.get(char, [])

        conn.execute(
            "INSERT INTO vocab (char, pinyin, grade, lesson, stroke_count) VALUES (?, ?, ?, ?, ?)",
            (char, pinyin, char_info["grade"], char_info["lesson"], len(strokes)),
        )

        for idx, path_str in enumerate(strokes):
            conn.execute(
                "INSERT INTO strokes (char, stroke_index, svg_path) VALUES (?, ?, ?)",
                (char, idx, path_str),
            )

        inserted += 1
        if inserted % 500 == 0:
            print(f"已处理 {inserted} 字...")
            conn.commit()

    conn.commit()
    conn.close()
    print(f"数据库已构建：{DB_PATH}")
    print(f"共 {inserted} 个不重复汉字")


if __name__ == "__main__":
    build_db()
