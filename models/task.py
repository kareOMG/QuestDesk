from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# 周一..周日
DAYS = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


@dataclass
class SmallTask:
    """小任务：最小可勾选项；day 表示周一(0)~周日(6)，None=未排期；pomo 为预算番茄，actual_pomo 为实际投入番茄"""
    id: str
    title: str
    done: bool = False
    xp: int = 30
    # 经验是否已发放，防止反复勾选刷经验
    awarded: bool = False
    # 周一到周日 = 0..6，None 表示未安排
    day: Optional[int] = None
    pomo: int = 1         # 预算番茄（计划投入专注资源）
    actual_pomo: int = 1  # 实际投入番茄

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
            "xp": self.xp,
            "awarded": self.awarded,
            "day": self.day,
            "pomo": self.pomo,
            "actual_pomo": self.actual_pomo,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SmallTask':
        pomo_val = data.get("pomo", 1)
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            done=data.get("done", False),
            xp=data.get("xp", 30),
            awarded=data.get("awarded", False),
            day=data.get("day"),
            pomo=pomo_val,
            actual_pomo=data.get("actual_pomo", pomo_val),
        )


class BigTask:
    """大任务：一组小任务的集合；每周番茄预算由小任务所需的番茄总和自动计算"""

    def __init__(self, id: str, title: str, tasks: Optional[List[SmallTask]] = None, pomo_budget: Optional[int] = None):
        self.id = id
        self.title = title
        self.tasks = list(tasks) if tasks is not None else []

    @property
    def done_count(self) -> int:
        return sum(1 for t in self.tasks if t.done)

    @property
    def total(self) -> int:
        return len(self.tasks)

    @property
    def completed(self) -> bool:
        return bool(self.tasks) and all(t.done for t in self.tasks)

    @property
    def progress_percentage(self) -> int:
        if not self.tasks:
            return 0
        return int(self.done_count / self.total * 100)

    @property
    def pomo_done(self) -> int:
        return sum(t.pomo for t in self.tasks if t.done)

    @property
    def pomo_total(self) -> int:
        return sum(t.pomo for t in self.tasks)

    @property
    def pomo_budget(self) -> int:
        """每周番茄预算：由所有小任务所需番茄相加计算得出"""
        return self.pomo_total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "tasks": [t.to_dict() for t in self.tasks],
            "pomo_budget": self.pomo_total,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BigTask':
        tasks = [SmallTask.from_dict(t) for t in data.get("tasks", [])]
        return cls(
            id=data.get("id", ""),
            title=data.get("title", ""),
            tasks=tasks,
        )