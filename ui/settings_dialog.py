import time

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QCheckBox, QScrollArea, QWidget, QGroupBox, QMessageBox,
    QTabWidget, QFrame, QComboBox, QProgressBar, QGraphicsDropShadowEffect,
    QSlider, QSizeGrip,
)
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QPoint, Signal

from models.task import SmallTask, BigTask, DAYS
from models.user_stats import UserStats, rank_name
from storage.json_storage import JSONStorage
from ui.toast_dialog import ConfirmDialog


class NumberStepper(QWidget):
    """具有明显增减按钮、无 I-beam 文字光标干扰的高可用步进控件"""
    valueChanged = Signal(int)

    def __init__(self, value: int = 0, min_val: int = 0, max_val: int = 1000,
                 step: int = 10, suffix: str = "", parent=None):
        super().__init__(parent)
        self.min_val = min_val
        self.max_val = max_val
        self.step = step
        self.suffix = suffix
        self._val = max(min_val, min(max_val, int(value)))

        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(3)

        self.dec_btn = QPushButton("−")
        self.dec_btn.setObjectName("StepperBtn")
        self.dec_btn.setFixedSize(22, 24)
        self.dec_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dec_btn.setToolTip("减少")
        self.dec_btn.clicked.connect(self._dec)

        self.edit = QLineEdit(self._format_text())
        self.edit.setObjectName("StepperEdit")
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.setCursor(Qt.CursorShape.ArrowCursor)
        self.edit.setFixedWidth(66)
        self.edit.editingFinished.connect(self._on_edit_finished)

        self.inc_btn = QPushButton("+")
        self.inc_btn.setObjectName("StepperBtn")
        self.inc_btn.setFixedSize(22, 24)
        self.inc_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.inc_btn.setToolTip("增加")
        self.inc_btn.clicked.connect(self._inc)

        lay.addWidget(self.dec_btn)
        lay.addWidget(self.edit)
        lay.addWidget(self.inc_btn)

    def _format_text(self) -> str:
        return f"{self._val}{self.suffix}"

    def _dec(self):
        self.setValue(self._val - self.step)

    def _inc(self):
        self.setValue(self._val + self.step)

    def _on_edit_finished(self):
        txt = self.edit.text().replace(self.suffix, "").strip()
        try:
            val = int(txt)
            self.setValue(val)
        except ValueError:
            self.edit.setText(self._format_text())

    def value(self) -> int:
        return self._val

    def setValue(self, v: int):
        new_v = max(self.min_val, min(self.max_val, int(v)))
        old_v = self._val
        self._val = new_v
        self.edit.setText(self._format_text())
        if new_v != old_v:
            self.valueChanged.emit(self._val)


