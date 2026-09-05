import time
import datetime
from typing import List, Dict, Any, Optional, Set
from models.achievement import Achievement
from events.event_bus import (
    event_bus, TaskToggledEvent, LevelUpEvent, AchievementUnlockedEvent,
    AllDailyTasksCompletedEvent, StatsUpdatedEvent
)
from config.constants import PRESET_ACHIEVEMENTS


class AchievementService:
    """成就判定与跟踪服务"""

    def __init__(self, achievements: List[Achievement] = None):
        self.achievements: List[Achievement] = achievements or []
        self._today_subjects: Set[str] = set()
        self._ensure_preset_achievements()
        self._subscribe_events()

    def _ensure_preset_achievements(self):
        """确保预设成就全部存在并与最新配置同步基础属性（名称、图标、线索）"""
        existing_map = {a.id: a for a in self.achievements}
        for preset in PRESET_ACHIEVEMENTS:
            pid = preset["id"]
            if pid not in existing_map:
                self.achievements.append(Achievement.from_dict(preset))
            else:
                ach = existing_map[pid]
                ach.name = preset["name"]
                ach.description = preset["description"]
                ach.icon = preset["icon"]
                ach.category = preset["category"]
                ach.target_progress = preset["target_progress"]
                ach.clue = preset.get("clue", "")

    def _subscribe_events(self):
        event_bus.subscribe(TaskToggledEvent, self._on_task_toggled)
        event_bus.subscribe(LevelUpEvent, self._on_level_up)
        event_bus.subscribe(AllDailyTasksCompletedEvent, self._on_all_daily_completed)
        event_bus.subscribe(StatsUpdatedEvent, self._on_stats_updated)

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

    def record_logo_click(self) -> int:
        """记录主界面 Logo 徽记敲击，触发彩蛋成就"""
        ach = self._get_achievement("logo_tapper_10")
        if not ach:
            return 0
        if not ach.unlocked:
            ach.current_progress += 1
            if ach.current_progress >= ach.target_progress:
                self._unlock(ach)
        return ach.current_progress

    def _on_all_daily_completed(self, event: AllDailyTasksCompletedEvent):
        """全境肃清：单日全任务完成"""
        ach = self._get_achievement("all_daily_clear")
        if ach and not ach.unlocked:
            ach.current_progress = 1
            self._unlock(ach)

    def _on_stats_updated(self, event: StatsUpdatedEvent):
        """连击天数成就检查"""
        streak = getattr(event.user_stats, "streak_days", 0)
        for ach_id, req in [("streak_3", 3), ("streak_7", 7)]:
            ach = self._get_achievement(ach_id)
            if ach and not ach.unlocked:
                ach.current_progress = streak
                if streak >= req:
                    self._unlock(ach)

    def _on_level_up(self, event: LevelUpEvent):
        """等级突破成就"""
        for ach_id in ["level_up_1", "level_5", "level_10"]:
            ach = self._get_achievement(ach_id)
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

        # 2. 彩蛋：时间与时段判定
        now = datetime.datetime.now()
        hour = now.hour
        weekday = now.weekday()  # 0~6: 周一至周日

        # 夜巡游侠: 23:00 - 04:59
        if hour >= 23 or hour < 5:
            owl = self._get_achievement("night_owl")
            if owl and not owl.unlocked:
                owl.current_progress = 1
                self._unlock(owl)

        # 晨曦先驱: 05:00 - 06:59
        if 5 <= hour < 7:
            bird = self._get_achievement("early_bird")
            if bird and not bird.unlocked:
                bird.current_progress = 1
                self._unlock(bird)

        # 周末狂战士: 周六/周日累计攻坚
        if weekday in (5, 6):
            wk = self._get_achievement("weekend_blitz")
            if wk and not wk.unlocked:
                wk.current_progress += 1
                if wk.current_progress >= wk.target_progress:
                    self._unlock(wk)

        # 3. 各专项成就累计
        if "高等数学" in event.big_title or "数学" in event.big_title:
            self._today_subjects.add("math")
            ach = self._get_achievement("math_expert")
            if ach and not ach.unlocked:
                ach.current_progress += 1
                if ach.current_progress >= ach.target_progress:
                    self._unlock(ach)

        elif "数据结构" in event.big_title or "编程" in event.big_title:
            self._today_subjects.add("coding")
            ach = self._get_achievement("ds_coder")
            if ach and not ach.unlocked:
                ach.current_progress += 1
                if ach.current_progress >= ach.target_progress:
                    self._unlock(ach)

        elif "英语" in event.big_title:
            self._today_subjects.add("english")
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

        # 4. 三位一体 (单日涵盖数学、编程、英语)
        if {"math", "coding", "english"}.issubset(self._today_subjects):
            tri = self._get_achievement("tri_mastery")
            if tri and not tri.unlocked:
                tri.current_progress = 3
                self._unlock(tri)

    def check_pomo_achievements(self, total_pomo: int):
        """番茄数阈值检查"""
        for ach_id, req in [("pomo_10", 10), ("pomo_30", 30), ("pomo_50", 50), ("pomo_100", 100)]:
            ach = self._get_achievement(ach_id)
            if ach and not ach.unlocked:
                ach.current_progress = total_pomo
                if total_pomo >= req:
                    self._unlock(ach)

    def get_unlocked_count(self) -> int:
        return sum(1 for a in self.achievements if a.unlocked)

    def get_total_count(self) -> int:
        return len(self.achievements)
