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

DEFAULT_DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "okr_data.json")
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
    def __init__(self, filepath: str = DEFAULT_DATA_FILE):
        self.filepath = os.path.abspath(filepath)
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
            base, ext = os.path.splitext(self.filepath)
            backup = f"{base}.{int(time.time())}.bak{ext}"
            shutil.copy(self.filepath, backup)
            print(f"[Info] 损坏数据已备份至: {backup}")
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
            BigTask("math", "武忠祥高等数学", [
                st("math-tue", "做一组知识点习题", False, 40, day=1, pomo=1),
                st("math-wed", "完整攻克 1 个知识点并做题", False, 50, day=2, pomo=2),
                st("math-thu", "攻克完整模块与错题整理", False, 60, day=3, pomo=3),
                st("math-fri", "巩固练习与错题回顾", False, 40, day=4, pomo=2),
                st("math-sat", "本周数学闭环与综合练习", False, 60, day=5, pomo=3),
                st("math-sun", "数学补漏（依本周欠账选做）", False, 30, day=6, pomo=1),
            ], pomo_budget=10),
            BigTask("ds", "数据结构（C语言）", [
                st("ds-thu", "阅读严蔚敏教材，C 语言手写实现", False, 50, day=3, pomo=2),
                st("ds-fri", "算法逻辑验证与代码调试", False, 40, day=4, pomo=1),
                st("ds-sat", "完成数据结构主题实现（链表/树）", False, 60, day=5, pomo=2),
            ], pomo_budget=6),
            BigTask("en", "考研英语", [
                st("en-mon", "单词打卡", False, 30, day=0, pomo=1),
                st("en-tue", "单词与长难句分析", False, 30, day=1, pomo=1),
                st("en-wed", "单词打卡与语法巩固", False, 30, day=2, pomo=1),
                st("en-thu", "单词打卡与语法强化", False, 30, day=3, pomo=1),
                st("en-fri", "单词打卡", False, 30, day=4, pomo=1),
                st("en-sat", "真题长难句与词汇攻坚", False, 40, day=5, pomo=1),
                st("en-sun", "单词打卡与周度复习", False, 30, day=6, pomo=1),
            ], pomo_budget=7),
            BigTask("cs", "专业课复盘与实践", [
                st("cs-mon", "课程复盘：嵌入式 / JavaEE / 计网", False, 40, day=0, pomo=1),
                st("cs-tue", "移动开发实践：课堂代码重跑与功能实现", False, 50, day=1, pomo=2),
                st("cs-wed", "操作系统复盘：整理课堂理论与机制", False, 40, day=2, pomo=1),
                st("cs-fri", "专业课欠账清理：检查遗留作业与代码", False, 40, day=4, pomo=1),
            ], pomo_budget=6),
            BigTask("review", "周度复盘与休整", [
                st("rev-sun", "Sunday 8 问周度复盘清单", False, 50, day=6, pomo=2),
            ], pomo_budget=2),
        ]

        achievements = [Achievement.from_dict(p) for p in PRESET_ACHIEVEMENTS]
        self.save_data(user_stats, big_tasks, achievements)
        return user_stats, big_tasks, achievements