class GlassSettingsDialog(QDialog):
    """与主界面一致的无边框磨砂玻璃弹窗基类（深色暖炭）"""

    def __init__(self, win_title: str, parent=None, size=(860, 620), min_size=(720, 520)):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(*size)
        self.setMinimumSize(*min_size)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)

        self.card = QFrame()
        self.card.setObjectName("DialogCard")
        self.card.setStyleSheet("QFrame#DialogCard { background-color: #23211f; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 16px; }")
        self.body = QVBoxLayout(self.card)
        self.body.setContentsMargins(22, 18, 22, 20)
        self.body.setSpacing(12)
        root.addWidget(self.card)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 90))
        self.card.setGraphicsEffect(shadow)

        bar = QHBoxLayout()
        t = QLabel(win_title)
        t.setObjectName("DialogTitle")
        bar.addWidget(t)
        bar.addStretch()
        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.reject)
        bar.addWidget(close_btn)
        self.body.addLayout(bar)

        self._drag_pos = QPoint()
        self._is_dragging = False

        self.grip = QSizeGrip(self)
        self.grip.setFixedSize(16, 16)
        self.grip.setStyleSheet("background: transparent;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "grip"):
            self.grip.move(self.width() - 24, self.height() - 24)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.position().y() < 40:
            self._is_dragging = True
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._is_dragging = False
        event.accept()


class BigTaskEditorDialog(GlassSettingsDialog):
    """编辑单个大任务：标题 + 小任务清单（支持周排期与行上下排序、数字步进）"""
    changed = Signal()

    def __init__(self, big: BigTask, parent=None):
        super().__init__("编辑大任务", parent, size=(860, 620), min_size=(680, 480))
        self.big = big
        self._rows = []  # (row_widget, task, cb, edit, xp_stepper, day_combo)
        self._build()

    def _build(self):
        from ui.icon_helper import clean_title_no_emoji
        title_lbl = QLabel("大任务标题")
        title_lbl.setObjectName("GroupHeader")
        self.body.addWidget(title_lbl)
        self.title_edit = QLineEdit(clean_title_no_emoji(self.big.title))
        self.title_edit.setPlaceholderText("如：高等数学")
        self.body.addWidget(self.title_edit)

        tag = QLabel("小任务清单　·　安排所属星期、专注番茄与经验奖励（保存后自动按周一至周日排序）")
        tag.setObjectName("GroupHeader")
        self.body.addWidget(tag)

        self.list_box = QWidget()
        self.list_box.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.list_layout = QVBoxLayout(self.list_box)
        self.list_layout.setContentsMargins(0, 2, 0, 0)
        self.list_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        scroll.viewport().setAutoFillBackground(False)
        scroll.setWidget(self.list_box)
        self.body.addWidget(scroll, stretch=1)

        add_btn = QPushButton("＋ 添加小任务")
        add_btn.setObjectName("GhostBtn")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(lambda: self._add_row())
        self.body.addWidget(add_btn)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("GhostBtn")
        cancel_btn.setMinimumWidth(80)
        cancel_btn.setFixedHeight(34)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.setToolTip("放弃修改并关闭")
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.setMinimumWidth(100)
        save_btn.setFixedHeight(34)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setToolTip("保存当前配置并按周一至周日自动排序")
        save_btn.clicked.connect(self._apply)

        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        self.body.addLayout(btn_row)

        for task in self.big.tasks:
            self._add_row(task)

    def _add_row(self, task: SmallTask = None):
        row = QWidget()
        row.setObjectName("TaskRow")
        lay = QHBoxLayout(row)
        lay.setContentsMargins(4, 2, 4, 2)
        lay.setSpacing(8)

        if task is None:
            task = SmallTask(f"new-{int(time.time()*1000)+len(self._rows)}", "新小任务")

        cb = QCheckBox()
        cb.setChecked(task.done)
        if task.done:
            cb.setEnabled(False)
            cb.setToolTip("已完成（不可取消）")
        else:
            cb.setToolTip("完成状态（单向完成，不可取消）")
            cb.setCursor(Qt.CursorShape.PointingHandCursor)

        edit = QLineEdit(task.title)
        edit.setPlaceholderText("小任务内容")
        edit.setMinimumWidth(300)
        edit.setToolTip(task.title)
        edit.textChanged.connect(edit.setToolTip)

        day = QComboBox()
        day.addItem("未排期")
        day.addItems(DAYS)
        day.setCurrentIndex((task.day + 1) if task.day is not None else 0)
        day.setFixedWidth(82)
        day.setCursor(Qt.CursorShape.PointingHandCursor)

        pomo = NumberStepper(value=getattr(task, 'pomo', 1), min_val=1, max_val=20, step=1, suffix=" 🍅")
        xp = NumberStepper(value=task.xp, min_val=0, max_val=1000, step=10, suffix=" XP")

        del_btn = QPushButton("×")
        del_btn.setObjectName("DangerIconBtn")
        del_btn.setFixedSize(26, 26)
        del_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        del_btn.setToolTip("删除该小任务")
        del_btn.clicked.connect(lambda: self._remove_row(row))

        lay.addWidget(cb)
        lay.addWidget(edit, stretch=1)
        lay.addWidget(day)
        lay.addWidget(pomo)
        lay.addWidget(xp)
        lay.addWidget(del_btn)

        self.list_layout.addWidget(row)
        self._rows.append((row, task, cb, edit, xp, day, pomo))

    def _remove_row(self, row_widget):
        idx = -1
        for i, entry in enumerate(self._rows):
            if entry[0] == row_widget:
                idx = i
                break
        if idx >= 0:
            self.list_layout.removeWidget(row_widget)
            row_widget.deleteLater()
            self._rows.pop(idx)

    def _apply(self):
        from ui.icon_helper import clean_title_no_emoji
        self.big.title = clean_title_no_emoji(self.title_edit.text().strip()) or self.big.title
        self.big.tasks = []
        for _, orig_task, cb, edit, xp, day, pomo_stepper in self._rows:
            title = edit.text().strip()
            if not title:
                continue
            d = (day.currentIndex() - 1) if day.currentIndex() > 0 else None
            pomo_val = pomo_stepper.value()
            is_done = orig_task.done if (orig_task and orig_task.done) else cb.isChecked()
            self.big.tasks.append(SmallTask(
                id=orig_task.id if (orig_task and orig_task.id) else f"t-{int(time.time()*1000)+len(self.big.tasks)}",
                title=title, done=is_done, xp=xp.value(), day=d,
                pomo=pomo_val,
                actual_pomo=getattr(orig_task, 'actual_pomo', pomo_val),
                awarded=getattr(orig_task, 'awarded', False) or is_done,
            ))
        # 自动按照星期一至星期天顺序调整排序（未排期放在最后）
        self.big.tasks.sort(key=lambda t: 7 if t.day is None else t.day)
        self.changed.emit()
        self.accept()


class SettingsDialog(GlassSettingsDialog):
    """设置：任务管理 + 账号数据 + 外观。支持周度复盘重置、透明度无极调节与排期管理。"""
    settings_changed = Signal()
    reset_requested = Signal()

    def __init__(self, user_stats: UserStats, big_tasks: list, storage: JSONStorage, parent=None):
        super().__init__("设置", parent, size=(880, 660), min_size=(740, 560))
        self.user_stats = user_stats
        self.big_tasks = big_tasks
        self.storage = storage
        self._build()

    # ---------- 主框架 ----------
    def _build(self):
        tabs = QTabWidget()
        tabs.setDocumentMode(True)
        tabs.addTab(self._build_tasks_tab(), "任务管理")
        tabs.addTab(self._build_account_tab(), "账号数据")
        tabs.addTab(self._build_appearance_tab(), "外观")
        self.body.addWidget(tabs, stretch=1)

        btn_row = QHBoxLayout()
        reset_btn = QPushButton("重置数据")
        reset_btn.setObjectName("DangerBtn")
        reset_btn.clicked.connect(self._on_reset)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        save_btn = QPushButton("保存")
        save_btn.setObjectName("PrimaryBtn")
        save_btn.clicked.connect(self._on_save)
        btn_row.addWidget(reset_btn)
        btn_row.addStretch()
        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(save_btn)
        self.body.addLayout(btn_row)

    # ---------- 任务管理 ----------
    def _build_tasks_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(8)

        self.tree = QWidget()
        self.tree.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.tree_layout = QVBoxLayout(self.tree)
        self.tree_layout.setContentsMargins(0, 0, 6, 0)
        self.tree_layout.setSpacing(12)

        self.tasks_scroll = QScrollArea()
        self.tasks_scroll.setWidgetResizable(True)
        self.tasks_scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        self.tasks_scroll.setStyleSheet("background: transparent;")
        self.tasks_scroll.viewport().setAutoFillBackground(False)
        self.tasks_scroll.setWidget(self.tree)
        lay.addWidget(self.tasks_scroll, stretch=1)

        action_row = QHBoxLayout()
        add_big_btn = QPushButton("＋ 添加大任务")
        add_big_btn.clicked.connect(lambda: self._add_big())

        reset_weekly_btn = QPushButton("周度复盘与一键重置")
        reset_weekly_btn.setObjectName("GhostBtn")
        reset_weekly_btn.setToolTip("重置本周所有小任务的完成打勾状态，任务结构与排期完整保留")
        reset_weekly_btn.clicked.connect(self._on_weekly_reset)

        action_row.addWidget(add_big_btn)
        action_row.addStretch()
        action_row.addWidget(reset_weekly_btn)
        lay.addLayout(action_row)

        self._rebuild()
        return page

    def _rebuild(self):
        while self.tree_layout.count():
            item = self.tree_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        from ui.icon_helper import clean_title_no_emoji

        for big in self.big_tasks:
            card = QFrame()
            card.setObjectName("BigTaskSettingCard")
            lay = QVBoxLayout(card)
            lay.setContentsMargins(14, 12, 14, 12)
            lay.setSpacing(8)

            header_row = QHBoxLayout()
            header_row.setContentsMargins(0, 0, 0, 0)
            header_row.setSpacing(8)

            pill = QFrame()
            pill.setObjectName("TaskTitleCapsule")
            pill_lay = QHBoxLayout(pill)
            pill_lay.setContentsMargins(12, 4, 12, 4)
            pill_lay.setSpacing(8)

            clean_title = clean_title_no_emoji(big.title)
            title_lbl = QLabel(clean_title)
            title_lbl.setObjectName("CapsuleTitle")
            pill_lay.addWidget(title_lbl)

            sep_lbl = QLabel("·")
            sep_lbl.setObjectName("CapsuleCount")
            pill_lay.addWidget(sep_lbl)

            count_lbl = QLabel(f"{big.done_count}/{big.total}")
            count_lbl.setObjectName("CapsuleCount")
            pill_lay.addWidget(count_lbl)

            header_row.addWidget(pill)
            header_row.addStretch()

            budget_lbl = QLabel(f"{big.pomo_budget} 🍅/周" if big.pomo_budget else "0 🍅/周")
            budget_lbl.setObjectName("MetaText")
            header_row.addWidget(budget_lbl)

            edit_btn = QPushButton("编辑")
            edit_btn.setObjectName("GhostBtn")
            edit_btn.clicked.connect(lambda _=False, b=big: self._edit_big(b))

            del_btn = QPushButton("删除")
            del_btn.setObjectName("DangerBtn")
            del_btn.clicked.connect(lambda _=False, b=big: self._delete_big(b))

            header_row.addWidget(edit_btn)
            header_row.addWidget(del_btn)
            lay.addLayout(header_row)

            meta_parts = []
            for t in big.tasks[:3]:
                meta_parts.append(f"{DAYS[t.day]}｜{clean_title_no_emoji(t.title)}" if t.day is not None else clean_title_no_emoji(t.title))
            meta = QLabel(" · ".join(meta_parts) + (" …" if len(big.tasks) > 3 else ""))
            meta.setObjectName("DialogBody")
            meta.setWordWrap(True)
            lay.addWidget(meta)

            self.tree_layout.addWidget(card)

        self.tree_layout.addStretch()

    def _on_weekly_reset(self):
        parent = self.parent()
        if parent and hasattr(parent, "task_service"):
            summary = parent.task_service.get_week_focus_summary()
            msg = (
                f"确定进行周度复盘并结算本周学习沉淀吗？\n\n"
                f"• 本周主线攻坚完成：{summary['task_done']} 🍅\n"
                f"• 本周自由探索投入：{summary['free_done']} 🍅\n"
                f"• 本周学习总投入：{summary['total_pomo']} 🍅（成长点已沉淀至历史记录）\n\n"
                f"• 所有排期小任务进度将重置为未完成（开启新的一周）\n"
                f"• 任务结构、排期与历史成就完整保留"
            )
            if ConfirmDialog.ask(
                self,
                "周度复盘与一键重置",
                msg,
                confirm_text="确定重置",
                is_danger=True
            ):
                parent.task_service.perform_weekly_reset()
                parent._update_stats_ui()
                parent._rebuild_cards()
                self.user_stats = parent.user_stats
                self.big_tasks = parent.big_tasks
                self._rebuild()

    # ---------- 账号数据 ----------
    def _build_account_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(12)

        # 等级卡
        rank_card = QGroupBox()
        rc = QVBoxLayout(rank_card)
        rc.setContentsMargins(14, 10, 14, 10)
        rc.setSpacing(6)

        name_lbl = QLabel(rank_name(self.user_stats.level))
        name_lbl.setObjectName("SectionTitle")
        rc.addWidget(name_lbl)

        level_lbl = QLabel(f"Lv.{self.user_stats.level}")
        level_lbl.setObjectName("DialogBody")
        rc.addWidget(level_lbl)

        xp_bar = QProgressBar()
        xp_bar.setRange(0, max(1, self.user_stats.next_level_xp))
        xp_bar.setValue(self.user_stats.current_xp)
        rc.addWidget(xp_bar)

        xp_lbl = QLabel(f"{self.user_stats.current_xp} / {self.user_stats.next_level_xp} XP")
        xp_lbl.setObjectName("MetaText")
        xp_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        rc.addWidget(xp_lbl)

        lay.addWidget(rank_card)

        # 汇总统计
        done_small = self.user_stats.total_small_tasks_done
        done_bigs = self.user_stats.total_big_tasks_done
        week_task_pomo = sum(t.pomo for b in self.big_tasks for t in b.tasks if t.done)

        stats_card = QGroupBox("任务汇总")
        stats_card.setMinimumHeight(196)
        sc = QVBoxLayout(stats_card)
        sc.setContentsMargins(14, 10, 14, 10)
        sc.setSpacing(6)
        rows = [
            ("累计获得经验", f"{self.user_stats.total_xp} XP"),
            ("小任务累计完成", f"{done_small} 次"),
            ("大任务累计攻克", f"{done_bigs} 次"),
            ("主线任务番茄", f"{self.user_stats.task_pomo_total} 🍅 (本周 {week_task_pomo})"),
            ("自由探索番茄", f"{self.user_stats.free_pomo_total} 🍅 (本周 {self.user_stats.free_pomo_week})"),
            ("历史总专注投入", f"{self.user_stats.total_pomo_history} 🍅"),
        ]
        for k, v in rows:
            hl = QHBoxLayout()
            lab = QLabel(k)
            lab.setObjectName("DialogBody")
            val = QLabel(v)
            val.setObjectName("DialogBody")
            hl.addWidget(lab)
            hl.addStretch()
            hl.addWidget(val)
            sc.addLayout(hl)
        lay.addWidget(stats_card)

        # 危险操作区
        danger_card = QGroupBox("危险区域")
        dc = QVBoxLayout(danger_card)
        dc.setContentsMargins(14, 10, 14, 10)
        dc.setSpacing(6)

        d_tip = QLabel("清空所有个人经验、等级与任务进度，恢复至初始默认数据。此操作不可撤销。")
        d_tip.setObjectName("DialogBody")
        d_tip.setWordWrap(True)
        dc.addWidget(d_tip)

        d_btn_row = QHBoxLayout()
        acc_reset_btn = QPushButton("清空并重置全部数据")
        acc_reset_btn.setObjectName("DangerBtn")
        acc_reset_btn.setFixedHeight(32)
        acc_reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        acc_reset_btn.setToolTip("点击弹出确认窗口，重置账号数据至初始状态")
        acc_reset_btn.clicked.connect(self._on_reset)
        d_btn_row.addWidget(acc_reset_btn)
        d_btn_row.addStretch()
        dc.addLayout(d_btn_row)
        lay.addWidget(danger_card)

        lay.addStretch()
        return page

    # ---------- 外观 ----------
    def _build_appearance_tab(self) -> QWidget:
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(0, 8, 0, 0)
        lay.setSpacing(12)

        opacity_card = QGroupBox("界面透明度")
        oc = QVBoxLayout(opacity_card)
        oc.setContentsMargins(14, 12, 14, 12)
        oc.setSpacing(8)

        oc.addWidget(QLabel("面板整体不透明度（拖动即时预览）："))

        row = QHBoxLayout()
        row.setSpacing(10)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(35, 100)
        self.opacity_slider.setValue(int(self.user_stats.window_opacity * 100))
        self.opacity_slider.valueChanged.connect(self._on_opacity_change)
        self.opacity_lbl = QLabel(f"{self.opacity_slider.value()}%")
        self.opacity_lbl.setObjectName("MetaText")
        self.opacity_lbl.setMinimumWidth(46)
        row.addWidget(self.opacity_slider, stretch=1)
        row.addWidget(self.opacity_lbl)
        oc.addLayout(row)

        tip = QLabel("100% = 完全纯色不透明，35% = 透出桌面背景")
        tip.setObjectName("EmptyState")
        oc.addWidget(tip)

        lay.addWidget(opacity_card)
        lay.addStretch()
        return page

    def _on_opacity_change(self, value: int):
        opacity = value / 100.0
        self.user_stats.window_opacity = opacity
        self.opacity_lbl.setText(f"{value}%")
        parent = self.parent()
        if parent is not None:
            if hasattr(parent, "_apply_opacity"):
                parent._apply_opacity()
            elif hasattr(parent, "setWindowOpacity"):
                parent.setWindowOpacity(opacity)

    # ---------- 操作 ----------
    def _add_big(self):
        from PySide6.QtCore import QTimer
        new_big = BigTask(f"b-{int(time.time()*1000)}", "新大任务")
        new_big.tasks.append(SmallTask(f"t-{int(time.time()*1000)}", "新小任务", day=0, pomo=1))
        self.big_tasks.append(new_big)
        self._rebuild()
        if hasattr(self, "tasks_scroll") and self.tasks_scroll:
            QTimer.singleShot(60, lambda: self.tasks_scroll.verticalScrollBar().setValue(
                self.tasks_scroll.verticalScrollBar().maximum()
            ))
        self._edit_big(new_big)

    def _delete_big(self, big: BigTask):
        from ui.icon_helper import clean_title_no_emoji
        title = clean_title_no_emoji(big.title)
        if ConfirmDialog.ask(
            self,
            "删除大任务",
            f"确定删除「{title}」及其所有小任务吗？\n\n此操作将同时移除该科目下的所有周排期任务。",
            confirm_text="删除",
            is_danger=True
        ):
            if big in self.big_tasks:
                self.big_tasks.remove(big)
                self._rebuild()

    def _edit_big(self, big: BigTask):
        dlg = BigTaskEditorDialog(big, self)
        dlg.exec()
        self._rebuild()

    def _on_save(self):
        self.settings_changed.emit()
        self.accept()

    def _on_reset(self):
        if ConfirmDialog.ask(
            self,
            "确认重置数据",
            "确定清空当前进度并恢复为默认示例数据吗？\n此操作不可撤销。",
            confirm_text="确认清空",
            is_danger=True
        ):
            self.reset_requested.emit()
            self.accept()