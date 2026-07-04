# ui/progress.py
# PDF 生成进度对话框
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel
from PyQt6.QtCore import Qt


class ProgressDialog(QDialog):
    """生成进度弹窗，带不确定进度条。"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("正在生成字帖…")
        self.setFixedSize(360, 120)
        self.setModal(True)

        layout = QVBoxLayout(self)
        self.label = QLabel("正在生成 PDF…")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # 不确定模式
        layout.addWidget(self.label)
        layout.addWidget(self.progress)

    def set_progress(self, value: int, maximum: int):
        self.progress.setRange(0, maximum)
        self.progress.setValue(value)
