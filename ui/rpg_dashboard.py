from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QScrollArea, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from services.task_service import TaskService
from ui.styles import ThemeManager
from models.task import DAYS
from config.constants import AttributeType, DAY_SUBTITLES


class DailyEventCard(QFrame):
    """单个今日冒险事件卡片（RPG包装 + 原任务说明 + 掉落奖励 + 勾选打卡）"""
    toggled = Signal(str, str, bool)  # (big_id, small_id, done)

    def __init__(self, event_data: dict, parent=None):
        super().__init__(parent)
        self.setObjectName("DailyEventCard")
        self.event_data = event_data
        self.task = event_data["task"]
        self._init_ui()

    def _init_ui(self):
        p = ThemeManager.palette()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(8)

        # 顶行：RPG 试炼事件名称 + 勾选按钮
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(10)

        self.check_btn = QPushButton()
        self.check_btn.setFixedSize(20, 20)
        self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.check_btn.clicked.connect(self._on_click)

        self.rpg_title_lbl = QLabel(self.event_data["rpg_event_title"])
        self.rpg_title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #ece7e1;")

        top_row.addWidget(self.check_btn)
        top_row.addWidget(self.rpg_title_lbl, stretch=1)

        # 所属科目胶囊标签
        cat_badge = QLabel(self.event_data["big_title"])
        cat_badge.setStyleSheet(
            f"font-size: 11px; padding: 2px 8px; border-radius: 6px; "
            f"background-color: {p['surface']}; border: 1px solid {p['border']}; color: {p['accent_text']};"
        )
        top_row.addWidget(cat_badge)
        lay.addLayout(top_row)

        # 中行：任务实际内容
        self.content_lbl = QLabel(f"◇ {self.task.title}")
        self.content_lbl.setStyleSheet(f"font-size: 13px; color: {p['sub']}; margin-left: 30px;")
        self.content_lbl.setWordWrap(True)
        lay.addWidget(self.content_lbl)

        # 底行：掉落奖励
        reward_row = QHBoxLayout()
        reward_row.setContentsMargins(30, 0, 0, 0)
        reward_lbl = QLabel(f"奖励: {self.event_data['reward_desc']} · {self.task.pomo} 🍅")
        reward_lbl.setStyleSheet(f"font-size: 11px; color: {p['accent']}; font-weight: 600;")
        reward_row.addWidget(reward_lbl)
        reward_row.addStretch()
        lay.addLayout(reward_row)

        self._apply_style()

    def _on_click(self):
        if self.task.done:
            return
        self.toggled.emit(self.event_data["big_id"], self.task.id, True)

    def _apply_style(self):
        p = ThemeManager.palette()
        if self.task.done:
            self.check_btn.setObjectName("TaskDotDone")
            self.check_btn.setText("✓")
            self.check_btn.setEnabled(False)
            self.check_btn.setCursor(Qt.CursorShape.ArrowCursor)
            self.check_btn.setToolTip("已完成")
            self.rpg_title_lbl.setStyleSheet(f"font-size: 14px; font-weight: 600; color: {p['sub']}; text-decoration: line-through;")
            self.content_lbl.setStyleSheet(f"font-size: 13px; color: {p['sub']}; text-decoration: line-through; margin-left: 30px;")
        else:
            self.check_btn.setObjectName("TaskDot")
            self.check_btn.setText("")
            self.check_btn.setEnabled(True)
            self.check_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.check_btn.setToolTip("点击完成任务（完成后不可取消）")
            self.rpg_title_lbl.setStyleSheet("font-size: 14px; font-weight: 700; color: #ece7e1;")
            self.content_lbl.setStyleSheet(f"font-size: 13px; color: {p['sub']}; margin-left: 30px;")
        self.check_btn.style().unpolish(self.check_btn)
        self.check_btn.style().polish(self.check_btn)


