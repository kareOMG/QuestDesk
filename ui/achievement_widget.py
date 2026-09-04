from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QProgressBar
)
from PySide6.QtCore import Qt
from services.achievement_service import AchievementService
from ui.styles import ThemeManager


class AchievementBadgeCard(QFrame):
    """单张成就卡片"""

    def __init__(self, ach, parent=None):
        super().__init__(parent)
        self.ach = ach
        self.setObjectName("AchievementCardUnlocked" if ach.unlocked else "AchievementCardLocked")
        self._init_ui()

    def _init_ui(self):
        p = ThemeManager.palette()
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(14)

        # 徽章图标
        icon_box = QFrame()
        icon_box.setFixedSize(44, 44)
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        icon_lbl = QLabel(self.ach.icon if self.ach.unlocked else "🔒")
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 24px;")
        icon_lay.addWidget(icon_lbl)
        lay.addWidget(icon_box)

        # 文本信息
        info_lay = QVBoxLayout()
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(3)

        title_row = QHBoxLayout()
        title_lbl = QLabel(self.ach.name)
        title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #ece7e1;" if self.ach.unlocked
                                else f"font-size: 14px; font-weight: 600; color: {p['sub']};")
        cat_badge = QLabel(self.ach.category)
        cat_badge.setStyleSheet(f"font-size: 10px; padding: 2px 6px; border-radius: 4px; "
                                f"background-color: {p['selected']}; color: {p['accent_text']};")
        title_row.addWidget(title_lbl)
        title_row.addWidget(cat_badge)
        title_row.addStretch()
        info_lay.addLayout(title_row)

        desc_lbl = QLabel(self.ach.description)
        desc_lbl.setStyleSheet(f"font-size: 12px; color: {p['sub']};")
        desc_lbl.setWordWrap(True)
        info_lay.addWidget(desc_lbl)

        # 进度或解锁时间
        if self.ach.unlocked:
            time_lbl = QLabel(f"✓ 已解锁 · {self.ach.unlocked_at or '已达成'}")
            time_lbl.setStyleSheet("font-size: 11px; color: #b2a69a; font-weight: 500;")
            info_lay.addWidget(time_lbl)
        else:
            prog_row = QHBoxLayout()
            prog_bar = QProgressBar()
            prog_bar.setRange(0, self.ach.target_progress)
            prog_bar.setValue(self.ach.current_progress)
            prog_bar.setFixedHeight(5)
            prog_txt = QLabel(f"{self.ach.current_progress}/{self.ach.target_progress}")
            prog_txt.setStyleSheet(f"font-size: 11px; color: {p['sub']};")
            prog_row.addWidget(prog_bar, stretch=1)
            prog_row.addWidget(prog_txt)
            info_lay.addLayout(prog_row)

        lay.addLayout(info_lay, stretch=1)


class AchievementView(QWidget):
    """成就陈列室 / 荣誉墙面板"""

    def __init__(self, achievement_service: AchievementService, parent=None):
        super().__init__(parent)
        self.ach_service = achievement_service
        self._init_ui()

    def _init_ui(self):
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(10)

        # 顶部标头
        header = QHBoxLayout()
        unlocked = self.ach_service.get_unlocked_count()
        total = self.ach_service.get_total_count()
        title = QLabel("🏆 荣耀陈列室")
        title.setObjectName("SectionTitle")
        self.count_lbl = QLabel(f"已解锁 {unlocked} / {total}")
        self.count_lbl.setObjectName("MetaText")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.count_lbl)
        root_lay.addLayout(header)

        # 徽章卡片列表容器
        self.cards_box = QWidget()
        self.cards_layout = QVBoxLayout(self.cards_box)
        self.cards_layout.setContentsMargins(0, 4, 0, 4)
        self.cards_layout.setSpacing(8)
        root_lay.addWidget(self.cards_box)

        self.rebuild_achievements()

    def rebuild_achievements(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        unlocked_count = self.ach_service.get_unlocked_count()
        total_count = self.ach_service.get_total_count()
        self.count_lbl.setText(f"已解锁 {unlocked_count} / {total_count}")

        # 已解锁排在前面
        sorted_achs = sorted(self.ach_service.achievements, key=lambda a: (not a.unlocked, a.id))
        for ach in sorted_achs:
            card = AchievementBadgeCard(ach)
            self.cards_layout.addWidget(card)

        self.cards_layout.addStretch()
