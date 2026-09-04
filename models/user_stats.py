from dataclasses import dataclass, field
from typing import Dict
from config.constants import get_rank_title, DEFAULT_ATTRIBUTES


def rank_name(level: int) -> str:
    return get_rank_title(level)


@dataclass
class UserStats:
    level: int = 1
    current_xp: int = 0
    next_level_xp: int = 500
    overall_progress: int = 0
    xp_growth_factor: float = 1.2
    theme_mode: str = "dark"
    total_xp: int = 0  # 历史累计获得经验
    last_active_date: str = ""  # 上次活跃日期 (YYYY-MM-DD)，跨天自动重置今日番茄
    streak_days: int = 1  # 连续学习天数

    # 任务累计完成统计
    total_small_tasks_done: int = 0  # 小任务累计完成次数
    total_big_tasks_done: int = 0    # 大任务累计攻克次数

    # 【双轨番茄体系 · 学习投入资源】
    # 1. 任务番茄（Quest Focus）：主线推进
    task_pomo_today: int = 0   # 今日任务番茄
    task_pomo_week: int = 0    # 本周任务番茄
    task_pomo_total: int = 0   # 历史累计任务番茄

    # 2. 自由探索番茄（Free Exploration）：主动探索发现
    free_pomo_today: int = 0   # 今日自由探索番茄
    free_pomo_week: int = 0    # 本周自由探索番茄
    free_pomo_total: int = 0   # 历史累计自由探索番茄

    # 四维成长属性：记录本周获得的属性增量点数 {"数学": 80, "编程": 120, ...}
    weekly_attributes: Dict[str, int] = field(default_factory=lambda: dict(DEFAULT_ATTRIBUTES))
    # 每日番茄预算：周一~周日
    day_target: list = field(default_factory=lambda: [3, 4, 4, 6, 5, 6, 3])
    # 面板整体透明度（0.35 ~ 1.0）
    window_opacity: float = 0.95

    @property
    def rank(self) -> str:
        return get_rank_title(self.level)

    @property
    def pomo_today(self) -> int:
        """向后兼容属性：返回今日总投入番茄（主线 + 自由探索）"""
        return self.task_pomo_today + self.free_pomo_today

    @pomo_today.setter
    def pomo_today(self, val: int):
        self.task_pomo_today = max(0, int(val))

    @property
    def total_pomo_today(self) -> int:
        return self.task_pomo_today + self.free_pomo_today

    @property
    def total_pomo_week(self) -> int:
        return self.task_pomo_week + self.free_pomo_week

    @property
    def total_pomo_history(self) -> int:
        return self.task_pomo_total + self.free_pomo_total

    def add_xp(self, xp: int) -> bool:
        """Add XP and return True if leveled up."""
        self.current_xp += xp
        self.total_xp += xp
        leveled_up = False
        while self.current_xp >= self.next_level_xp:
            self.current_xp -= self.next_level_xp
            self.level += 1
            self.next_level_xp = int(self.next_level_xp * self.xp_growth_factor)
            leveled_up = True
        return leveled_up

    def add_attribute_point(self, attr_name: str, points: int):
        """增加本周指定维度的成长点数"""
        if attr_name not in self.weekly_attributes:
            self.weekly_attributes[attr_name] = 0
        self.weekly_attributes[attr_name] += points

    def reset_weekly_attributes(self):
        """周度复盘时重置本周属性成长"""
        self.weekly_attributes = dict(DEFAULT_ATTRIBUTES)

    @classmethod
    def from_dict(cls, data: dict) -> 'UserStats':
        target = data.get("day_target") or [3, 4, 4, 6, 5, 6, 3]
        attrs = dict(DEFAULT_ATTRIBUTES)
        if "weekly_attributes" in data and isinstance(data["weekly_attributes"], dict):
            attrs.update(data["weekly_attributes"])

        legacy_pomo = data.get("pomo_today", 0)
        return cls(
            level=data.get("level", 1),
            current_xp=data.get("current_xp", 0),
            next_level_xp=data.get("next_level_xp", 500),
            overall_progress=data.get("overall_progress", 0),
            xp_growth_factor=data.get("xp_growth_factor", 1.2),
            theme_mode=data.get("theme_mode", "dark"),
            total_xp=data.get("total_xp", 0),
            last_active_date=data.get("last_active_date", ""),
            streak_days=data.get("streak_days", 1),
            total_small_tasks_done=data.get("total_small_tasks_done", 0),
            total_big_tasks_done=data.get("total_big_tasks_done", 0),
            task_pomo_today=data.get("task_pomo_today", legacy_pomo),
            task_pomo_week=data.get("task_pomo_week", 0),
            task_pomo_total=data.get("task_pomo_total", 0),
            free_pomo_today=data.get("free_pomo_today", 0),
            free_pomo_week=data.get("free_pomo_week", 0),
            free_pomo_total=data.get("free_pomo_total", 0),
            weekly_attributes=attrs,
            day_target=list(target),
            window_opacity=float(data.get("window_opacity", 0.95)),
        )

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "current_xp": self.current_xp,
            "next_level_xp": self.next_level_xp,
            "overall_progress": self.overall_progress,
            "xp_growth_factor": self.xp_growth_factor,
            "theme_mode": self.theme_mode,
            "total_xp": self.total_xp,
            "pomo_today": self.total_pomo_today,
            "last_active_date": self.last_active_date,
            "streak_days": self.streak_days,
            "total_small_tasks_done": self.total_small_tasks_done,
            "total_big_tasks_done": self.total_big_tasks_done,
            "task_pomo_today": self.task_pomo_today,
            "task_pomo_week": self.task_pomo_week,
            "task_pomo_total": self.task_pomo_total,
            "free_pomo_today": self.free_pomo_today,
            "free_pomo_week": self.free_pomo_week,
            "free_pomo_total": self.free_pomo_total,
            "weekly_attributes": self.weekly_attributes,
            "day_target": self.day_target,
            "window_opacity": self.window_opacity,
        }