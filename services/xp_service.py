from typing import Tuple
from models.user_stats import UserStats
from events.event_bus import event_bus, LevelUpEvent, StatsUpdatedEvent
from config.constants import TASK_ATTRIBUTE_MAP, AttributeType


class XPService:
    """经验值结算与属性点成长服务（支持双轨番茄体系）"""

    FREE_EXPLORATION_XP_PER_POMO = 15  # 自由探索每个番茄给予 15 XP（低于主线任务的 30~50 XP，防刷机制）

    def __init__(self, user_stats: UserStats):
        self.user_stats = user_stats

    def award_task_rewards(self, big_title: str, xp: int, pomo: int) -> bool:
        """
        为勾选完成的小任务（主线推进）发放奖励：
        1. 累计经验值与等级升级判定
        2. 获得学科专属属性成长点数 (按 100% 经验转化为属性点)
        3. 累计任务番茄（今日、本周、历史累计）
        """
        # 1. 属性点归属判定
        attr_name = TASK_ATTRIBUTE_MAP.get(big_title, AttributeType.PRACTICE)
        self.user_stats.add_attribute_point(attr_name, xp)

        # 2. 任务番茄资源累计与完成次数
        self.user_stats.task_pomo_today += pomo
        self.user_stats.task_pomo_week += pomo
        self.user_stats.task_pomo_total += pomo
        self.user_stats.total_small_tasks_done += 1

        # 3. 经验值结算与升级判定
        leveled_up = self.user_stats.add_xp(xp)

        if leveled_up:
            event_bus.publish(LevelUpEvent(new_level=self.user_stats.level, total_xp=self.user_stats.total_xp))

        event_bus.publish(StatsUpdatedEvent(user_stats=self.user_stats))
        return leveled_up

    def revoke_task_rewards(self, big_title: str, xp: int, pomo: int):
        """取消勾选时扣减属性与任务番茄（防刷机制：历史总经验不倒扣，但属性与番茄同步修正）"""
        attr_name = TASK_ATTRIBUTE_MAP.get(big_title, AttributeType.PRACTICE)
        current_attr = self.user_stats.weekly_attributes.get(attr_name, 0)
        self.user_stats.weekly_attributes[attr_name] = max(0, current_attr - xp)

        self.user_stats.task_pomo_today = max(0, self.user_stats.task_pomo_today - pomo)
        self.user_stats.task_pomo_week = max(0, self.user_stats.task_pomo_week - pomo)
        self.user_stats.task_pomo_total = max(0, self.user_stats.task_pomo_total - pomo)
        event_bus.publish(StatsUpdatedEvent(user_stats=self.user_stats))

    def award_free_exploration(self, pomos: int, attribute: str, topic: str = "") -> Tuple[bool, int]:
        """
        发放自由探索（计划外学习/阅读/查阅资料/探索新技术）奖励：
        1. 给予较低权重的经验奖励（防刷经验）
        2. 提升对应属性沉淀
        3. 累计自由探索番茄（今日、本周、历史累计）
        返回: (是否升级, 获得经验值)
        """
        xp_gain = pomos * self.FREE_EXPLORATION_XP_PER_POMO

        # 1. 对应属性成长
        if attribute in self.user_stats.weekly_attributes:
            self.user_stats.add_attribute_point(attribute, xp_gain)
        else:
            self.user_stats.add_attribute_point(AttributeType.PRACTICE, xp_gain)

        # 2. 自由探索番茄累计
        self.user_stats.free_pomo_today += pomos
        self.user_stats.free_pomo_week += pomos
        self.user_stats.free_pomo_total += pomos

        # 3. 经验值结算与升级判定
        leveled_up = self.user_stats.add_xp(xp_gain)

        if leveled_up:
            event_bus.publish(LevelUpEvent(new_level=self.user_stats.level, total_xp=self.user_stats.total_xp))

        event_bus.publish(StatsUpdatedEvent(user_stats=self.user_stats))
        return leveled_up, xp_gain

    def reset_weekly_growth(self):
        """周度复盘重置本周属性成长与本周番茄投入数值（历史累计永久保留）"""
        self.user_stats.task_pomo_week = 0
        self.user_stats.free_pomo_week = 0
        self.user_stats.reset_weekly_attributes()
        event_bus.publish(StatsUpdatedEvent(user_stats=self.user_stats))
