"""
QuestDesk 全局常量配置与游戏化设定
"""

from typing import Dict, List

# 四维属性分类（由学科与专业技能映射而来）
class AttributeType:
    MATH = "数学"        # 逻辑推理、高数攻坚
    CODING = "编程"      # 算法结构、底层代码
    ENGLISH = "英语"     # 语言积累、真题语感
    PRACTICE = "实践"    # 工程开发、课程项目
    REVIEW = "心智"      # 周度复盘、自律与规划

# 科目对应属性映射
TASK_ATTRIBUTE_MAP = {
    "武忠祥高等数学": AttributeType.MATH,
    "数据结构（C语言）": AttributeType.CODING,
    "考研英语": AttributeType.ENGLISH,
    "专业课复盘与实践": AttributeType.PRACTICE,
    "周度复盘与休整": AttributeType.REVIEW,
}

# 每日副标题设定（结合课表节奏）
DAY_SUBTITLES = [
    "专业课启动日", "实践动手日", "数学攻坚日",
    "深度工作日", "课程收尾日", "成长主战场", "复盘休整日"
]

# 默认属性初值
DEFAULT_ATTRIBUTES = {
    AttributeType.MATH: 0,
    AttributeType.CODING: 0,
    AttributeType.ENGLISH: 0,
    AttributeType.PRACTICE: 0,
    AttributeType.REVIEW: 0,
}

# 称号等级体系
RANK_TITLES = [
    (1, "初级探路者"),
    (3, "进阶学徒"),
    (6, "资深学者"),
    (10, "星旅探索者"),
    (15, "巅峰宗师"),
    (20, "传奇造物主"),
]

def get_rank_title(level: int) -> str:
    title = RANK_TITLES[0][1]
    for req_lvl, t in RANK_TITLES:
        if level >= req_lvl:
            title = t
        else:
            break
    return title

# 每日冒险事件包装模板（为普通任务注入 RPG 沉浸感）
EVENT_TITLE_TEMPLATES = {
    "武忠祥高等数学": [
        "🌱 智慧试炼 · 极限逻辑突围",
        "📐 算理演算 · 核心模块攻坚",
        "⚔️ 知识闭环 · 综合题型围剿",
        "🛡️ 错题除障 · 疑难死角扫除",
    ],
    "数据结构（C语言）": [
        "🧱 构造探秘 · 经典结构手写",
        "⚡ 逻辑验证 · 算法内核调试",
        "🏰 代码筑基 · 主题实现闭环",
    ],
    "考研英语": [
        "📖 词识觉醒 · 每日词汇打卡",
        "🔍 句读破阵 · 长难句深度解析",
        "📜 语感淬炼 · 历年真题攻坚",
    ],
    "专业课复盘与实践": [
        "🛠️ 实践精进 · 移动开发代码重构",
        "💻 体系梳理 · 专业理论深度复盘",
        "🧹 欠账清理 · 阻碍收尾与消解",
    ],
    "周度复盘与休整": [
        "🏛️ 贤者沉思 · Sunday 8问全周复盘",
        "🏕️ 灵能蓄能 · 状态恢复与下周蓄势",
    ]
}

# 默认预设成就表
PRESET_ACHIEVEMENTS = [
    {
        "id": "first_blood",
        "name": "初出茅庐",
        "description": "完成任意第 1 个冒险小任务",
        "icon": "🗡️",
        "category": "起步",
        "target_progress": 1,
    },
    {
        "id": "level_up_1",
        "name": "突破界限",
        "description": "角色等级首次达到 Lv.2",
        "icon": "⭐",
        "category": "成长",
        "target_progress": 2,
    },
    {
        "id": "pomo_10",
        "name": "专注学徒",
        "description": "累计完成 10 个番茄钟专注",
        "icon": "🍅",
        "category": "专注",
        "target_progress": 10,
    },
    {
        "id": "pomo_30",
        "name": "高能攻坚手",
        "description": "累计完成 30 个番茄钟专注",
        "icon": "🔥",
        "category": "专注",
        "target_progress": 30,
    },
    {
        "id": "math_expert",
        "name": "理则破障者",
        "description": "完成 5 次武忠祥高等数学攻坚任务",
        "icon": "📐",
        "category": "学术",
        "target_progress": 5,
    },
    {
        "id": "ds_coder",
        "name": "算法筑基者",
        "description": "完成 3 次数据结构手写与调试任务",
        "icon": "💻",
        "category": "学术",
        "target_progress": 3,
    },
    {
        "id": "english_persistent",
        "name": "语海远航家",
        "description": "完成 7 次考研英语打卡",
        "icon": "📜",
        "category": "学术",
        "target_progress": 7,
    },
    {
        "id": "sunday_review",
        "name": "反思之镜",
        "description": "完成一次周日 Sunday 8 问全周复盘",
        "icon": "🏛️",
        "category": "心智",
        "target_progress": 1,
    },
]
