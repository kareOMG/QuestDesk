import random
import math
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont


class Particle:
    def __init__(self, cx, cy):
        self.x = cx + random.uniform(-40, 40)
        self.y = cy + random.uniform(-10, 10)
        speed = random.uniform(8.0, 14.5)
        angle = random.uniform(-math.pi * 0.85, -math.pi * 0.15)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.gravity = 0.32
        self.drag = 0.985
        self.rotation = random.uniform(0, 360)
        self.v_rot = random.uniform(-10, 10)
        self.w = random.uniform(5, 10)
        self.h = random.uniform(4, 8)
        self.shape = random.choice(["rect", "circle", "ribbon"])

        palette = [
            QColor(245, 196, 68),   # 暖金
            QColor(235, 110, 128),  # 柔粉
            QColor(82, 196, 140),   # 翡翠
            QColor(230, 145, 90),   # 暖橙
            QColor(170, 140, 240),  # 薰衣草紫
            QColor(90, 185, 235),   # 澄空蓝
            QColor(255, 235, 160),  # 珍珠白金
        ]
        self.color = random.choice(palette)
        self.alpha = 255.0
        self.fade_speed = random.uniform(1.6, 2.4)

    def update(self):
        self.vy += self.gravity
        self.vx *= self.drag
        self.vy *= self.drag
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.v_rot
        self.alpha = max(0.0, self.alpha - self.fade_speed)
        return self.alpha > 5.0


class ConfettiCelebrationOverlay(QWidget):
    """今日任务全部完成专属：60FPS 原生轻量多彩礼花粒子与优雅玻璃庆祝浮层"""

    def __init__(self, parent=None, task_count=0, total_pomo=0):
        super().__init__(parent)
        self.task_count = task_count
        self.total_pomo = total_pomo
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)
        if parent:
            self.setGeometry(parent.rect())

        self.particles = []
        self._spawn_particles()

        self._frame = 0
        self._max_frames = 170  # 约 2.8 秒 (16ms * 170)
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_tick)
        self._timer.start(16)
        self.show()
        self.raise_()

    def _spawn_particles(self):
        w = max(400, self.width())
        h = max(300, self.height())
        cx = w / 2.0
        cy = h * 0.65
        for _ in range(85):
            self.particles.append(Particle(cx, cy))

    def _on_tick(self):
        self._frame += 1
        alive = []
        for p in self.particles:
            if p.update():
                alive.append(p)
        self.particles = alive

        if self._frame >= self._max_frames and not self.particles:
            self._timer.stop()
            self.deleteLater()
            return
        self.update()

    def mousePressEvent(self, event):
        """点击任意区域平滑关闭礼花庆祝浮层"""
        self._timer.stop()
        self.deleteLater()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 1. 绘制多彩礼花粒子
        for p in self.particles:
            painter.save()
            painter.translate(p.x, p.y)
            painter.rotate(p.rotation)
            c = QColor(p.color)
            c.setAlpha(int(p.alpha))
            painter.setBrush(QBrush(c))
            painter.setPen(Qt.PenStyle.NoPen)

            if p.shape == "circle":
                painter.drawEllipse(QPointF(0, 0), p.w * 0.5, p.w * 0.5)
            elif p.shape == "ribbon":
                painter.drawRoundedRect(QRectF(-p.w / 2, -p.h / 2, p.w * 1.5, p.h * 0.6), 2, 2)
            else:
                painter.drawRect(QRectF(-p.w / 2, -p.h / 2, p.w, p.h))
            painter.restore()

        # 2. 绘制居中暖炭磨砂胜利气泡卡片 (Banner)
        banner_alpha = 255
        if self._frame < 15:
            banner_alpha = int((self._frame / 15.0) * 255)
        elif self._frame > 130:
            banner_alpha = max(0, int(((self._max_frames - self._frame) / 40.0) * 255))

        if banner_alpha > 0:
            bw, bh = 340, 92
            bx = (self.width() - bw) / 2.0
            by = (self.height() - bh) / 2.0 - 15

            painter.save()
            # 磨砂阴影底
            shadow_rect = QRectF(bx, by + 3, bw, bh)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0, int(banner_alpha * 0.35)))
            painter.drawRoundedRect(shadow_rect, 16, 16)

            # 气泡背景（温润深炭）
            card_rect = QRectF(bx, by, bw, bh)
            painter.setBrush(QColor(28, 26, 24, int(banner_alpha * 0.94)))
            pen = QPen(QColor(230, 200, 150, int(banner_alpha * 0.45)))
            pen.setWidthF(1.2)
            painter.setPen(pen)
            painter.drawRoundedRect(card_rect, 16, 16)

            # 主标题文本
            font_title = QFont(painter.font())
            font_title.setPointSize(13)
            font_title.setBold(True)
            painter.setFont(font_title)
            painter.setPen(QColor(245, 235, 225, banner_alpha))
            title_text = "🎉 今日试炼 · 全数攻克！"
            painter.drawText(QRectF(bx, by + 16, bw, 26), Qt.AlignmentFlag.AlignCenter, title_text)

            # 副标题文本
            font_sub = QFont(painter.font())
            font_sub.setPointSize(10)
            font_sub.setBold(False)
            painter.setFont(font_sub)
            painter.setPen(QColor(185, 175, 165, int(banner_alpha * 0.9)))
            sub_text = f"今日专注全部达成 · 恭喜完成 {self.task_count} 项试炼" if self.task_count > 0 else "今日所有冒险任务圆满收官，好好休息！"
            painter.drawText(QRectF(bx, by + 46, bw, 22), Qt.AlignmentFlag.AlignCenter, sub_text)
            painter.restore()
