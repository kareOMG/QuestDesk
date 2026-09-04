from PySide6.QtCore import Qt, QPoint
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QGraphicsDropShadowEffect
)
from PySide6.QtGui import QColor

from ui.styles import ThemeManager


class GlassDialog(QDialog):
    """通用的磨砂玻璃模态弹窗基类，跟随当前主题配色（杜绝原生窗口边框标题栏）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Dialog
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._drag_pos = QPoint()
        self._is_dragging = False

        self.root_layout = QVBoxLayout(self)
        self.root_layout.setContentsMargins(16, 16, 16, 16)

        # 内部卡片容器（确保不透明纯色底，防止底层文字重叠穿透）
        self.card = QFrame()
        self.card.setObjectName("DialogCard")
        self.card.setStyleSheet("QFrame#DialogCard { background-color: #23211f; border: 1px solid rgba(255, 255, 255, 0.14); border-radius: 16px; }")
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(22, 18, 22, 20)
        self.card_layout.setSpacing(12)
        self.root_layout.addWidget(self.card)

        # 弥散阴影
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(0, 0, 0, 95))
        self.card.setGraphicsEffect(shadow)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
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


class LevelUpDialog(GlassDialog):
    def __init__(self, new_level: int, parent=None):
        super().__init__(parent)
        self.resize(380, 240)
        p = ThemeManager.palette()

        # 顶部栏：标题 + 关闭
        top_bar = QHBoxLayout()
        tag = QLabel("等级突破")
        tag.setStyleSheet(f"color: {p['accent']}; background-color: {p['selected']};"
                          f"font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px;")
        top_bar.addWidget(tag)
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.accept)
        top_bar.addWidget(close_btn)
        self.card_layout.addLayout(top_bar)

        lvl = QLabel(f"Lv.{new_level}")
        lvl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lvl.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {p['accent']}; padding: 4px 0;")
        self.card_layout.addWidget(lvl)

        body = QLabel("能力边界再次拓展，向着更深的目标继续进发！")
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body.setWordWrap(True)
        body.setStyleSheet(f"color: {p['sub']}; font-size: 13px;")
        self.card_layout.addWidget(body)

        self.card_layout.addSpacing(6)
        confirm_btn = QPushButton("继续前进")
        confirm_btn.setObjectName("PrimaryBtn")
        confirm_btn.setFixedHeight(34)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        self.card_layout.addWidget(confirm_btn)


class QuestCompleteDialog(GlassDialog):
    def __init__(self, title: str, xp: int, leveled_up: bool, new_level: int, parent=None):
        super().__init__(parent)
        self.resize(400, 260)
        p = ThemeManager.palette()

        top_bar = QHBoxLayout()
        tag = QLabel("目标达成")
        tag.setStyleSheet(f"color: {p['accent']}; background-color: {p['selected']};"
                          f"font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 6px;")
        top_bar.addWidget(tag)
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.accept)
        top_bar.addWidget(close_btn)
        self.card_layout.addLayout(top_bar)

        q_title = QLabel(f"「{title}」")
        q_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        q_title.setWordWrap(True)
        q_title.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {p['text']}; padding: 6px 0;")
        self.card_layout.addWidget(q_title)

        reward_box = QHBoxLayout()
        reward_box.addStretch()
        reward_badge = QLabel(f"+{xp} 经验值已注入")
        reward_badge.setStyleSheet(
            f"color: {p['accent']}; background-color: {p['selected']};"
            f"font-size: 12px; font-weight: 600; padding: 4px 12px; border-radius: 10px;")
        reward_box.addWidget(reward_badge)
        reward_box.addStretch()
        self.card_layout.addLayout(reward_box)

        if leveled_up:
            up_note = QLabel(f"恭喜！同时突破升至 Lv.{new_level}")
            up_note.setAlignment(Qt.AlignmentFlag.AlignCenter)
            up_note.setStyleSheet(f"color: {p['accent']}; font-weight: 600; font-size: 12px;")
            self.card_layout.addWidget(up_note)

        self.card_layout.addSpacing(6)
        confirm_btn = QPushButton("收到，继续保持")
        confirm_btn.setObjectName("PrimaryBtn")
        confirm_btn.setFixedHeight(34)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        self.card_layout.addWidget(confirm_btn)


class AchievementUnlockDialog(GlassDialog):
    """成就解锁弹窗：带来强烈的 RPG 仪式感与正反馈"""

    def __init__(self, name: str, desc: str, icon: str = "🏆", parent=None):
        super().__init__(parent)
        self.resize(420, 270)
        p = ThemeManager.palette()

        top_bar = QHBoxLayout()
        tag = QLabel("🏆 成就解锁")
        tag.setStyleSheet(
            f"color: #e5c07b; background-color: rgba(229, 192, 123, 0.16); "
            f"font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 6px; border: 1px solid rgba(229, 192, 123, 0.3);"
        )
        top_bar.addWidget(tag)
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.accept)
        top_bar.addWidget(close_btn)
        self.card_layout.addLayout(top_bar)

        # 勋章图标与成就名称
        title_box = QVBoxLayout()
        title_box.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_box.setSpacing(4)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 38px; padding-top: 4px;")
        title_box.addWidget(icon_lbl)

        name_lbl = QLabel(name)
        name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_lbl.setStyleSheet(f"font-size: 18px; font-weight: 800; color: #ece7e1;")
        title_box.addWidget(name_lbl)

        desc_lbl = QLabel(desc)
        desc_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc_lbl.setWordWrap(True)
        desc_lbl.setStyleSheet(f"font-size: 13px; color: {p['sub']}; padding: 0 16px;")
        title_box.addWidget(desc_lbl)

        self.card_layout.addLayout(title_box)
        self.card_layout.addSpacing(8)

        confirm_btn = QPushButton("荣耀铭刻")
        confirm_btn.setObjectName("PrimaryBtn")
        confirm_btn.setFixedHeight(34)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        self.card_layout.addWidget(confirm_btn)


class ConfirmDialog(GlassDialog):
    """统一暗黑磨砂玻璃质感的二次确认弹窗（彻底替代 Windows 原生白底 QMessageBox）"""

    def __init__(self, title: str, message: str, parent=None,
                 confirm_text: str = "确定", cancel_text: str = "取消",
                 is_danger: bool = False):
        super().__init__(parent)
        self.resize(390, 210)
        p = ThemeManager.palette()

        # 顶部栏：标题标签 + 关闭按钮
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)

        tag = QLabel(title)
        tag.setObjectName("DialogTitle")
        tag.setStyleSheet("font-size: 14px; font-weight: 700; color: #ece7e1;")
        top_bar.addWidget(tag)
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(22, 22)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.reject)
        top_bar.addWidget(close_btn)
        self.card_layout.addLayout(top_bar)

        # 内容提示文本
        msg_lbl = QLabel(message)
        msg_lbl.setObjectName("DialogBody")
        msg_lbl.setWordWrap(True)
        msg_lbl.setStyleSheet(f"font-size: 13px; color: {p['text']}; line-height: 1.4; padding: 10px 2px 6px 2px;")
        self.card_layout.addWidget(msg_lbl)

        self.card_layout.addStretch()

        # 底部操作按钮栏
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        cancel_btn = QPushButton(cancel_text)
        cancel_btn.setObjectName("GhostBtn")
        cancel_btn.setMinimumWidth(72)
        cancel_btn.setFixedHeight(32)
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(cancel_btn)

        confirm_btn = QPushButton(confirm_text)
        if is_danger:
            confirm_btn.setObjectName("DangerBtn")
            confirm_btn.setStyleSheet(
                f"background-color: {p['danger_border']}; color: #ffffff; font-weight: 600; "
                f"border-radius: 6px; padding: 4px 16px;"
            )
        else:
            confirm_btn.setObjectName("PrimaryBtn")
            confirm_btn.setStyleSheet("padding: 4px 16px;")
        confirm_btn.setMinimumWidth(72)
        confirm_btn.setFixedHeight(32)
        confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        confirm_btn.clicked.connect(self.accept)
        btn_row.addWidget(confirm_btn)

        self.card_layout.addLayout(btn_row)

    @classmethod
    def ask(cls, parent, title: str, message: str, confirm_text: str = "确定",
            cancel_text: str = "取消", is_danger: bool = False) -> bool:
        dlg = cls(title, message, parent, confirm_text, cancel_text, is_danger)
        return dlg.exec() == QDialog.DialogCode.Accepted