"""
QuestDesk 轻量级强类型发布-订阅事件总线 (EventBus)
解耦 UI 表现层与 Service 业务层
"""

from dataclasses import dataclass
from typing import Callable, Dict, List, Type, Any
from models.achievement import Achievement
from models.user_stats import UserStats


@dataclass
class BaseEvent:
    """事件基类"""
    pass


@dataclass
class TaskToggledEvent(BaseEvent):
    """任务勾选状态变更事件"""
    big_id: str
    small_id: str
    done: bool
    gained_xp: int
    attribute: str
    pomo: int
    task_title: str
    big_title: str


@dataclass
class LevelUpEvent(BaseEvent):
    """等级突破事件"""
    new_level: int
    total_xp: int


@dataclass
class AchievementUnlockedEvent(BaseEvent):
    """成就解锁事件"""
    achievement: Achievement


@dataclass
class StatsUpdatedEvent(BaseEvent):
    """全局状态/属性更新事件"""
    user_stats: UserStats


@dataclass
class WeeklyResetEvent(BaseEvent):
    """周度复盘重置事件"""
    pass


class EventBus:
    def __init__(self):
        self._listeners: Dict[Type[BaseEvent], List[Callable[[Any], None]]] = {}

    def subscribe(self, event_type: Type[BaseEvent], callback: Callable[[Any], None]):
        """订阅指定类型的事件"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        if callback not in self._listeners[event_type]:
            self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type: Type[BaseEvent], callback: Callable[[Any], None]):
        """取消订阅指定事件"""
        if event_type in self._listeners and callback in self._listeners[event_type]:
            self._listeners[event_type].remove(callback)

    def publish(self, event: BaseEvent):
        """发布事件并同步通知所有监听者"""
        event_type = type(event)
        callbacks = self._listeners.get(event_type, [])
        for cb in list(callbacks):
            try:
                cb(event)
            except Exception as e:
                print(f"[EventBus Error] 执行事件监听器 {cb} 失败: {e}")


# 全局事件总线单例
event_bus = EventBus()
