import os
import sys

# 修正 Windows 下 Qt 平台插件路径识别问题
import PySide6
plugin_path = os.path.join(os.path.dirname(PySide6.__file__), "plugins", "platforms")
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = plugin_path

# 将当前项目根目录加入 sys.path，确保可相对导入
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication

from storage.json_storage import JSONStorage
from ui.floating_window import FloatingWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("QuestDesk")

    storage = JSONStorage()
    window = FloatingWindow(storage)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()