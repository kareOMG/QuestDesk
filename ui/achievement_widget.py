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

        is_secret = (self.ach.category == "彩蛋")
        is_unlocked = self.ach.unlocked

        # 徽章图标
        icon_box = QFrame()
        icon_box.setFixedSize(44, 44)
        icon_lay = QVBoxLayout(icon_box)
        icon_lay.setContentsMargins(0, 0, 0, 0)
        
        if is_unlocked:
            display_icon = self.ach.icon
        elif is_secret:
            display_icon = "❓"
        else:
            display_icon = "🔒"

        icon_lbl = QLabel(display_icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 24px;")
        icon_lay.addWidget(icon_lbl)
        lay.addWidget(icon_box)

        # 文本信息
        info_lay = QVBoxLayout()
        info_lay.setContentsMargins(0, 0, 0, 0)
        info_lay.setSpacing(3)

        title_row = QHBoxLayout()
        if is_unlocked:
            display_title = self.ach.name
            title_style = "font-size: 14px; font-weight: 700; color: #ece7e1;"
        elif is_secret:
            display_title = "？？？（隐藏探索）"
            title_style = "font-size: 14px; font-weight: 600; color: #eab308;"
        else:
            display_title = self.ach.name
            title_style = f"font-size: 14px; font-weight: 600; color: {p['sub']};"

        title_lbl = QLabel(display_title)
        title_lbl.setStyleSheet(title_style)

        # 分类徽标着色
        cat_badge = QLabel(self.ach.category)
        cat_colors = {
            "彩蛋": "background-color: rgba(234, 179, 8, 0.18); color: #fbbf24; border: 1px solid rgba(251, 191, 36, 0.35);",
            "成长": "background-color: rgba(168, 85, 247, 0.18); color: #c084fc; border: 1px solid rgba(192, 132, 252, 0.35);",
            "专注": "background-color: rgba(249, 115, 22, 0.18); color: #fb923c; border: 1px solid rgba(251, 146, 60, 0.35);",
            "学术": "background-color: rgba(59, 130, 246, 0.18); color: #60a5fa; border: 1px solid rgba(96, 165, 250, 0.35);",
            "战役": "background-color: rgba(239, 68, 68, 0.18); color: #f87171; border: 1px solid rgba(248, 113, 113, 0.35);",
            "坚韧": "background-color: rgba(34, 197, 94, 0.18); color: #4ade80; border: 1px solid rgba(74, 222, 128, 0.35);",
            "心智": "background-color: rgba(148, 163, 184, 0.18); color: #cbd5e1; border: 1px solid rgba(203, 213, 225, 0.35);",
            "起步": "background-color: rgba(120, 113, 108, 0.18); color: #d6d3d1; border: 1px solid rgba(214, 211, 209, 0.35);",
        }
        badge_style = cat_colors.get(self.ach.category, f"background-color: {p['selected']}; color: {p['accent_text']};")
        cat_badge.setStyleSheet(f"font-size: 10px; font-weight: 600; padding: 2px 7px; border-radius: 4px; {badge_style}")
        title_row.addWidget(title_lbl)
        title_row.addWidget(cat_badge)
        title_row.addStretch()
        info_lay.addLayout(title_row)

        if is_unlocked:
            display_desc = self.ach.description
            desc_style = f"font-size: 12px; color: {p['sub']};"
        elif is_secret:
            display_desc = getattr(self.ach, "clue", "") or "这是一个隐藏的彩蛋成就，完成特定探索即可揭晓..."
            desc_style = "font-size: 12px; color: #a3998e; font-style: italic;"
        else:
            display_desc = self.ach.description
            desc_style = f"font-size: 12px; color: {p['sub']};"

        desc_lbl = QLabel(display_desc)
        desc_lbl.setStyleSheet(desc_style)
        desc_lbl.setWordWrap(True)
        info_lay.addWidget(desc_lbl)

        # 进度或解锁时间
        if is_unlocked:
            time_lbl = QLabel(f"✓ 已解锁 · {self.ach.unlocked_at or '已达成'}")
            time_lbl.setStyleSheet("font-size: 11px; color: #b2a69a; font-weight: 500;")
            info_lay.addWidget(time_lbl)
        elif is_secret:
            hint_lbl = QLabel("神秘线索 · 静候触发")
            hint_lbl.setStyleSheet("font-size: 11px; color: #8c8278;")
            info_lay.addWidget(hint_lbl)
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
