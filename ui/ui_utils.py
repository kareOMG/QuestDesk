"""
QuestDesk - UI 通用工具与渲染增强组件 (ui/ui_utils.py)
提供布局安全递归清理、平滑高质量 Pixmap 缩放以及应用图标自动加载等通用方法。
"""

import os
from typing import Union, Tuple
from pathlib import Path

from PySide6.QtWidgets import QLayout
from PySide6.QtGui import QPixmap, QIcon, QPainter, QColor
from PySide6.QtCore import Qt, QRectF

from core.paths import get_assets_dir, get_icons_dir


def clear_layout(layout: QLayout):
    """
    递归销毁布局中的所有子控件与嵌套子布局，
    彻底避免在切换视图或重新构建列表时产生内存孤儿控件和重叠渲染残留。
    """
    if layout is None:
        return
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget is not None:
            widget.hide()
            widget.setParent(None)
            widget.deleteLater()
        elif item.layout() is not None:
            clear_layout(item.layout())


def get_smooth_pixmap(file_path: Union[str, Path], size: Union[int, Tuple[int, int]]) -> QPixmap:
    """
    加载指定图像并以高质量平滑算法 (SmoothTransformation) 进行保真等比缩放。
    若图片不存在或加载失败，返回相应尺寸的透明 QPixmap。
    """
    target_w = size if isinstance(size, int) else size[0]
    target_h = size if isinstance(size, int) else size[1]

    path_str = str(file_path)
    if os.path.exists(path_str):
        pix = QPixmap(path_str)
        if not pix.isNull():
            return pix.scaled(
                target_w, target_h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )

    fallback = QPixmap(target_w, target_h)
    fallback.fill(Qt.GlobalColor.transparent)
    return fallback


def load_app_icon() -> QIcon:
    """
    自动按优先级加载应用图标（支持 .ico 与高分辨率 .png），若本地文件缺失则动态程序化绘制备用矢量图标。
    """
    icons_dir = get_icons_dir()
    assets_dir = get_assets_dir()

    candidate_paths = [
        icons_dir / "logo.ico",
        icons_dir / "logo.png",
        icons_dir / "logo_128.png",
        assets_dir / "logo.ico",
        assets_dir / "logo.png",
        assets_dir / "logo_128.png",
    ]

    for p in candidate_paths:
        if p.exists():
            icon = QIcon(str(p))
            if not icon.isNull():
                return icon

    # 程序化自绘制现代极简风格备用图标
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
    painter.drawLine(28, 40, 42, 24)
    painter.end()

    return QIcon(pixmap)
