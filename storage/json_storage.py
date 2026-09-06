import json
import os
import re
import shutil
import time
from typing import Tuple, List, Optional

from models.user_stats import UserStats
from models.task import BigTask, SmallTask
from models.achievement import Achievement
from config.constants import PRESET_ACHIEVEMENTS

from core.paths import get_data_file, get_backups_dir

SCHEMA_VERSION = 3

_leading_emoji = re.compile(
    u'^[' u'\U0001F000-\U0001FAFF' u'\U00002190-\U00002BFF'
    u'\U00002600-\U000027BF' u'\U0000FE00-\U0000FE0F' u'\U0001F1E6-\U0001F1FF' u']+'
)


def _strip_leading_emoji(s: str):
    if not s:
        return s
    return _leading_emoji.sub('', s).lstrip()


class JSONStorage:
    def __init__(self, filepath: Optional[str] = None):
        self.filepath = os.path.abspath(filepath) if filepath else str(get_data_file())
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)

    def load_data(self) -> Tuple[UserStats, List[BigTask], List[Achievement]]:
        """读取数据；文件缺失自动初始化；支持 UserStats、BigTask 与成就系统持久化"""
        if not os.path.exists(self.filepath):
            return self._create_default_data()

        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            print(f"[Warning] 数据读取异常，已备份损坏文件并恢复默认数据: {e}")
            self._backup_corrupt_file()
            return self._create_default_data()

        user_stats = UserStats.from_dict(raw_data.get("user_stats", {}))

        big_tasks = [BigTask.from_dict(b) for b in raw_data.get("big_tasks", [])]
        for b in big_tasks:
            b.title = _strip_leading_emoji(b.title)

        # 加载成就列表
        ach_raw = raw_data.get("achievements", [])
        if ach_raw:
            achievements = [Achievement.from_dict(a) for a in ach_raw]
        else:
            achievements = [Achievement.from_dict(p) for p in PRESET_ACHIEVEMENTS]

        return user_stats, big_tasks, achievements

    def save_data(self, user_stats: UserStats, big_tasks: List[BigTask], achievements: Optional[List[Achievement]] = None):
        if achievements is None:
            # 读取既有成就避免覆盖丢失
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    achievements_raw = json.load(f).get("achievements", [])
            except Exception:
                achievements_raw = PRESET_ACHIEVEMENTS
        else:
            achievements_raw = [a.to_dict() for a in achievements]

        data = {
            "version": SCHEMA_VERSION,
            "user_stats": user_stats.to_dict(),
            "big_tasks": [b.to_dict() for b in big_tasks],
            "achievements": achievements_raw,
        }
        with open(self.filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def reset_data(self) -> Tuple[UserStats, List[BigTask], List[Achievement]]:
        """放弃当前进度，恢复为默认示例数据"""
        return self._create_default_data()

    def _backup_corrupt_file(self):
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = get_backups_dir() / f"okr_data_corrupt_{timestamp}.json"
            shutil.copy2(self.filepath, str(backup_path))
            print(f"[Info] 损坏数据已备份至: {backup_path}")
        except OSError as e:
            print(f"[Warning] 备份失败: {e}")

    # ---------- 默认数据 ----------
    def _create_default_data(self) -> Tuple[UserStats, List[BigTask], List[Achievement]]:
        user_stats = UserStats(
            level=1, current_xp=0, next_level_xp=500,
            overall_progress=0, window_opacity=0.95,
            day_target=[3, 4, 4, 6, 5, 6, 3]
        )

        def st(id_: str, title: str, done: bool = False, xp: int = 30, day=None, pomo: int = 1) -> SmallTask:
            return SmallTask(id=id_, title=title, done=done, xp=xp, awarded=done, day=day, pomo=pomo)

        big_tasks = [
            BigTask("math", "高等数学", [
                st("math-tue", "极限与微分学核心例题演算", False, 40, day=1, pomo=1),
                st("math-wed", "定积分与微分方程重点攻坚", False, 50, day=2, pomo=2),
                st("math-thu", "多元函数与级数核心考点突破", False, 60, day=3, pomo=2),
                st("math-fri", "经典例题变式训练与疑难排查", False, 40, day=4, pomo=1),
                st("math-sat", "本周数学模块综合练习与模拟", False, 60, day=5, pomo=2),
                st("math-sun", "数学错题闭环与公式速查复盘", False, 30, day=6, pomo=1),
            ], pomo_budget=9),
            BigTask("ds", "数据结构与算法", [
                st("ds-thu", "经典线性表与树形结构算法手写", False, 50, day=3, pomo=2),
                st("ds-fri", "图论与动态规划算法逻辑验证", False, 40, day=4, pomo=1),
                st("ds-sat", "高频面试算法题自测与代码重构", False, 60, day=5, pomo=2),
            ], pomo_budget=5),
            BigTask("en", "外语读写与学术积累", [
                st("en-mon", "核心高频学术词汇打卡 50 词", False, 30, day=0, pomo=1),
                st("en-tue", "经典外刊长难句精读与语法解析", False, 30, day=1, pomo=1),
                st("en-wed", "学术听力与跟读训练 30 分钟", False, 30, day=2, pomo=1),
                st("en-thu", "专业外语文献深度速读与摘要", False, 30, day=3, pomo=1),
                st("en-fri", "真题阅读理解精炼与生词归纳", False, 30, day=4, pomo=1),
                st("en-sat", "学术写作句型仿写与词汇巩固", False, 40, day=5, pomo=1),
                st("en-sun", "全周生词本盲测与周度复盘", False, 30, day=6, pomo=1),
            ], pomo_budget=7),
            BigTask("cs", "专业实践与项目构建", [
                st("cs-mon", "项目架构设计与核心模块规划", False, 40, day=0, pomo=1),
                st("cs-tue", "核心接口开发与功能逻辑实现", False, 50, day=1, pomo=2),
                st("cs-wed", "单元测试编写与代码质量检查", False, 40, day=2, pomo=1),
                st("cs-fri", "项目文档撰写与遗留问题清理", False, 40, day=4, pomo=1),
            ], pomo_budget=5),
            BigTask("review", "周度复盘与休整", [
                st("rev-sun", "Sunday 8 问全周深度复盘清单", False, 50, day=6, pomo=2),
            ], pomo_budget=2),
        ]

        achievements = [Achievement.from_dict(p) for p in PRESET_ACHIEVEMENTS]
        self.save_data(user_stats, big_tasks, achievements)
        return user_stats, big_tasks, achievements