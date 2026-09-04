from PySide6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QWidget,
                               QLabel, QPushButton, QProgressBar)
from PySide6.QtCore import Qt, Signal
from models.task import SmallTask, BigTask


class SmallTaskRow(QWidget):
    """小任务行：勾选框 + 标题"""
    toggled = Signal(str, bool)

    def __init__(self, task: SmallTask, parent=None):
        super().__init__(parent)
        self.setObjectName("TaskRow")
        self.task = task
        self._init_ui()
        self._apply_state()

    def _init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 3, 4, 3)
        layout.setSpacing(10)

        self.icon_btn = QPushButton()
        self.icon_btn.setFixedSize(18, 18)
        self.icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.icon_btn.clicked.connect(self._on_toggle)

        self.title_label = QLabel(self.task.title)
        self.title_label.setWordWrap(True)

        self.pomo_badge = QLabel(f"{self.task.pomo} 🍅" if self.task.pomo else "1 🍅")
        self.pomo_badge.setObjectName("MetaText")

        layout.addWidget(self.icon_btn)
        layout.addWidget(self.title_label, stretch=1)
        layout.addWidget(self.pomo_badge)

    def _on_toggle(self):
        if self.task.done:
            return
        self.task.done = True
        self._apply_state()
        self.toggled.emit(self.task.id, True)

    def _apply_state(self):
        if self.task.done:
            self.icon_btn.setObjectName("TaskDotDone")
            self.icon_btn.setText("✓")
            self.icon_btn.setEnabled(False)
            self.icon_btn.setCursor(Qt.CursorShape.ArrowCursor)
            self.icon_btn.setToolTip("已完成")
            self.title_label.setObjectName("TaskTitleDone")
        else:
            self.icon_btn.setObjectName("TaskDot")
            self.icon_btn.setText("")
            self.icon_btn.setEnabled(True)
            self.icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.icon_btn.setToolTip("点击完成任务（完成后不可取消）")
            self.title_label.setObjectName("TaskTitle")
        self.icon_btn.style().unpolish(self.icon_btn)
        self.icon_btn.style().polish(self.icon_btn)
        self.title_label.style().unpolish(self.title_label)
        self.title_label.style().polish(self.title_label)


class BigTaskCard(QFrame):
    """大任务卡片：胶囊标题 + 进度 + 小任务列表（纯净排版，无 Emoji 与冗余图片）"""
    task_toggled = Signal(str, str, bool)  # (big_task_id, small_task_id, done)

    def __init__(self, big: BigTask, parent=None, tasks: list = None):
        super().__init__(parent)
        self.setObjectName("BigCard")
        self.big = big
        self.tasks = tasks if tasks is not None else big.tasks
        self._init_ui()

    def _init_ui(self):
        from ui.icon_helper import clean_title_no_emoji
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(10)

        header = QHBoxLayout()
        header.setContentsMargins(0, 0, 0, 0)
        header.setSpacing(8)

        # 胶囊垫底背景（纯净字体排版，无任何 Emoji 与图标侵入）
        pill = QFrame()
        pill.setObjectName("TaskTitleCapsule")
        pill_lay = QHBoxLayout(pill)
        pill_lay.setContentsMargins(12, 4, 12, 4)
        pill_lay.setSpacing(8)

        clean_title = clean_title_no_emoji(self.big.title)
        self.title_label = QLabel(clean_title)
        self.title_label.setObjectName("CapsuleTitle")
        pill_lay.addWidget(self.title_label)

        sep_lbl = QLabel("·")
        sep_lbl.setObjectName("CapsuleCount")
        pill_lay.addWidget(sep_lbl)

        done_cnt = sum(1 for t in self.tasks if t.done)
        tot_cnt = len(self.tasks)
        self.meta_label = QLabel(f"{done_cnt}/{tot_cnt}")
        self.meta_label.setObjectName("CapsuleCount")
        pill_lay.addWidget(self.meta_label)

        header.addWidget(pill)
        header.addStretch()
        layout.addLayout(header)

        pct = int(done_cnt / tot_cnt * 100) if tot_cnt > 0 else 0
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(pct)
        layout.addWidget(self.progress_bar)

        for task in self.tasks:
            row = SmallTaskRow(task)
            row.toggled.connect(lambda done, tid=task.id: self.task_toggled.emit(self.big.id, tid, done))
            layout.addWidget(row)

    def refresh(self):
        """外部状态变更后刷新计数与进度"""
        done_cnt = sum(1 for t in self.tasks if t.done)
        tot_cnt = len(self.tasks)
        pct = int(done_cnt / tot_cnt * 100) if tot_cnt > 0 else 0
        self.meta_label.setText(f"{done_cnt}/{tot_cnt}")
        self.progress_bar.setValue(pct)