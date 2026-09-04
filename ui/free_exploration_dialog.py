from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QFrame, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt
from ui.toast_dialog import GlassDialog
from ui.styles import ThemeManager
from config.constants import AttributeType


class FreeExplorationDialog(GlassDialog):
    """
    自由探索打卡弹窗（双轨番茄之“自由探索轨”）：
    记录计划外的专注投入（文献阅读、新技术调研、临时解题、论文研读等），
    给予轻量经验反馈（+15 XP/🍅）与对应学科属性沉淀。
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(420, 360)
        self.selected_pomo = 1
        self.selected_attr = AttributeType.CODING
        self._init_form()

    def _init_form(self):
        p = ThemeManager.palette()

        # 1. 顶部栏：标题与关闭
        top_bar = QHBoxLayout()
        top_bar.setContentsMargins(0, 0, 0, 0)
        tag = QLabel("🧭 自由探索 · 专注资源投入")
        tag.setObjectName("DialogTitle")
        tag.setStyleSheet("font-size: 14px; font-weight: 700; color: #ece7e1;")
        top_bar.addWidget(tag)
        top_bar.addStretch()

        close_btn = QPushButton("X")
        close_btn.setObjectName("CloseBtn")
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.reject)
        top_bar.addWidget(close_btn)
        self.card_layout.addLayout(top_bar)

        sub_desc = QLabel("记录未在周排期中的自学、阅读、查阅资料或拓展实践。")
        sub_desc.setStyleSheet(f"font-size: 12px; color: {p['sub']}; padding-bottom: 4px;")
        self.card_layout.addWidget(sub_desc)

        # 2. 投入番茄数量选择
        pomo_section = QVBoxLayout()
        pomo_section.setSpacing(6)
        p_lbl = QLabel("投入专注资源 (1 🍅 = 40分钟)：")
        p_lbl.setObjectName("MetaText")
        pomo_section.addWidget(p_lbl)

        pomo_btn_row = QHBoxLayout()
        pomo_btn_row.setSpacing(8)
        self.pomo_btns = []
        for n in [1, 2, 3, 4]:
            btn = QPushButton(f"{n} 🍅")
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, val=n: self._select_pomo(val))
            pomo_btn_row.addWidget(btn)
            self.pomo_btns.append((n, btn))
        pomo_section.addLayout(pomo_btn_row)
        self.card_layout.addLayout(pomo_section)

        # 3. 关联属性维度选择
        attr_section = QVBoxLayout()
        attr_section.setSpacing(6)
        a_lbl = QLabel("成长属性归属：")
        a_lbl.setObjectName("MetaText")
        attr_section.addWidget(a_lbl)

        attr_row = QHBoxLayout()
        attr_row.setSpacing(6)
        self.attr_btns = []
        attrs = [AttributeType.CODING, AttributeType.MATH, AttributeType.ENGLISH,
                 AttributeType.PRACTICE, AttributeType.REVIEW]
        for name in attrs:
            btn = QPushButton(f"◇ {name}")
            btn.setCheckable(True)
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, val=name: self._select_attr(val))
            attr_row.addWidget(btn)
            self.attr_btns.append((name, btn))
        attr_section.addLayout(attr_row)
        self.card_layout.addLayout(attr_section)

        # 4. 探索主题简述（选填）
        topic_section = QVBoxLayout()
        topic_section.setSpacing(4)
        t_lbl = QLabel("探索主题（选填）：")
        t_lbl.setObjectName("MetaText")
        topic_section.addWidget(t_lbl)

        self.topic_edit = QLineEdit()
        self.topic_edit.setPlaceholderText("如：阅读技术文档 / 查阅论文 / 临时调试代码")
        topic_section.addWidget(self.topic_edit)
        self.card_layout.addLayout(topic_section)

        # 5. 预期奖励提示
        self.preview_lbl = QLabel()
        self.preview_lbl.setStyleSheet(
            f"font-size: 11px; color: {p['accent']}; background-color: {p['selected']}; "
            f"padding: 6px 10px; border-radius: 6px; font-weight: 600;"
        )
        self.card_layout.addWidget(self.preview_lbl)

        self.card_layout.addStretch()

        # 6. 底部操作栏
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        btn_row.addStretch()

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("GhostBtn")
        self.cancel_btn.setMinimumWidth(80)
        self.cancel_btn.setFixedHeight(34)
        self.cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.cancel_btn.setToolTip("放弃并关闭窗口")
        self.cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(self.cancel_btn)

        self.confirm_btn = QPushButton("记录探索投入")
        self.confirm_btn.setObjectName("PrimaryBtn")
        self.confirm_btn.setMinimumWidth(120)
        self.confirm_btn.setFixedHeight(34)
        self.confirm_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.confirm_btn.setToolTip("确认并记录本次自由探索投入，结算属性与经验反馈")
        self.confirm_btn.clicked.connect(self.accept)
        btn_row.addWidget(self.confirm_btn)

        self.card_layout.addLayout(btn_row)

        # 初始化选中项
        self._select_pomo(1)
        self._select_attr(AttributeType.CODING)

    def _select_pomo(self, n: int):
        self.selected_pomo = n
        p = ThemeManager.palette()
        for val, btn in self.pomo_btns:
            if val == n:
                btn.setStyleSheet(f"background-color: {p['accent']}; color: #211f1c; font-weight: 700; border: none;")
            else:
                btn.setStyleSheet("")
        self._update_preview()

    def _select_attr(self, name: str):
        self.selected_attr = name
        p = ThemeManager.palette()
        for val, btn in self.attr_btns:
            if val == name:
                btn.setStyleSheet(f"background-color: {p['accent']}; color: #211f1c; font-weight: 700; border: none;")
            else:
                btn.setStyleSheet("")
        self._update_preview()

    def _update_preview(self):
        xp = self.selected_pomo * 15
        self.preview_lbl.setText(f"✦ 预计收获: +{xp} XP 经验反馈  ·  +{xp} {self.selected_attr}属性成长点")

    def get_result(self):
        return {
            "pomos": self.selected_pomo,
            "attribute": self.selected_attr,
            "topic": self.topic_edit.text().strip(),
        }
