import os
import re
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
from PySide6.QtCore import Qt

import sys

def _get_icons_dir() -> str:
    if getattr(sys, "frozen", False):
        internal = os.path.join(getattr(sys, "_MEIPASS", ""), "assets", "icons")
        if os.path.exists(internal):
            return internal
        return os.path.join(os.path.dirname(sys.executable), "assets", "icons")
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "icons"))

ICONS_DIR = _get_icons_dir()

ICON_KEYWORDS = {
    "math.png": ["数", "算", "高数", "代数", "几何", "微积分", "物理"],
    "code.png": ["代码", "数据结构", "程序", "开发", "c语言", "java", "python", "算法", "嵌入式", "网络"],
    "english.png": ["英", "外语", "单词", "长难句", "阅读", "写作", "听力", "考研英语"],
    "book.png": ["书", "教材", "复盘", "讲义", "学习", "专业课"],
}


def clean_title_no_emoji(title: str) -> str:
    """去除标题中残留的 emoji 表情符与常见标志，返回干净规范的文字"""
    if not title:
        return ""
    # 去除常见 emoji 范围及修饰符
    emoji_pattern = re.compile(
        "[\U00010000-\U0010ffff"
        "\U00002600-\U000027bf"
        "\U00002300-\U000023ff"
        "\U00002b50-\U00002b55"
        "\U0000fe00-\U0000fe0f"
        "\U0001f300-\U0001f9ff"
        "]+",
        flags=re.UNICODE
    )
    cleaned = emoji_pattern.sub("", title)
    # 去除残留的类似 "GB " 或特定开头的杂质
    cleaned = re.sub(r"^(GB|UK|US)\s*", "", cleaned).strip()
    return cleaned or title.strip()


def get_task_icon_path(title: str) -> str:
    """根据大任务标题关键词，从用户提供的图标包中自动匹配最精准的专属图标文件"""
    t = title.lower()
    for icon_name, keywords in ICON_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in t:
                path = os.path.join(ICONS_DIR, icon_name)
                if os.path.exists(path):
                    return path
    # 默认书籍图标
    fallback = os.path.join(ICONS_DIR, "book.png")
    return fallback if os.path.exists(fallback) else ""


def get_task_pixmap(title: str, size: int = 18, theme: str = "dark") -> QPixmap:
    """获取指定尺寸的清晰图标 Pixmap，支持深浅色模式自适应着色"""
    icon_path = get_task_icon_path(title)
    if not icon_path or not os.path.exists(icon_path):
        # 兜底返回空白透明 pixmap
        p = QPixmap(size, size)
        p.fill(Qt.GlobalColor.transparent)
        return p

    orig = QPixmap(icon_path)
    scaled = orig.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    # 若为浅色模式，将白色笔画染为深灰色；若深色模式则保持优雅高对比度米白
    target_color = QColor("#1d1d1f") if theme == "light" else QColor("#e8e8ed")

    result = QPixmap(scaled.size())
    result.fill(Qt.GlobalColor.transparent)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.drawPixmap(0, 0, scaled)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(result.rect(), target_color)
    painter.end()

    return result
