# ui/main_window.py
# 字帖生成器主窗口
import os
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QComboBox, QSpinBox, QPushButton, QFileDialog,
    QMessageBox, QLineEdit,
)
from PyQt6.QtCore import QThread, pyqtSignal

from engine.pdf_generator import generate_pdf


class GenerateWorker(QThread):
    """后台生成线程，不阻塞 UI。"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, output_path: str, grade: int, chars_per_row: int, rows: int, title: str):
        super().__init__()
        self.output_path = output_path
        self.grade = grade
        self.chars_per_row = chars_per_row
        self.rows = rows
        self.title = title

    def run(self):
        try:
            generate_pdf(
                self.output_path,
                grade=self.grade,
                cols=self.chars_per_row,
                rows=self.rows,
                title=self.title,
            )
            self.finished.emit(self.output_path)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """字帖生成器主窗口。"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("字帖生成器")
        self.setFixedSize(420, 320)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setSpacing(12)

        # 年级
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("年级："))
        self.grade_combo = QComboBox()
        self.grade_combo.addItems([f"{i}年级" for i in range(1, 7)])
        row1.addWidget(self.grade_combo)
        row1.addStretch()
        layout.addLayout(row1)

        # 列数（每行几个字）
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("每行字数："))
        self.cols_spin = QSpinBox()
        self.cols_spin.setRange(1, 4)
        self.cols_spin.setValue(1)
        row2.addWidget(self.cols_spin)
        row2.addStretch()
        layout.addLayout(row2)

        # 行数
        row3 = QHBoxLayout()
        row3.addWidget(QLabel("每页行数："))
        self.rows_spin = QSpinBox()
        self.rows_spin.setRange(2, 15)
        self.rows_spin.setValue(10)
        row3.addWidget(self.rows_spin)
        row3.addStretch()
        layout.addLayout(row3)

        # 标题
        row4 = QHBoxLayout()
        row4.addWidget(QLabel("字帖标题："))
        self.title_edit = QLineEdit("一年级生字练习")
        row4.addWidget(self.title_edit)
        layout.addLayout(row4)

        layout.addStretch()

        # 生成按钮
        self.generate_btn = QPushButton("生成 PDF")
        self.generate_btn.setMinimumHeight(40)
        self.generate_btn.clicked.connect(self.on_generate)
        layout.addWidget(self.generate_btn)

        self.worker = None

    def on_generate(self):
        grade = self.grade_combo.currentIndex() + 1
        chars_per_row = self.cols_spin.value()
        rows = self.rows_spin.value()
        title = self.title_edit.text()

        default_name = f"{grade}年级字帖.pdf"
        output_path, _ = QFileDialog.getSaveFileName(
            self, "保存字帖", default_name, "PDF (*.pdf)"
        )
        if not output_path:
            return

        self.generate_btn.setEnabled(False)
        self.generate_btn.setText("正在生成…")

        self.worker = GenerateWorker(output_path, grade, chars_per_row, rows, title)
        self.worker.finished.connect(self.on_success)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_success(self, path: str):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成 PDF")
        QMessageBox.information(self, "完成", f"字帖已生成：\n{path}")
        self._open_file(path)

    def on_error(self, msg: str):
        self.generate_btn.setEnabled(True)
        self.generate_btn.setText("生成 PDF")
        QMessageBox.critical(self, "生成失败", f"发生错误：\n{msg}")

    @staticmethod
    def _open_file(path: str):
        """在系统默认应用中打开文件。"""
        try:
            if os.name == "nt":
                os.startfile(path)
            elif os.uname().sysname == "Darwin":
                os.system(f'open "{path}"')
        except Exception:
            pass
