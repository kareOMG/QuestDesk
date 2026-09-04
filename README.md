<div align="center">

# ⚔️ QuestDesk · 个人学习与成长桌面 RPG 悬浮工作台

**OKR 定方向 ｜ Quest 定行动 ｜ 结果定沉淀**

把日常枯燥的考研、自律、代码与学业日程，化作指尖沉浸式的桌面级 RPG 冒险。

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52?style=flat-square&logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![License](https://img.shields.io/badge/License-MIT-amber?style=flat-square)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)](#)

</div>

---

## 📖 简介 (Overview)

**QuestDesk** 是一款专为终身学习者、考研攻坚党及程序员打造的**轻量化桌面 RPG 悬浮学习终端**。

传统打卡软件往往充斥着冰冷的 KPI 压力，而 QuestDesk 采用**「自然浮动 + 关键结果补偿」**哲学：
- **拒绝死板的强制打卡**：以周为单位进行节奏编排（专业课启动、数学攻坚、深度工作等），允许日常学习时间自然浮动。
- **资源化番茄投入**：番茄钟不再只是倒计时工具，而是你可以自由投资到“主线任务攻坚”或“未知自由探索”中的成长资源。
- **全要素游戏化反馈**：每次小任务攻关、每段番茄专注，都会化作角色经验（EXP）、五维能力属性点与成就徽章，让长期的复习积累可视化、可感知。

---

## ✨ 核心特性 (Key Features)

### 1. 🎮 沉浸式 RPG 角色与能力成长
- **阶梯称号体系**：从 `Lv.1 初级探路者`、`进阶学徒`，一路突破至 `星旅探索者`、`传奇造物主`。
- **五维学识属性**：
  - 📐 **数学**（逻辑推理、公式推导）
  - 💻 **编程**（算法构造、底层工程）
  - 📖 **英语**（词汇积累、长难句语感）
  - 🛠️ **实践**（课程项目、动手闭环）
  - 🏛️ **心智**（周度复盘、自律规划）
- **每日冒险事件包装**：自动将普通的做题、背单词转化为「🌱 智慧试炼 · 极限逻辑突围」、「📐 算理演算 · 核心模块攻坚」等沉浸式史诗任务。

### 2. 📅 智能 OKR 周度排期管理
- **周一至周日节奏编排**：依据脑力与课程负荷定制专属副标题与主线科目。
- **胶囊排期卡片**：大任务模块（如武忠祥高等数学、数据结构）搭配精炼的小任务清单，清晰呈现完成进度（`done/total`）与番茄预算。
- **周度复盘与一键重置**：每周日支持「一键结转沉淀」，重置小任务勾选状态开启新一周，同时大任务结构、累积专注度与历史成就永久保留。

### 3. 🍅 双轨专注投入系统
- **主线攻坚番茄**：与具体小任务绑定，完成后直接计入对应科目的专注沉淀。
- **自由探索模式**：支持随时随地开启一段轻量化自由专注，记录临时自习与发散研究，同样收获成长经验。

### 4. 🏆 成就殿堂与即时荣誉弹窗
- 内置数十项阶段成就（初出茅庐、专注先锋、全周闭环、五维学者等）。
- 达成目标即刻弹出全特效荣誉结算卡片，记录每一个拼搏里程碑。

### 5. 🪟 极致美学与原生桌面体验
- **暖炭磨砂玻璃（Charcoal Frosted Glass）泛美学**：全局杜绝高饱和度蓝光与刺眼纯白，柔和护眼。
- **无感边缘八向拉伸**：支持窗口四周及四角任意拖拽缩放，内置智能防死锁最小尺寸保护。
- **无级透明度调节**：35% ~ 100% 自由预览调节，既可融入桌面壁纸，也能纯色专注。
- **便捷交互**：支持顶部快速贴边、一键隐藏/唤出托盘、置顶切换与右下角 SizeGrip 调整。

---

## 🗂️ 目录结构 (Directory Structure)

```text
QuestDesk/
├── assets/                  # 静态资源
│   └── icons/               # 武器、头盔、书本、图鉴等游戏化高保真矢量图标
├── config/                  # 全局配置与常量
│   └── constants.py         # 五维属性、等级称号映射、每日事件模板与成就预设
├── data/                    # 本地数据存储与快照
│   ├── okr_data.json        # 核心用户数据（任务、经验、番茄、成就等）
│   └── backups/             # 自动轮转数据快照备份
├── events/                  # 事件总线解耦层
│   └── event_bus.py         # 发布-订阅式事件分发中心
├── models/                  # 核心数据实体模型
│   ├── task.py              # 大任务（BigTask）与小任务（SmallTask）
│   ├── user_stats.py        # 角色属性、等级、经验值与专注统计
│   └── achievement.py       # 成就定义与进度跟踪
├── services/                # 业务逻辑服务层
│   ├── task_service.py      # 任务调度、周度复盘与每日事件生成
│   ├── xp_service.py        # 经验计算与升级判定
│   ├── achievement_service.py # 成就解锁触发监听
│   └── backup_service.py    # 数据版本自动快照机制
├── storage/                 # 数据持久化接口
│   └── json_storage.py      # JSON 文件的原子级安全读写
├── ui/                      # 基于 PySide6 的现代化 UI 界面
│   ├── floating_window.py   # 悬浮主窗口基类（无边框、磨砂毛玻璃、拖拽吸附）
│   ├── rpg_dashboard.py     # 冒险仪表盘（等级、五维雷达图、每日事件）
│   ├── task_widget.py       # 周排期任务卡片与清单小组件
│   ├── settings_dialog.py   # 任务管理、账号统计与外观设置弹窗
│   ├── free_exploration_dialog.py # 自由探索专注倒计时面板
│   ├── achievement_widget.py# 荣誉徽章与成就展示网格
│   ├── toast_dialog.py      # 升级结算、成就解锁与确认对话框
│   ├── icon_helper.py       # 图标着色与字符清洗适配器
│   └── styles.py            # 全局 QSS 样式表与单主题色彩空间（PALETTE）
├── main.py                  # 应用程序启动入口
└── requirements.txt         # 项目依赖声明
```

---

## 🚀 快速开始 (Getting Started)

### 环境依赖
- Python 3.10 或更高版本
- Windows 10/11、macOS 或主流 Linux 发行版

### 1. 克隆仓库
```bash
git clone https://github.com/kareOMG/QuestDesk.git
cd QuestDesk
```

### 2. 创建并激活虚拟环境（推荐）
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖包
```bash
pip install -r requirements.txt
```

### 4. 启动运行
```bash
python main.py
```

---

## 🛠️ 键盘与快捷交互 (Shortcuts & Interactions)

| 交互动作 | 作用说明 |
| :--- | :--- |
| **按住窗口顶部拖拽** | 自由移动桌面悬浮窗 |
| **拖拽窗口边缘/四角** | 实时拉伸调整长宽，自适应内容展示 |
| **点击小任务圆圈** | 标记攻克完成，自动结算经验与番茄点数 |
| **周度复盘与一键重置** | 每周结算并清空勾选状态，开启新一周冒险 |
| **设置 -> 外观** | 无级调节面板背景不透明度（35% ~ 100%） |

---

## 🛡️ 开源协议 (License)

本项目采用 [MIT 许可证](LICENSE) 进行开源。欢迎提交 Issue 或 Pull Request，一起让 QuestDesk 变得更加强大有趣！