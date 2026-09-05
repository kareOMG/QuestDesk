"""
QuestDesk - 核心路径与运行时环境管理中枢 (core/paths.py)
统一负责源码运行与 PyInstaller 打包环境下的路径推导、数据隔离与动态链接库环境补丁。
"""

import sys
import os
import shutil
from pathlib import Path


def is_frozen() -> bool:
    """判断当前程序是否处于 PyInstaller 打包脱机运行状态。"""
    return getattr(sys, "frozen", False)


def get_app_root() -> Path:
    """
    获取应用程序的静态只读资源根目录。
    - 打包运行 (frozen)：指向 sys._MEIPASS (解压只读临时目录)
    - 源码运行：指向项目根目录 (即 core/ 的父目录)
    """
    if is_frozen():
        return Path(getattr(sys, "_MEIPASS", os.path.dirname(sys.executable)))
    return Path(__file__).resolve().parent.parent


def get_data_dir() -> Path:
    """
    获取持久化可写数据目录。
    - 打包运行 (frozen)：指向可执行文件所在的真实外部目录下的 data 文件夹（保证用户数据永久保存，关闭不丢失）
    - 源码运行：指向项目根目录下的 data 文件夹
    """
    if is_frozen():
        base = Path(sys.executable).resolve().parent
    else:
        base = get_app_root()
    data_path = base / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path


def get_data_file() -> Path:
    """获取用户 OKR 数据文件 (data/okr_data.json) 的完整绝对路径。"""
    data_file = get_data_dir() / "okr_data.json"
    
    # 打包运行首次启动时，若外部不存在 okr_data.json，但内置包中随附了初始/模板数据，则优雅拷贝
    if is_frozen() and not data_file.exists():
        embedded_template = get_app_root() / "data" / "okr_data.json"
        if embedded_template.exists():
            try:
                shutil.copy2(embedded_template, data_file)
            except Exception as e:
                print(f"[paths] 初始化用户数据模板失败: {e}", file=sys.stderr)
                
    return data_file


def get_backups_dir() -> Path:
    """获取数据安全自动备份目录 (data/backups/)。"""
    backups_path = get_data_dir() / "backups"
    backups_path.mkdir(parents=True, exist_ok=True)
    return backups_path


def get_assets_dir() -> Path:
    """获取静态只读资源根目录 (assets/)。"""
    return get_app_root() / "assets"


def get_icons_dir() -> Path:
    """获取图标资源目录 (assets/icons/)。"""
    return get_assets_dir() / "icons"


def get_sounds_dir() -> Path:
    """获取音频音效资源目录 (assets/sounds/)。"""
    return get_assets_dir() / "sounds"


def get_config_dir() -> Path:
    """获取静态配置文件目录 (config/)。"""
    return get_app_root() / "config"


def get_logo_path() -> Path:
    """获取应用主 Logo 路径 (优先 logo.png，备用 logo.ico)。"""
    for p in [get_icons_dir() / "logo.png", get_assets_dir() / "logo.png", get_icons_dir() / "logo.ico", get_assets_dir() / "logo.ico"]:
        if p.exists():
            return p
    return get_icons_dir() / "logo.png"


def init_runtime_environment():
    """
    运行时底层依赖补丁注入：
    1. 打包环境 (frozen)：注入 _MEIPASS 动态库目录，防止 Anaconda 等系统 PATH 劫持旧版 icu*.dll 导致 127 错误。
    2. 源码环境：显式注入 Qt platform 插件路径，防止 Linux/macOS/Windows 下某些环境插件探测异常。
    """
    if sys.platform == "win32":
        if is_frozen():
            base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
            for sub in ["", "PySide6", "shiboken6"]:
                d = os.path.join(base, sub)
                if os.path.isdir(d) and hasattr(os, "add_dll_directory"):
                    try:
                        os.add_dll_directory(d)
                    except Exception:
                        pass
        else:
            try:
                base_dir = os.path.dirname(sys.executable)
                if hasattr(os, "add_dll_directory") and os.path.exists(base_dir):
                    os.add_dll_directory(base_dir)
            except Exception:
                pass

    if not is_frozen():
        try:
            import PySide6
            plugin_path = os.path.join(os.path.dirname(PySide6.__file__), "plugins", "platforms")
            if os.path.exists(plugin_path):
                os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path
        except Exception:
            pass
