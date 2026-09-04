from datetime import date, datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QProgressBar, QFrame, QGraphicsDropShadowEffect,
    QSystemTrayIcon, QMenu, QApplication, QMessageBox, QSizeGrip,
)
from PySide6.QtCore import Qt, QPoint, QRect, QRectF, QTimer, QEvent
from PySide6.QtGui import QCursor, QColor, QPainter, QPainterPath, QIcon, QPixmap

from ui.task_widget import BigTaskCard, SmallTaskRow
from ui.toast_dialog import LevelUpDialog, QuestCompleteDialog, AchievementUnlockDialog, ConfirmDialog
from ui.settings_dialog import SettingsDialog
from ui.rpg_dashboard import RPGDashboard
from ui.achievement_widget import AchievementView
from ui.styles import ThemeManager

from storage.json_storage import JSONStorage
from models.task import BigTask, DAYS
from models.user_stats import rank_name
from config.constants import DAY_SUBTITLES

from events.event_bus import (
    event_bus, TaskToggledEvent, LevelUpEvent, AchievementUnlockedEvent,
    StatsUpdatedEvent, WeeklyResetEvent
)
from services.backup_service import BackupService
from services.xp_service import XPService
from services.achievement_service import AchievementService
from services.task_service import TaskService


def clamp_unit(v):
    try:
        return max(0.35, min(1.0, float(v)))
    except (TypeError, ValueError):
        return 0.95


def _clear_layout(lay):
    """递归清理布局及其子布局、子控件，彻底避免跨视图残留孤儿控件"""
    while lay.count():
        item = lay.takeAt(0)
        if item.widget():
            item.widget().deleteLater()
        elif item.layout():
            _clear_layout(item.layout())


class FramelessGlassContainer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.opacity = 0.95

    def set_opacity(self, opacity: float):
        self.opacity = max(0.2, min(1.0, float(opacity)))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        path = QPainterPath()
        path.addRoundedRect(self.rect().adjusted(1, 1, -1, -1), 14, 14)

        r, g, b, _ = ThemeManager.glass()
        alpha = int(self.opacity * 255)
        painter.fillPath(path, QColor(r, g, b, alpha))

        pen = painter.pen()
        br, bg, bb, ba = ThemeManager.glass_border()
        border_alpha = min(255, int(ba * (self.opacity / 0.95)))
        pen.setColor(QColor(br, bg, bb, border_alpha))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.drawPath(path)


class BottomLeftGrip(QWidget):
    """左下角显式缩放手柄，支持鼠标拖拽向左/向下拉伸窗口"""

    def __init__(self, target_window: QWidget, parent=None):
        super().__init__(parent or target_window)
        self.target_window = target_window
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        self.setToolTip("拖拽缩放窗口（向左/向下拉伸）")
        self._dragging = False
        self._start_pos = QPoint()
        self._start_geo = QRect()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._start_pos = event.globalPosition().toPoint()
            self._start_geo = self.target_window.geometry()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._dragging and event.buttons() & Qt.MouseButton.LeftButton:
            gpos = event.globalPosition().toPoint()
            dx = gpos.x() - self._start_pos.x()
            dy = gpos.y() - self._start_pos.y()

            min_w = self.target_window.minimumWidth()
            min_h = self.target_window.minimumHeight()

            new_w = max(min_w, self._start_geo.width() - dx)
            new_x = self._start_geo.x() + (self._start_geo.width() - new_w)
            new_h = max(min_h, self._start_geo.height() + dy)

            geo = QRect(self._start_geo)
            geo.setX(new_x)
            geo.setWidth(new_w)
            geo.setHeight(new_h)
            self.target_window.setGeometry(geo)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._dragging = False
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(236, 231, 225, 65))
        # 绘制朝向左下角的精致三层阶梯点阵
        painter.drawEllipse(3, 11, 2, 2)
        painter.drawEllipse(7, 11, 2, 2)
        painter.drawEllipse(11, 11, 2, 2)
        painter.drawEllipse(3, 7, 2, 2)
        painter.drawEllipse(7, 7, 2, 2)
        painter.drawEllipse(3, 3, 2, 2)
        painter.end()


