"""
QuestDesk - 桌面端 RPG 沉浸式任务与个人成长系统
主程序入口 (main.py)
"""

import sys
import os

# 1. 运行时底层依赖与环境补丁初始化（必须在导入 PySide6 之前执行）
from core.paths import init_runtime_environment, get_app_root
init_runtime_environment()

# 2. 注册项目根目录至 sys.path
sys.path.insert(0, str(get_app_root()))

from PySide6.QtWidgets import QApplication
from ui.ui_utils import load_app_icon
from storage.json_storage import JSONStorage
from ui.floating_window import FloatingWindow


def main():
    # 设置 Windows 专属 AppUserModelID，使任务栏具备独立进程图标与分组
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kareOMG.QuestDesk.Product.v1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    app.setApplicationName("QuestDesk")
    app.setWindowIcon(load_app_icon())

    storage = JSONStorage()
    window = FloatingWindow(storage)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()