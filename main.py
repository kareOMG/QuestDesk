import os
import sys

# 将当前项目根目录加入 sys.path，确保可相对导入
if getattr(sys, "frozen", False):
    BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    # 确保 Windows 下 PySide6 与 shiboken6 专属动态库目录优先正确载入
    for sub in ["", "PySide6", "shiboken6"]:
        dll_dir = os.path.join(BASE_DIR, sub)
        if os.path.isdir(dll_dir) and hasattr(os, "add_dll_directory"):
            try:
                os.add_dll_directory(dll_dir)
            except Exception:
                pass
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    import PySide6
    plugin_path = os.path.join(os.path.dirname(PySide6.__file__), "plugins", "platforms")
    os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

sys.path.insert(0, BASE_DIR)

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from storage.json_storage import JSONStorage
from ui.floating_window import FloatingWindow


def main():
    # 设置 Windows 独立的 AppUserModelID，确保任务栏独立显示专属应用图标
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kareOMG.QuestDesk.Product.v1")
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setApplicationName("QuestDesk")

    # 设置任务栏与全局窗口图标（优先 logo.ico，备选 logo.png）
    ico_path = os.path.join(BASE_DIR, "assets", "logo.ico")
    png_path = os.path.join(BASE_DIR, "assets", "logo.png")
    icon_path = ico_path if os.path.exists(ico_path) else png_path
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    storage = JSONStorage()
    window = FloatingWindow(storage)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()