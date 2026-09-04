import time
from typing import List, Dict, Any, Optional
from models.achievement import Achievement
from events.event_bus import event_bus, TaskToggledEvent, LevelUpEvent, AchievementUnlockedEvent
from config.constants import PRESET_ACHIEVEMENTS


class AchievementService:
    """成就判定与跟踪服务"""

    def __init__(self, achievements: List[Achievement] = None):
        self.achievements: List[Achievement] = achievements or []
        self._ensure_preset_achievements()
        self._subscribe_events()

    def _ensure_preset_achievements(self):
        """确保预设成就全部存在"""
        existing_ids = {a.id for a in self.achievements}
        for preset in PRESET_ACHIEVEMENTS:
            if preset["id"] not in existing_ids:
                self.achievements.append(Achievement.from_dict(preset))

    def _subscribe_events(self):
        event_bus.subscribe(TaskToggledEvent, self._on_task_toggled)
        event_bus.subscribe(LevelUpEvent, self._on_level_up)

    def _get_achievement(self, ach_id: str) -> Optional[Achievement]:
        for a in self.achievements:
            if a.id == ach_id:
                return a
        return None

    def _unlock(self, ach: Achievement):
        if not ach.unlocked:
            ach.unlocked = True
            ach.current_progress = ach.target_progress
            ach.unlocked_at = time.strftime("%Y-%m-%d %H:%M")
            print(f"[Achievement] 解锁成就: {ach.name} ({ach.description})")
            event_bus.publish(AchievementUnlockedEvent(achievement=ach))

    def _on_level_up(self, event: LevelUpEvent):
        ach = self._get_achievement("level_up_1")
        if ach and not ach.unlocked and event.new_level >= ach.target_progress:
            self._unlock(ach)

    def _on_task_toggled(self, event: TaskToggledEvent):
        if not event.done:
            return

        # 1. 首杀小任务
        fb = self._get_achievement("first_blood")
        if fb and not fb.unlocked:
            fb.current_progress = 1
            self._unlock(fb)

        # 2. 各专项成就累计
        if "高等数学" in event.big_title:
            ach = self._get_achievement("math_expert")
            if ach and not ach.unlocked:
                ach.current_progress += 1
                if ach.current_progress >= ach.target_progress:
                    self._unlock(ach)

        elif "数据结构" in event.big_title:
            ach = self._get_achievement("ds_coder")
            if ach and not ach.unlocked:
                ach.current_progress += 1
                if ach.current_progress >= ach.target_progress:
                    self._unlock(ach)

        elif "英语" in event.big_title:
            ach = self._get_achievement("english_persistent")
            if ach and not ach.unlocked:
                ach.current_progress += 1
                if ach.current_progress >= ach.target_progress:
                    self._unlock(ach)

        elif "复盘" in event.big_title:
            ach = self._get_achievement("sunday_review")
            if ach and not ach.unlocked:
                ach.current_progress = 1
                self._unlock(ach)

    def check_pomo_achievements(self, total_pomo: int):
        """番茄数阈值检查"""
        for ach_id, req in [("pomo_10", 10), ("pomo_30", 30)]:
            ach = self._get_achievement(ach_id)
            if ach and not ach.unlocked:
                ach.current_progress = total_pomo
                if total_pomo >= req:
                    self._unlock(ach)

    def get_unlocked_count(self) -> int:
        return sum(1 for a in self.achievements if a.unlocked)

    def get_total_count(self) -> int:
        return len(self.achievements)
