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

# 默认预设成就表（丰富多类别体系：起步、成长、专注、学术、坚韧、心智、彩蛋）
PRESET_ACHIEVEMENTS = [
    # --- 起步与破冰 ---
    {
        "id": "first_blood",
        "name": "初出茅庐",
        "description": "完成任意第 1 个冒险小任务",
        "icon": "🗡️",
        "category": "起步",
        "target_progress": 1,
    },

    # --- 等级与进阶 ---
    {
        "id": "level_up_1",
        "name": "突破界限",
        "description": "角色等级首次达到 Lv.2",
        "icon": "⭐",
        "category": "成长",
        "target_progress": 2,
    },
    {
        "id": "level_5",
        "name": "资深学者",
        "description": "角色等级突破至 Lv.5",
        "icon": "🎖️",
        "category": "成长",
        "target_progress": 5,
    },
    {
        "id": "level_10",
        "name": "星旅探索者",
        "description": "角色等级突破至 Lv.10",
        "icon": "👑",
        "category": "成长",
        "target_progress": 10,
    },

    # --- 专注与心流 ---
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
        "id": "pomo_50",
        "name": "心流大师",
        "description": "累计完成 50 个番茄钟专注",
        "icon": "🔮",
        "category": "专注",
        "target_progress": 50,
    },
    {
        "id": "pomo_100",
        "name": "时间领主",
        "description": "累计完成 100 个番茄钟专注",
        "icon": "⏳",
        "category": "专注",
        "target_progress": 100,
    },

    # --- 学术与专项攻坚 ---
    {
        "id": "math_expert",
        "name": "理则破障者",
        "description": "完成 5 次高等数学攻坚任务",
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
        "id": "tri_mastery",
        "name": "三位一体",
        "description": "单日内攻破高数、数据结构、英语各至少一项任务",
        "icon": "🔱",
        "category": "学术",
        "target_progress": 3,
    },

    # --- 战役与毅力 ---
    {
        "id": "all_daily_clear",
        "name": "全境肃清",
        "description": "达成今日所有预定试炼全数攻克",
        "icon": "🎯",
        "category": "战役",
        "target_progress": 1,
    },
    {
        "id": "streak_3",
        "name": "坚毅之步",
        "description": "连续打卡完成任务达到 3 天",
        "icon": "⚡",
        "category": "坚韧",
        "target_progress": 3,
    },
    {
        "id": "streak_7",
        "name": "七日之誓",
        "description": "连续打卡完成任务达到 7 天",
        "icon": "🛡️",
        "category": "坚韧",
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

    # --- 隐秘与彩蛋 ---
    {
        "id": "logo_tapper_10",
        "name": "好奇心害死猫",
        "description": "连续敲击主界面 Logo 徽记 10 次，发现隐藏小机关！",
        "icon": "🐾",
        "category": "彩蛋",
        "target_progress": 10,
        "clue": "主界面的徽记似乎有微弱的灵能反应...敲击试试？",
    },
    {
        "id": "night_owl",
        "name": "夜巡游侠",
        "description": "在深夜 23:00 之后完成一次攻坚打卡",
        "icon": "🦉",
        "category": "彩蛋",
        "target_progress": 1,
        "clue": "在万籁俱寂的深宵，仍有未熄灭的星火...",
    },
    {
        "id": "early_bird",
        "name": "晨曦先驱",
        "description": "在清晨 07:00 之前完成一次晨间任务",
        "icon": "🌅",
        "category": "彩蛋",
        "target_progress": 1,
        "clue": "黎明破晓前，第一缕晨光与笔尖的沙沙声...",
    },
    {
        "id": "weekend_blitz",
        "name": "周末狂战士",
        "description": "在周末（周六或周日）攻克 3 个及以上任务",
        "icon": "⚔️",
        "category": "彩蛋",
        "target_progress": 3,
        "clue": "即便是在休整的周末，猎犬也从未停下追逐...",
    },
]
