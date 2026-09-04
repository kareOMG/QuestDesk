""": 单主题「暖炭磨砂玻璃」泛美学，全局去蓝。

固定深色暖炭玻璃 + 暖白文字，强调色为柔和石棕，杜绝蓝调与刺眼的白。
"""


def _base(P):
    return f"""
* {{
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI",
                 Roboto, "Microsoft YaHei", "PingFang SC", sans-serif;
    color: {P['text']};
}}

QWidget#CentralWidget, QDialog {{
    background: transparent;
}}

/* ---- 弹窗卡片（彻底不透明，防止下层内容重叠穿透） ---- */
QFrame#DialogCard {{
    background-color: {P['dialog']};
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
}}

/* ---- 文本层级 ---- */
QLabel#RankTitle {{ color: {P['text']}; font-size: 14px; font-weight: 700; }}
QLabel#LevelLabel {{ color: {P['accent_text']}; font-size: 12px; font-weight: 600; }}
QLabel#BigTitle {{ color: {P['text']}; font-size: 15px; font-weight: 600; }}
QLabel#BigHeader {{ color: {P['accent_text']}; font-size: 12px; font-weight: 700; }}
QLabel#SectionTitle {{ color: {P['text']}; font-size: 16px; font-weight: 700; }}
QLabel#GroupHeader {{ color: {P['sub']}; font-size: 12px; font-weight: 600; }}
QLabel#DialogTitle {{ color: {P['text']}; font-size: 16px; font-weight: 700; }}
QLabel#DialogBody {{ color: {P['sub']}; font-size: 13px; }}
QLabel#EmptyState {{ color: {P['sub']}; font-size: 13px; padding: 20px 0; }}
QLabel#FieldLabel {{ color: {P['sub']}; font-size: 12px; font-weight: 500; }}
QLabel#MetaText {{ color: {P['sub']}; font-size: 11px; }}
QLabel#PomoBadge {{
    color: {P['accent']}; font-size: 12px; font-weight: 700;
    background-color: {P['selected']};
    padding: 3px 10px; border-radius: 9px;
}}

/* ---- 进度条 ---- */
QProgressBar {{
    border: none; border-radius: 6px; background-color: #3f3d3c;
    text-align: center; color: transparent;
}}
QProgressBar::chunk {{ background-color: {P['accent']}; border-radius: 6px; }}


/* ---- 大任务卡片 ---- */
QFrame#BigCard {{
    background-color: {P['surface']};
    border: 1px solid {P['border']};
    border-radius: 14px;
}}

/* 设置面板中的大任务卡片与胶囊垫底背景 */
QFrame#BigTaskSettingCard {{
    background-color: {P['surface']};
    border: 1px solid {P['border']};
    border-radius: 12px;
}}
QFrame#TaskTitleCapsule {{
    background-color: rgba(255, 255, 255, 0.08);
    border: 1px solid {P['border']};
    border-radius: 13px;
}}
QLabel#CapsuleTitle {{
    color: {P['text']};
    font-size: 13px;
    font-weight: 700;
}}
QLabel#CapsuleCount {{
    color: {P['accent_text']};
    font-size: 11px;
    font-weight: 600;
}}

/* 小任务行 */
QWidget#TaskRow {{ background: transparent; }}
QPushButton#TaskDot {{
    background-color: transparent;
    border: 1px solid {P['dot']};
    border-radius: 9px;
}}
QPushButton#TaskDot:hover {{ border-color: {P['text']}; background-color: {P['hover']}; }}
QPushButton#TaskDotDone {{
    background-color: {P['accent']};
    border: none; border-radius: 9px;
    color: #2b2927; font-size: 9px; font-weight: 800;
}}
QLabel#TaskTitle {{ color: {P['text']}; font-size: 13px; }}
QLabel#TaskTitleDone {{
    color: {P['sub']};
    font-size: 13px;
    text-decoration: line-through;
}}

/* ---- 左侧导航（半透明，融入玻璃背景） ---- */
QFrame#NavPanel {{
    background-color: {P['nav']};
    border-right: 1px solid {P['border']};
}}
QPushButton#NavBtn {{
    background-color: transparent;
    border: none; border-radius: 8px;
    padding: 10px 8px;
    font-size: 12px; color: {P['nav_idle']};
    text-align: center;
}}
QPushButton#NavBtn:hover {{ background-color: {P['hover']}; color: {P['text']}; }}
QPushButton#NavBtnActive {{
    background-color: {P['selected']};
    border: none; border-radius: 8px;
    padding: 10px 8px;
    font-size: 12px; color: {P['accent_text']};
    font-weight: 600; text-align: center;
}}

/* ---- 滚动条 ---- */
QScrollBar:vertical {{
    border: none; background: transparent; width: 6px; margin: 0 2px 0 0;
}}
QScrollBar::handle:vertical {{
    background-color: {P['track']}; min-height: 24px; border-radius: 3px;
}}
QScrollBar::handle:vertical:hover {{ background-color: {P['hover']}; }}

/* ---- 按钮 ---- */
QPushButton {{
    background-color: {P['button']};
    color: {P['text']};
    border: 1px solid {P['border']};
    border-radius: 6px; padding: 5px 10px; font-size: 12px;
}}
QPushButton:hover {{ background-color: {P['hover']}; }}
QPushButton:pressed {{ background-color: {P['pressed']}; }}

QPushButton#PrimaryBtn {{
    background-color: {P['primary']};
    color: {P['primary_text']};
    border: 1px solid rgba(255, 255, 255, 0.18);
    border-radius: 7px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 700;
}}
QPushButton#PrimaryBtn:hover {{
    background-color: #a89c8f;
    border-color: rgba(255, 255, 255, 0.38);
    color: #ffffff;
}}
QPushButton#PrimaryBtn:pressed {{
    background-color: #786f63;
}}

QPushButton#GhostBtn {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 7px;
    padding: 6px 14px;
    color: rgba(236, 231, 225, 0.78);
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#GhostBtn:hover {{
    color: #ffffff;
    background-color: rgba(255, 255, 255, 0.12);
    border-color: rgba(255, 255, 255, 0.25);
}}
QPushButton#GhostBtn:pressed {{
    background-color: rgba(255, 255, 255, 0.08);
}}

QPushButton#CloseBtn {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 6px;
    padding: 0px;
    margin: 0px;
    color: rgba(236, 231, 225, 0.75);
    font-size: 13px;
    font-weight: bold;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
    text-align: center;
}}
QPushButton#CloseBtn:hover {{
    color: #ffffff;
    background-color: rgba(239, 68, 68, 0.75);
    border-color: rgba(239, 68, 68, 0.90);
}}
QPushButton#CloseBtn:pressed {{
    background-color: rgba(220, 38, 38, 0.90);
    color: #ffffff;
}}

QPushButton#DangerBtn {{
    color: {P['danger']};
    border: 1px solid {P['danger_border']};
    background-color: rgba(224, 149, 143, 0.06);
    border-radius: 7px;
    padding: 6px 14px;
    font-size: 12px;
    font-weight: 500;
}}
QPushButton#DangerBtn:hover {{
    background-color: {P['danger_hover']};
    border-color: {P['danger']};
}}

QPushButton#DangerIconBtn {{
    color: {P['danger']};
    border: 1px solid {P['danger_border']};
    background-color: rgba(224, 149, 143, 0.06);
    border-radius: 6px;
    padding: 0px;
    font-size: 13px;
    font-weight: bold;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Microsoft YaHei", sans-serif;
    text-align: center;
}}
QPushButton#DangerIconBtn:hover {{
    background-color: {P['danger_hover']};
    border-color: {P['danger']};
    color: #ffffff;
}}

/* ---- 输入 / 下拉 / 分组 ---- */
QLineEdit, QComboBox {{
    background-color: {P['input']};
    border: 1px solid {P['border']};
    border-radius: 6px; padding: 4px 8px; font-size: 13px; min-height: 20px;
}}
QLineEdit:focus, QComboBox:focus {{ border-color: {P['accent']}; }}
QComboBox::drop-down {{
    border: none; width: 18px; margin: 0; background: transparent;
}}
QComboBox QAbstractItemView {{
    background-color: {P['menu_bg']}; color: {P['menu_text']};
    border: 1px solid {P['border']}; border-radius: 6px;
    selection-background-color: {P['selected']};
    selection-color: {P['text']}; outline: none;
}}

/* ---- 高可用数字步进控件（彻底消除 I-beam 光标与无响应感） ---- */
QPushButton#StepperBtn {{
    background-color: {P['button']};
    border: 1px solid {P['border']};
    border-radius: 5px;
    color: {P['text']};
    font-size: 13px;
    font-weight: 700;
    padding: 0;
}}
QPushButton#StepperBtn:hover {{
    background-color: {P['hover']};
    border-color: {P['accent']};
    color: #ffffff;
}}
QPushButton#StepperBtn:pressed {{
    background-color: {P['pressed']};
}}

QLineEdit#StepperEdit {{
    background-color: {P['input']};
    border: 1px solid {P['border']};
    border-radius: 5px;
    color: {P['text']};
    font-size: 12px;
    font-weight: 600;
    padding: 2px 4px;
    min-height: 20px;
}}
QLineEdit#StepperEdit:focus {{
    border-color: {P['accent']};
}}

QSpinBox, QDoubleSpinBox {{
    background-color: {P['input']};
    border: 1px solid {P['border']};
    border-radius: 6px;
    padding: 3px 20px 3px 8px;
    font-size: 13px;
    min-height: 20px;
}}
QSpinBox:focus, QDoubleSpinBox:focus {{ border-color: {P['accent']}; }}
QSpinBox::up-button, QDoubleSpinBox::up-button {{
    subcontrol-origin: border;
    subcontrol-position: top right;
    width: 18px;
    border-left: 1px solid {P['border']};
    border-bottom: 1px solid {P['border']};
    background-color: {P['button']};
    border-top-right-radius: 5px;
}}
QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
    background-color: {P['hover']};
    border-left-color: {P['accent']};
}}
QSpinBox::down-button, QDoubleSpinBox::down-button {{
    subcontrol-origin: border;
    subcontrol-position: bottom right;
    width: 18px;
    border-left: 1px solid {P['border']};
    background-color: {P['button']};
    border-bottom-right-radius: 5px;
}}
QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
    background-color: {P['hover']};
    border-left-color: {P['accent']};
}}

/* ---- 选项卡（设置窗口） ---- */
QTabWidget::pane {{ border: none; background: transparent; }}

/* 滚动区透明化：磨砂玻璃内滚动不留底色/鬼影 */
QScrollArea {{ background: transparent; border: none; }}
QScrollArea > QWidget > QWidget {{ background: transparent; }}
QTabBar::tab {{
    background: transparent; color: {P['sub']};
    padding: 6px 14px; margin-right: 4px;
    border-bottom: 2px solid transparent; font-size: 13px;
}}
QTabBar::tab:selected {{ color: {P['text']}; font-weight: 600; border-bottom: 2px solid {P['accent']}; }}
QTabBar::tab:hover {{ color: {P['text']}; }}

QLabel#DayHeader {{
    color: {P['accent_text']}; font-size: 12px; font-weight: 700;
    padding: 6px 8px 2px 8px; border-bottom: 1px solid {P['border']};
}}
QFrame#DayPanel {{
    background-color: {P['surface']};
    border: 1px solid {P['border']};
    border-radius: 12px;
}}

QGroupBox {{
    background-color: {P['surface']};
    border: 1px solid {P['border']};
    border-radius: 10px; margin-top: 12px;
    padding: 6px 10px 10px 10px;
    font-size: 13px; font-weight: 600; color: {P['text']};
}}
QGroupBox::title {{
    subcontrol-origin: margin; subcontrol-position: top left;
    left: 12px; padding: 0 4px;
}}

QCheckBox {{ spacing: 8px; font-size: 13px; color: {P['text']}; }}
QCheckBox::indicator {{
    width: 16px; height: 16px; border-radius: 4px;
    border: 1px solid {P['dot']}; background: transparent;
}}
QCheckBox::indicator:checked {{ background-color: {P['accent']}; border-color: {P['accent']}; }}

/* 外观页的选择卡 */
QFrame#ChoiceRow {{
    background-color: {P['surface']};
    border: 1px solid {P['border']};
    border-radius: 10px;
}}
QFrame#ChoiceRowActive {{
    background-color: {P['selected']};
    border: 1px solid {P['accent']};
    border-radius: 10px;
}}

/* ---- 托盘 / 右键菜单 ---- */
QMenu {{
    background-color: {P['menu_bg']};
    color: {P['menu_text']};
    border: 1px solid {P['border']}; padding: 4px;
}}
QMenu::item {{ padding: 6px 22px; border-radius: 4px; font-size: 12px; background: transparent; }}
QMenu::item:disabled {{ color: {P['menu_disabled']}; }}
QMenu::item:selected {{ background-color: {P['hover']}; }}
QMenu::item:checked {{ background-color: {P['selected']}; color: {P['accent_text']}; font-weight: 600; }}
QMenu::separator {{ height: 1px; background: {P['border']}; margin: 4px 8px; }}

/* ---- RPG 沉浸卡片与仪表盘 ---- */
QFrame#HeroCard {{
    background-color: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 14px;
}}

QFrame#StatusGridCard {{
    background-color: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
}}

QFrame#DailyEventCard {{
    background-color: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
}}
QFrame#DailyEventCard:hover {{
    border-color: rgba(255, 255, 255, 0.16);
    background-color: rgba(255, 255, 255, 0.06);
}}

QFrame#ExplorationCard {{
    background-color: rgba(255, 255, 255, 0.038);
    border: 1px dashed rgba(255, 255, 255, 0.12);
    border-radius: 12px;
}}
QFrame#ExplorationCard:hover {{
    background-color: rgba(255, 255, 255, 0.055);
    border-color: rgba(229, 192, 123, 0.35);
}}

QFrame#GrowthCard {{
    background-color: rgba(255, 255, 255, 0.035);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 12px;
}}

QFrame#AttributeChip {{
    background-color: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 8px;
}}

/* 成就卡片 */
QFrame#AchievementCardUnlocked {{
    background-color: rgba(229, 192, 123, 0.06);
    border: 1px solid rgba(229, 192, 123, 0.25);
    border-radius: 12px;
}}
QFrame#AchievementCardLocked {{
    background-color: rgba(255, 255, 255, 0.025);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
}}
"""