class RPGDashboard(QWidget):
    """
    全新 RPG 首页仪表盘：
    整合【角色状态卡】、【今日状态 (Focus/Growth)】、【今日冒险】与【本周成长属性沉淀】
    """
    task_toggled = Signal(str, str, bool)

    def __init__(self, task_service: TaskService, parent=None):
        super().__init__(parent)
        self.task_service = task_service
        self._init_ui()

    def _init_ui(self):
        root_lay = QVBoxLayout(self)
        root_lay.setContentsMargins(0, 0, 0, 0)
        root_lay.setSpacing(12)

        # 1. 角色 Hero 状态卡
        self.hero_card = self._build_hero_card()
        root_lay.addWidget(self.hero_card)

        # 2. 今日状态 (Focus / Growth)
        self.status_card = self._build_status_card()
        root_lay.addWidget(self.status_card)

        # 3. 自由探索专注资源投入卡
        self.exploration_card = self._build_free_exploration_card()
        root_lay.addWidget(self.exploration_card)

        # 4. 今日冒险标题
        today = self.task_service.get_today_weekday()
        adv_header = QHBoxLayout()
        adv_title = QLabel(f"⚔️ 今日冒险 · {DAYS[today]}（{DAY_SUBTITLES[today]}）")
        adv_title.setObjectName("SectionTitle")
        adv_header.addWidget(adv_title)
        adv_header.addStretch()
        root_lay.addLayout(adv_header)

        # 今日冒险事件列表容器
        self.events_box = QWidget()
        self.events_layout = QVBoxLayout(self.events_box)
        self.events_layout.setContentsMargins(0, 0, 0, 0)
        self.events_layout.setSpacing(8)
        root_lay.addWidget(self.events_box)

        # 5. 本周属性成长卡
        self.growth_card = self._build_growth_card()
        root_lay.addWidget(self.growth_card)

        self.rebuild_dashboard()

    def _build_hero_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("HeroCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(8)

        top_row = QHBoxLayout()
        self.hero_title = QLabel(f"Lv.{self.task_service.user_stats.level}  {self.task_service.user_stats.rank}")
        self.hero_title.setStyleSheet("font-size: 16px; font-weight: 800; color: #ece7e1;")

        self.streak_badge = QLabel(f"🔥 连胜 {self.task_service.user_stats.streak_days} 天")
        self.streak_badge.setStyleSheet(
            "font-size: 11px; font-weight: 700; color: #e5c07b; background-color: rgba(229, 192, 123, 0.15); "
            "padding: 3px 8px; border-radius: 6px;"
        )

        top_row.addWidget(self.hero_title)
        top_row.addStretch()
        top_row.addWidget(self.streak_badge)
        lay.addLayout(top_row)

        self.xp_bar = QProgressBar()
        self.xp_bar.setFixedHeight(12)
        lay.addWidget(self.xp_bar)

        xp_row = QHBoxLayout()
        self.xp_desc = QLabel("经验进度")
        self.xp_desc.setObjectName("MetaText")
        self.xp_num = QLabel(f"EXP {self.task_service.user_stats.current_xp} / {self.task_service.user_stats.next_level_xp}")
        self.xp_num.setObjectName("MetaText")
        xp_row.addWidget(self.xp_desc)
        xp_row.addStretch()
        xp_row.addWidget(self.xp_num)
        lay.addLayout(xp_row)

        return card

    def _build_status_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("StatusGridCard")
        lay = QHBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        # 1. 主线推进（任务番茄）
        task_box = QVBoxLayout()
        task_box.setSpacing(2)
        t_lbl = QLabel("⚔️ 任务推进")
        t_lbl.setObjectName("MetaText")
        t_lbl.setToolTip("今日已完成的主线/排期任务番茄投入与目标")
        self.task_pomo_val = QLabel("🍅 0/4")
        self.task_pomo_val.setStyleSheet("font-size: 15px; font-weight: 800; color: #ece7e1;")
        task_box.addWidget(t_lbl)
        task_box.addWidget(self.task_pomo_val)

        # 2. 自由探索（非排期学习）
        free_box = QVBoxLayout()
        free_box.setSpacing(2)
        fr_lbl = QLabel("🧭 自由探索")
        fr_lbl.setObjectName("MetaText")
        fr_lbl.setToolTip("今日计划外的自学、阅读与技术探索投入")
        self.free_pomo_val = QLabel("🍅 +0")
        self.free_pomo_val.setStyleSheet("font-size: 15px; font-weight: 800; color: #e5c07b;")
        free_box.addWidget(fr_lbl)
        free_box.addWidget(self.free_pomo_val)

        # 3. 专注总计（总学习投入）
        total_box = QVBoxLayout()
        total_box.setSpacing(2)
        tot_lbl = QLabel("📊 专注总计")
        tot_lbl.setObjectName("MetaText")
        tot_lbl.setToolTip("今日总专注资源投入（主线推进 + 自由探索）")
        self.total_pomo_val = QLabel("🍅 0")
        self.total_pomo_val.setStyleSheet("font-size: 15px; font-weight: 800; color: #b2a69a;")
        total_box.addWidget(tot_lbl)
        total_box.addWidget(self.total_pomo_val)

        # 4. 试炼攻克数
        growth_box = QVBoxLayout()
        growth_box.setSpacing(2)
        g_lbl = QLabel("🌱 试炼攻克")
        g_lbl.setObjectName("MetaText")
        g_lbl.setToolTip("今日已完成的小任务数量")
        self.growth_val = QLabel("+0 项")
        self.growth_val.setStyleSheet("font-size: 15px; font-weight: 800; color: #ded5c9;")
        growth_box.addWidget(g_lbl)
        growth_box.addWidget(self.growth_val)

        lay.addLayout(task_box)
        lay.addStretch()
        lay.addLayout(free_box)
        lay.addStretch()
        lay.addLayout(total_box)
        lay.addStretch()
        lay.addLayout(growth_box)
        return card

    def _build_free_exploration_card(self) -> QFrame:
        """自由探索打卡卡片：为计划外的自主学习、阅读、调研提供便捷的投入入口"""
        card = QFrame()
        card.setObjectName("ExplorationCard")
        lay = QHBoxLayout(card)
        lay.setContentsMargins(14, 10, 14, 10)
        lay.setSpacing(12)

        info_box = QVBoxLayout()
        info_box.setSpacing(2)

        title_row = QHBoxLayout()
        title = QLabel("🧭 自由探索 · 专注资源投入")
        title.setStyleSheet("font-size: 13px; font-weight: 700; color: #ece7e1;")
        tag = QLabel("计划外拓展")
        tag.setStyleSheet("font-size: 10px; color: #e5c07b; background-color: rgba(229,192,123,0.15); "
                          "padding: 1px 6px; border-radius: 4px; font-weight: 600;")
        title_row.addWidget(title)
        title_row.addWidget(tag)
        title_row.addStretch()
        info_box.addLayout(title_row)

        desc = QLabel("记录未排期的文献阅读、技术自学、偶发解题或拓展实践（+15 XP/🍅）")
        desc.setObjectName("MetaText")
        desc.setWordWrap(True)
        info_box.addWidget(desc)
        lay.addLayout(info_box, stretch=1)

        explore_btn = QPushButton("＋ 记录探索")
        explore_btn.setObjectName("PrimaryBtn")
        explore_btn.setFixedHeight(30)
        explore_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        explore_btn.clicked.connect(self._on_open_free_exploration)
        lay.addWidget(explore_btn)

        return card

    def _on_open_free_exploration(self):
        from ui.free_exploration_dialog import FreeExplorationDialog
        dlg = FreeExplorationDialog(self)
        if dlg.exec():
            res = dlg.get_result()
            self.task_service.log_free_exploration(res["pomos"], res["attribute"], res["topic"])
            self.rebuild_dashboard()

    def _build_growth_card(self) -> QFrame:
        card = QFrame()
        card.setObjectName("GrowthCard")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 14)
        lay.setSpacing(10)

        header = QLabel("📈 本周属性成长沉淀")
        header.setStyleSheet("font-size: 13px; font-weight: 700; color: #ece7e1;")
        lay.addWidget(header)

        self.attr_grid = QGridLayout()
        self.attr_grid.setSpacing(10)
        self.attr_labels = {}

        attrs = [AttributeType.MATH, AttributeType.CODING, AttributeType.ENGLISH,
                 AttributeType.PRACTICE, AttributeType.REVIEW]

        for i, name in enumerate(attrs):
            r, c = divmod(i, 2)
            chip = QFrame()
            chip.setObjectName("AttributeChip")
            chip_lay = QHBoxLayout(chip)
            chip_lay.setContentsMargins(10, 6, 10, 6)
            chip_title = QLabel(f"◇ {name}")
            chip_title.setStyleSheet("font-size: 12px; font-weight: 600; color: #ece7e1;")
            val_lbl = QLabel("+0")
            val_lbl.setStyleSheet("font-size: 12px; font-weight: 700; color: #b2a69a;")
            chip_lay.addWidget(chip_title)
            chip_lay.addStretch()
            chip_lay.addWidget(val_lbl)
            self.attr_labels[name] = val_lbl
            self.attr_grid.addWidget(chip, r, c)

        lay.addLayout(self.attr_grid)
        return card

    def rebuild_dashboard(self):
        """刷新看板的所有数据呈现"""
        stats = self.task_service.user_stats

        # 1. 刷新 Hero 卡
        self.hero_title.setText(f"Lv.{stats.level}  {stats.rank}")
        self.streak_badge.setText(f"🔥 连胜 {stats.streak_days} 天")
        self.xp_bar.setRange(0, max(1, stats.next_level_xp))
        self.xp_bar.setValue(stats.current_xp)
        self.xp_num.setText(f"EXP {stats.current_xp} / {stats.next_level_xp}")

        # 2. 刷新双轨学习投入状态值
        summary = self.task_service.get_today_focus_summary()
        g_cnt = self.task_service.get_today_growth_count()
        self.task_pomo_val.setText(f"🍅 {summary['task_done']}/{summary['task_target']}")
        self.free_pomo_val.setText(f"🍅 +{summary['free_done']}")
        self.total_pomo_val.setText(f"🍅 {summary['total_pomo']}")
        self.growth_val.setText(f"+{g_cnt} 项")

        # 3. 刷新今日事件列表
        while self.events_layout.count():
            item = self.events_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        events = self.task_service.get_today_event_tasks()
        if not events:
            empty = QLabel("今日所有试炼均已攻克，状态饱满，好好休息！")
            empty.setObjectName("EmptyState")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_layout.addWidget(empty)
        else:
            for ev in events:
                card = DailyEventCard(ev)
                card.toggled.connect(self.task_toggled.emit)
                self.events_layout.addWidget(card)

        # 4. 刷新本周成长属性值
        for name, lbl in self.attr_labels.items():
            pts = stats.weekly_attributes.get(name, 0)
            lbl.setText(f"+{pts}")