class FloatingWindow(QWidget):
    def __init__(self, storage: JSONStorage):
        super().__init__()
        self.storage = storage
        self.user_stats, self.big_tasks, achievements = storage.load_data()
        self.view = "adventure"  # adventure (首页RPG看板) | week (全周排期) | achievement (成就墙)

        # 初始化分层服务
        self.backup_service = BackupService(storage.filepath)
        self.xp_service = XPService(self.user_stats)
        self.achievement_service = AchievementService(achievements)
        self.task_service = TaskService(
            self.user_stats, self.big_tasks, self.storage,
            self.xp_service, self.achievement_service, self.backup_service
        )

        # 跨天检查
        self.task_service.check_cross_day()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint
                            | Qt.WindowType.WindowStaysOnTopHint
                            | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.resize(680, 560)
        self.setMinimumSize(540, 400)
        self.setMouseTracking(True)

        self._is_dragging = False
        self._drag_position = QPoint()
        self._resize_edge = None
        self._drag_start_pos = QPoint()
        self._drag_start_geo = QRect()
        self.BORDER_MARGIN = 8
        self.on_top = True

        self._init_ui()
        self._init_tray()
        self._apply_opacity()
        self._subscribe_events()
        self._update_stats_ui()

        # 每 60 秒检查一次跨天
        self._cross_day_timer = QTimer(self)
        self._cross_day_timer.timeout.connect(self._check_cross_day)
        self._cross_day_timer.start(60000)

    def _subscribe_events(self):
        """订阅全局业务事件，UI 响应弹窗与刷新"""
        event_bus.subscribe(LevelUpEvent, self._on_level_up_event)
        event_bus.subscribe(AchievementUnlockedEvent, self._on_achievement_unlocked_event)
        event_bus.subscribe(StatsUpdatedEvent, lambda ev: self._update_stats_ui())
        event_bus.subscribe(WeeklyResetEvent, lambda ev: self._rebuild_cards())

    def _on_level_up_event(self, ev: LevelUpEvent):
        LevelUpDialog(ev.new_level, self).exec()

    def _on_achievement_unlocked_event(self, ev: AchievementUnlockedEvent):
        AchievementUnlockDialog(ev.achievement.name, ev.achievement.description, ev.achievement.icon, self).exec()

    def _check_cross_day(self):
        self.task_service.check_cross_day()
        self._update_stats_ui()
        self._rebuild_cards()

    # ---------- UI 构建 ----------
    def _init_ui(self):
        ThemeManager.apply(QApplication.instance(), "dark")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)

        container = FramelessGlassContainer(self)
        self.container = container
        self.container.setMouseTracking(True)
        self.container.installEventFilter(self)
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 60))
        shadow.setOffset(0, 6)
        container.setGraphicsEffect(shadow)

        inner = QVBoxLayout()
        inner.setContentsMargins(0, 0, 0, 0)
        inner.setSpacing(0)
        inner.addWidget(self._build_header())

        body = QHBoxLayout()
        body.setContentsMargins(0, 0, 0, 0)
        body.setSpacing(0)
        body.addWidget(self._build_nav())
        body.addWidget(self._build_content(), stretch=1)
        inner.addLayout(body, stretch=1)

        container_layout.addLayout(inner)
        main_layout.addWidget(container)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)
        self.size_grip.setStyleSheet("background: transparent;")

        self.size_grip_bl = BottomLeftGrip(self)

        # 安装全局事件过滤器，彻底杜绝光标滞留在拉伸形状的问题
        QApplication.instance().installEventFilter(self)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "size_grip"):
            self.size_grip.move(self.width() - 22, self.height() - 22)
            self.size_grip.raise_()
        if hasattr(self, "size_grip_bl"):
            self.size_grip_bl.move(6, self.height() - 22)
            self.size_grip_bl.raise_()

    def leaveEvent(self, event):
        super().leaveEvent(event)
        if not self._resize_edge:
            self.unsetCursor()

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        lay = QHBoxLayout(header)
        lay.setContentsMargins(16, 12, 12, 6)
        lay.setSpacing(12)

        logo_title = QLabel("⚔️ QuestDesk")
        logo_title.setStyleSheet("font-size: 15px; font-weight: 800; color: #ece7e1;")
        lay.addWidget(logo_title)
        lay.addStretch()

        summary = self.task_service.get_week_focus_summary()
        self.pomo_lbl = QLabel(f"⚔️ 任务 🍅 {summary['task_done']}/{summary['task_target']}  ·  🧭 探索 🍅 +{summary['free_done']}")
        self.pomo_lbl.setObjectName("PomoBadge")
        self.pomo_lbl.setToolTip(f"本周专注投入总计: 🍅 {summary['total_pomo']} (主线攻坚 {summary['task_done']} + 自由探索 {summary['free_done']})")
        lay.addWidget(self.pomo_lbl)

        self.edit_btn = QPushButton("设置")
        self.edit_btn.setObjectName("GhostBtn")
        self.edit_btn.clicked.connect(self._on_open_settings)
        lay.addWidget(self.edit_btn)

        self.close_btn = QPushButton("X")
        self.close_btn.setObjectName("CloseBtn")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setToolTip("隐藏到托盘")
        self.close_btn.clicked.connect(self.hide)
        lay.addWidget(self.close_btn)

        return header

    def _build_nav(self) -> QFrame:
        self.nav = QFrame()
        self.nav.setObjectName("NavPanel")
        self.nav.setFixedWidth(64)
        nav_lay = QVBoxLayout(self.nav)
        nav_lay.setContentsMargins(6, 8, 6, 8)
        nav_lay.setSpacing(6)

        self.adv_btn = QPushButton("冒险")
        self.week_btn = QPushButton("排期")
        self.ach_btn = QPushButton("成就")

        self.adv_btn.setObjectName("NavBtnActive")
        self.adv_btn.clicked.connect(lambda: self._switch_view("adventure"))

        self.week_btn.setObjectName("NavBtn")
        self.week_btn.clicked.connect(lambda: self._switch_view("week"))

        self.ach_btn.setObjectName("NavBtn")
        self.ach_btn.clicked.connect(lambda: self._switch_view("achievement"))

        nav_lay.addWidget(self.adv_btn)
        nav_lay.addWidget(self.week_btn)
        nav_lay.addWidget(self.ach_btn)
        nav_lay.addStretch()
        return self.nav

    def _build_content(self) -> QWidget:
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(14, 8, 14, 12)
        content_layout.setSpacing(8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; } QScrollArea > QWidget > QWidget { background: transparent; }")

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(10)
        self._rebuild_cards()
        scroll.setWidget(self.scroll_content)
        content_layout.addWidget(scroll, stretch=1)
        return content

    # ---------- 渲染 ----------
    def _rebuild_cards(self):
        _clear_layout(self.scroll_layout)

        if self.view == "adventure":
            # 首页：全新 RPG 沉浸看板 (角色状态 + Focus/Growth + 今日试炼 + 本周成长)
            dashboard = RPGDashboard(self.task_service)
            dashboard.task_toggled.connect(self._on_task_toggled)
            self.scroll_layout.addWidget(dashboard)

        elif self.view == "week":
            self._build_week()

        elif self.view == "achievement":
            # 成就徽章墙
            ach_view = AchievementView(self.achievement_service)
            self.scroll_layout.addWidget(ach_view)

        self.scroll_layout.addStretch()

    def _build_week(self):
        """按周一~周日展示全周所有小任务（含今天高亮标记、一键周度复盘重置）"""
        today = datetime.today().weekday()

        bar_widget = QWidget()
        bar_layout = QHBoxLayout(bar_widget)
        bar_layout.setContentsMargins(4, 2, 4, 6)
        summary = self.task_service.get_week_focus_summary()
        info = QLabel(f"全周排期攻坚 🍅 {summary['task_done']}/{summary['task_target']}　·　自由探索 🍅 +{summary['free_done']}　·　总投入 🍅 {summary['total_pomo']}")
        info.setObjectName("MetaText")
        info.setStyleSheet("font-size: 12px; font-weight: 600; color: #ded5c9;")
        weekly_reset_btn = QPushButton("周度复盘与一键重置")
        weekly_reset_btn.setObjectName("GhostBtn")
        weekly_reset_btn.setToolTip("重置本周所有小任务的勾选状态，保留任务结构与排期")
        weekly_reset_btn.clicked.connect(self._on_weekly_reset)
        bar_layout.addWidget(info)
        bar_layout.addStretch()
        bar_layout.addWidget(weekly_reset_btn)
        self.scroll_layout.addWidget(bar_widget)

        day_tasks = {d: [] for d in range(7)}
        unplanned = []
        for big in self.big_tasks:
            for task in big.tasks:
                (day_tasks[task.day] if task.day is not None else unplanned).append((big, task))

        for d in range(7):
            panel = QFrame()
            panel.setObjectName("DayPanel")
            pl = QVBoxLayout(panel)
            pl.setContentsMargins(10, 8, 10, 10)
            pl.setSpacing(2)

            tag = "　今天" if d == today else ""
            achieved = sum(task.pomo for _, task in day_tasks[d] if task.done)
            target = sum(task.pomo for _, task in day_tasks[d])
            head = QLabel(f"{DAYS[d]}{tag}　{DAY_SUBTITLES[d]}　·　🍅 {achieved}/{target}")
            head.setObjectName("DayHeader")
            pl.addWidget(head)

            tasks = day_tasks[d]
            if not tasks:
                no = QLabel("暂无安排，休息或机动")
                no.setObjectName("EmptyState")
                no.setAlignment(Qt.AlignmentFlag.AlignCenter)
                pl.addWidget(no)
            def _bind_toggle(bi, tid):
                return lambda done=True: self._on_task_toggled(bi, tid, done)

            for big, task in tasks:
                row = SmallTaskRow(task)
                row.toggled.connect(_bind_toggle(big.id, task.id))
                pl.addWidget(row)

            self.scroll_layout.addWidget(panel)

        if unplanned:
            panel = QFrame()
            panel.setObjectName("DayPanel")
            pl = QVBoxLayout(panel)
            pl.setContentsMargins(10, 8, 10, 10)
            pl.setSpacing(2)
            head = QLabel("未排期任务")
            head.setObjectName("DayHeader")
            pl.addWidget(head)
            for big, task in unplanned:
                row = SmallTaskRow(task)
                row.toggled.connect(_bind_toggle(big.id, task.id))
                pl.addWidget(row)
            self.scroll_layout.addWidget(panel)

    def _switch_view(self, view: str):
        if view == self.view:
            return
        self.view = view
        states = [("adv_btn", "adventure"), ("week_btn", "week"), ("ach_btn", "achievement")]
        for attr, name in states:
            btn = getattr(self, attr)
            btn.setObjectName("NavBtnActive" if view == name else "NavBtn")
            btn.style().unpolish(btn)
            btn.style().polish(btn)
        self._rebuild_cards()

    # ---------- 交互逻辑 ----------
    def _on_task_toggled(self, big_id: str, task_id: str, done: bool):
        found, is_big_completed = self.task_service.toggle_task(big_id, task_id, done)
        if not found:
            return

        self._update_stats_ui()
        self._rebuild_cards()

        if is_big_completed:
            big, _ = self.task_service._find_task(big_id, task_id)
            if big:
                QuestCompleteDialog(big.title, big.total, False, self.user_stats.level, self).exec()

    def _on_weekly_reset(self):
        summary = self.task_service.get_week_focus_summary()
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
            self.task_service.perform_weekly_reset()
            self._update_stats_ui()
            self._rebuild_cards()

    def _update_stats_ui(self):
        summary = self.task_service.get_week_focus_summary()
        self.pomo_lbl.setText(f"⚔️ 任务 🍅 {summary['task_done']}/{summary['task_target']}  ·  🧭 探索 🍅 +{summary['free_done']}")
        self.pomo_lbl.setToolTip(f"本周专注投入总计: 🍅 {summary['total_pomo']} (主线攻坚 {summary['task_done']} + 自由探索 {summary['free_done']})")

    # ---------- 设置 / 托盘 / 窗口管理 ----------
    def _on_open_settings(self):
        dialog = SettingsDialog(self.user_stats, self.big_tasks, self.storage, self)
        dialog.settings_changed.connect(self.on_settings_updated)
        dialog.reset_requested.connect(self._on_reset_data)
        dialog.exec()

    def _apply_opacity(self):
        o = clamp_unit(self.user_stats.window_opacity)
        if hasattr(self, "container"):
            self.container.set_opacity(o)
        self.setWindowOpacity(1.0)

    def on_settings_updated(self):
        self._update_stats_ui()
        self._apply_opacity()
        self._rebuild_cards()
        self.task_service.save()

    def _on_reset_data(self):
        self.user_stats, self.big_tasks, achievements = self.storage.reset_data()
        self.xp_service.user_stats = self.user_stats
        self.achievement_service.achievements = achievements
        self.task_service.user_stats = self.user_stats
        self.task_service.big_tasks = self.big_tasks

        ThemeManager.apply(QApplication.instance(), "dark")
        self.container.update()
        self._update_stats_ui()
        self._apply_opacity()
        self._rebuild_cards()

    def _create_app_icon(self) -> QIcon:
        size = 64
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor("#7d8a95"))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(4, 4, size - 8, size - 8), 14, 14)
        painter.setPen(QColor("white"))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawLine(22, 34, 28, 40)
        painter.drawLine(28, 40, 42, 26)
        painter.end()
        return QIcon(pixmap)

    def _init_tray(self):
        self.tray = QSystemTrayIcon(self._create_app_icon(), self)
        self.tray.setToolTip("QuestDesk 冒险终端")

        menu = QMenu()
        menu.addAction("打开冒险终端").triggered.connect(self._show_from_tray)
        menu.addAction("隐藏终端").triggered.connect(self.hide)
        menu.addSeparator()
        menu.addAction("周度复盘与一键重置").triggered.connect(self._on_weekly_reset)
        menu.addSeparator()
        self.tray_top_action = menu.addAction("窗口置顶")
        self.tray_top_action.setCheckable(True)
        self.tray_top_action.setChecked(self.on_top)
        self.tray_top_action.toggled.connect(self._set_always_on_top)
        menu.addSeparator()
        menu.addAction("退出").triggered.connect(lambda: QApplication.quit())

        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self._on_tray_activated)
        if QSystemTrayIcon.isSystemTrayAvailable():
            self.tray.show()

    def _show_from_tray(self):
        self.show()
        self.raise_()
        self.activateWindow()

    def _on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self._show_from_tray()

    def _set_always_on_top(self, on_top: bool):
        self.on_top = on_top
        flags = self.windowFlags()
        if on_top:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        else:
            flags &= ~Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        self.show()
        self.raise_()
        self.activateWindow()

    # ---------- 窗口边缘全向拉伸与拖动 ----------
    def _determine_edge(self, gpos: QPoint) -> str:
        geo = self.frameGeometry()
        x = gpos.x() - geo.x()
        y = gpos.y() - geo.y()
        w = geo.width()
        h = geo.height()
        m = self.BORDER_MARGIN

        on_left = (x <= m)
        on_right = (x >= w - m)
        on_top = (y <= m)
        on_bottom = (y >= h - m)

        if on_top and on_left: return "top-left"
        if on_top and on_right: return "top-right"
        if on_bottom and on_left: return "bottom-left"
        if on_bottom and on_right: return "bottom-right"
        if on_left: return "left"
        if on_right: return "right"
        if on_top: return "top"
        if on_bottom: return "bottom"
        return ""

    def _update_edge_cursor(self, edge: str):
        mapping = {
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "top-left": Qt.CursorShape.SizeFDiagCursor,
            "bottom-right": Qt.CursorShape.SizeFDiagCursor,
            "top-right": Qt.CursorShape.SizeBDiagCursor,
            "bottom-left": Qt.CursorShape.SizeBDiagCursor,
        }
        if edge in mapping:
            self.setCursor(QCursor(mapping[edge]))
        else:
            self.unsetCursor()

    def eventFilter(self, obj, event):
        if isinstance(obj, QWidget) and (obj == self or self.isAncestorOf(obj)):
            t = event.type()
            if t == QEvent.Type.MouseMove:
                gpos = event.globalPosition().toPoint()
                if self._resize_edge and event.buttons() & Qt.MouseButton.LeftButton:
                    self._apply_resize(gpos)
                    return True
                if not self._resize_edge:
                    edge = self._determine_edge(gpos)
                    resize_shapes = (
                        Qt.CursorShape.SizeHorCursor, Qt.CursorShape.SizeVerCursor,
                        Qt.CursorShape.SizeFDiagCursor, Qt.CursorShape.SizeBDiagCursor
                    )
                    if edge:
                        self._update_edge_cursor(edge)
                    elif self.cursor().shape() in resize_shapes:
                        self.unsetCursor()
            elif t == QEvent.Type.MouseButtonPress and event.button() == Qt.MouseButton.LeftButton:
                gpos = event.globalPosition().toPoint()
                edge = self._determine_edge(gpos)
                if edge:
                    self._resize_edge = edge
                    self._drag_start_pos = gpos
                    self._drag_start_geo = self.geometry()
                    return True
            elif t == QEvent.Type.MouseButtonRelease:
                if self._resize_edge:
                    self._resize_edge = None
                    self.unsetCursor()
                    return True
            elif t == QEvent.Type.Leave and obj == self:
                if not self._resize_edge:
                    self.unsetCursor()
        return super().eventFilter(obj, event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            gpos = event.globalPosition().toPoint()
            edge = self._determine_edge(gpos)
            if edge:
                self._resize_edge = edge
                self._drag_start_pos = gpos
                self._drag_start_geo = self.geometry()
            else:
                self._is_dragging = True
                self._drag_position = gpos - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        gpos = event.globalPosition().toPoint()
        if self._resize_edge and event.buttons() & Qt.MouseButton.LeftButton:
            self._apply_resize(gpos)
            event.accept()
        elif self._is_dragging and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(gpos - self._drag_position)
            event.accept()
        else:
            edge = self._determine_edge(gpos)
            self._update_edge_cursor(edge)

    def mouseReleaseEvent(self, event):
        self._resize_edge = None
        self._is_dragging = False
        self.unsetCursor()
        event.accept()

    def _apply_resize(self, gpos: QPoint):
        dx = gpos.x() - self._drag_start_pos.x()
        dy = gpos.y() - self._drag_start_pos.y()
        geo = QRect(self._drag_start_geo)
        min_w = self.minimumWidth()
        min_h = self.minimumHeight()

        if "right" in self._resize_edge:
            new_w = max(min_w, self._drag_start_geo.width() + dx)
            geo.setWidth(new_w)
        if "bottom" in self._resize_edge:
            new_h = max(min_h, self._drag_start_geo.height() + dy)
            geo.setHeight(new_h)
        if "left" in self._resize_edge:
            new_w = max(min_w, self._drag_start_geo.width() - dx)
            new_x = self._drag_start_geo.x() + (self._drag_start_geo.width() - new_w)
            geo.setX(new_x)
            geo.setWidth(new_w)
        if "top" in self._resize_edge:
            new_h = max(min_h, self._drag_start_geo.height() - dy)
            new_y = self._drag_start_geo.y() + (self._drag_start_geo.height() - new_h)
            geo.setY(new_y)
            geo.setHeight(new_h)

        self.setGeometry(geo)