PALETTE = {
    "dialog": "#23211f",
    "border": "rgba(255, 255, 255, 0.08)",
    "surface": "rgba(255, 255, 255, 0.05)",
    "text": "#ece7e1",
    "sub": "rgba(236, 231, 225, 0.46)",
    "accent": "#b2a69a",
    "accent_text": "#ded5c9",
    "primary": "#8d8376",
    "primary_text": "#faf7f2",
    "track": "rgba(255, 255, 255, 0.16)",
    "hover": "rgba(255, 255, 255, 0.09)",
    "pressed": "rgba(255, 255, 255, 0.17)",
    "button": "rgba(255, 255, 255, 0.06)",
    "input": "rgba(18, 17, 16, 0.85)",
    "dot": "rgba(255, 255, 255, 0.30)",
    "nav": "rgba(255, 255, 255, 0.025)",
    "nav_idle": "rgba(236, 231, 225, 0.52)",
    "selected": "rgba(178, 166, 154, 0.17)",
    "danger": "#e0958f",
    "danger_border": "rgba(224, 149, 143, 0.4)",
    "danger_hover": "rgba(224, 149, 143, 0.1)",
    "menu_bg": "#2e2b28",
    "menu_text": "#ece7e1",
    "menu_disabled": "rgba(236, 231, 225, 0.35)",
    "glass": (30, 28, 26, 150),
    "glass_border": (255, 255, 255, 30),
}


def build_stylesheet(mode: str = None) -> str:
    return _base(PALETTE)


class ThemeManager:
    """单主题管理器；保留系统探测的兼容占位。"""

    current = "dark"

    @classmethod
    def apply(cls, app, mode: str = None):
        app.setStyleSheet(build_stylesheet())

    @classmethod
    def glass(cls):
        return PALETTE["glass"]

    @classmethod
    def glass_border(cls):
        return PALETTE["glass_border"]

    @classmethod
    def palette(cls):
        return PALETTE

    @staticmethod
    def resolve_mode(theme_mode: str, app) -> str:
        return "dark"


alias_palette = ThemeManager.palette