from datetime import datetime, date
from typing import List, Tuple, Optional, Dict

from models.task import BigTask, SmallTask, DAYS
from models.user_stats import UserStats
from storage.json_storage import JSONStorage
from services.xp_service import XPService
from services.achievement_service import AchievementService
from services.backup_service import BackupService
from events.event_bus import event_bus, TaskToggledEvent, WeeklyResetEvent, StatsUpdatedEvent
from config.constants import EVENT_TITLE_TEMPLATES, TASK_ATTRIBUTE_MAP, AttributeType


class TaskService:
    """任务核心业务服务：负责任务调度、每日事件RPG包装、打卡结算与数据一致性"""

    def __init__(self, user_stats: UserStats, big_tasks: List[BigTask], storage: JSONStorage,
                 xp_service: XPService, achievement_service: AchievementService, backup_service: BackupService):
        self.user_stats = user_stats
        self.big_tasks = big_tasks
        self.storage = storage
        self.xp = xp_service
        self.achievements = achievement_service
        self.backup = backup_service

    def get_today_weekday(self) -> int:
        return datetime.today().weekday()

    def get_today_event_tasks(self) -> List[Dict]:
        """
        获取今日冒险事件清单，并为每个小任务注入 RPG 试炼包装
        """
        today = self.get_today_weekday()
        events = []

        for b_idx, big in enumerate(self.big_tasks):
            today_small_tasks = [t for t in big.tasks if t.day == today or t.day is None]
            templates = EVENT_TITLE_TEMPLATES.get(big.title, ["⚔️ 专属试炼 · 专注攻坚"])
            attr = TASK_ATTRIBUTE_MAP.get(big.title, AttributeType.PRACTICE)

            for s_idx, task in enumerate(today_small_tasks):
                # 依据科目与任务序号挑选 RPG 试炼标题
                rpg_title = templates[s_idx % len(templates)]
                events.append({
                    "big_id": big.id,
                    "big_title": big.title,
                    "task": task,
                    "rpg_event_title": rpg_title,
                    "attribute": attr,
                    "reward_desc": f"+{task.xp} XP · +{task.xp} {attr}点",
                })
        return events

    def toggle_task(self, big_id: str, task_id: str, done: bool = True) -> Tuple[bool, bool]:
        """
        完成小任务（单向点击，不可取消）：
        返回: (task_found, is_big_completed)
        """
        big, task = self._find_task(big_id, task_id)
        if not big or not task:
            return False, False

        # 如果任务已经处于完成且已结算状态，或者试图传入 done=False 取消，直接拒绝并不做任何变更
        if (task.done and task.awarded) or not done:
            return False, False

        was_big_completed = big.completed
        task.done = True

        if not task.awarded:
            task.awarded = True
            self.xp.award_task_rewards(big.title, task.xp, task.pomo)
            # 检查番茄成就
            total_weekly_pomo = sum(t.pomo for b in self.big_tasks for t in b.tasks if t.done)
            self.achievements.check_pomo_achievements(total_weekly_pomo)
            if big.completed and not was_big_completed:
                self.user_stats.total_big_tasks_done += 1

        attr = TASK_ATTRIBUTE_MAP.get(big.title, AttributeType.PRACTICE)
        event_bus.publish(TaskToggledEvent(
            big_id=big.id,
            small_id=task.id,
            done=True,
            gained_xp=task.xp,
            attribute=attr,
            pomo=task.pomo,
            task_title=task.title,
            big_title=big.title,
        ))

        self.save()
        return True, (big.completed and not was_big_completed)

    def log_free_exploration(self, pomos: int, attribute: str, topic: str = "") -> Tuple[bool, int]:
        """记录自由探索（主动投入学习资源），发放对应经验与属性点，并保存数据"""
        leveled_up, xp = self.xp.award_free_exploration(pomos, attribute, topic)
        total_pomo = self.user_stats.total_pomo_history
        self.achievements.check_pomo_achievements(total_pomo)
        self.save()
        return leveled_up, xp

    def get_today_focus_summary(self) -> Dict[str, int]:
        """今日双轨番茄学习投入统计（基于小任务实际数据计算，彻底杜绝重置后重复计算）"""
        today = self.get_today_weekday()
        today_tasks = [t for b in self.big_tasks for t in b.tasks if (t.day == today or t.day is None)]
        task_target = sum(t.pomo for t in today_tasks)
        task_done = sum(t.pomo for t in today_tasks if t.done)
        free_done = self.user_stats.free_pomo_today
        return {
            "task_done": task_done,
            "task_target": task_target,
            "free_done": free_done,
            "total_pomo": task_done + free_done,
        }

    def get_week_focus_summary(self) -> Dict[str, int]:
        """本周双轨番茄学习投入统计（基于全周小任务所需番茄之和动态计算）"""
        week_target = sum(t.pomo for b in self.big_tasks for t in b.tasks)
        week_done = sum(t.pomo for b in self.big_tasks for t in b.tasks if t.done)
        free_done = self.user_stats.free_pomo_week
        return {
            "task_done": week_done,
            "task_target": week_target,
            "free_done": free_done,
            "total_pomo": week_done + free_done,
        }

    def get_today_focus_percentage(self) -> int:
        """计算今日主线任务专注完成率 (今日已攻克小任务番茄 / 今日计划小任务番茄)"""
        today = self.get_today_weekday()
        today_tasks = [t for b in self.big_tasks for t in b.tasks if (t.day == today or t.day is None)]
        target = sum(t.pomo for t in today_tasks)
        if target <= 0:
            return 100
        done = sum(t.pomo for t in today_tasks if t.done)
        return min(100, int(done / target * 100))

    def get_today_growth_count(self) -> int:
        """今日完成的试炼任务总数"""
        today = self.get_today_weekday()
        return sum(1 for b in self.big_tasks for t in b.tasks if (t.day == today and t.done))

    def perform_weekly_reset(self):
        """执行周度复盘与一键重置"""
        self.backup.create_snapshot(tag="pre_weekly_reset")
        for big in self.big_tasks:
            for task in big.tasks:
                task.done = False
                task.awarded = False

        self.xp.reset_weekly_growth()
        self.save()
        event_bus.publish(WeeklyResetEvent())

    def check_cross_day(self):
        """跨天检查：自动重置今日任务番茄与今日自由探索番茄"""
        today_str = date.today().isoformat()
        if self.user_stats.last_active_date != today_str:
            self.user_stats.task_pomo_today = 0
            self.user_stats.free_pomo_today = 0
            self.user_stats.last_active_date = today_str
            self.user_stats.streak_days += 1
            self.save()
            event_bus.publish(StatsUpdatedEvent(user_stats=self.user_stats))

    def save(self):
        """保存全量数据"""
        self.storage.save_data(self.user_stats, self.big_tasks, self.achievements.achievements)

    def _find_task(self, big_id: str, task_id: str) -> Tuple[Optional[BigTask], Optional[SmallTask]]:
        for big in self.big_tasks:
            if big.id == big_id:
                for task in big.tasks:
                    if task.id == task_id:
                        return big, task
        return None, None
