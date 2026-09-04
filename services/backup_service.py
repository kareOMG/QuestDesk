import os
import shutil
import time


class BackupService:
    """数据安全与自动快照备份服务"""

    def __init__(self, data_file_path: str, backup_dir: str = None):
        self.data_file_path = os.path.abspath(data_file_path)
        self.backup_dir = backup_dir or os.path.join(os.path.dirname(self.data_file_path), "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_snapshot(self, tag: str = "auto") -> str:
        """创建当前数据快照"""
        if not os.path.exists(self.data_file_path):
            return ""
        try:
            ts = time.strftime("%Y%m%d_%H%M%S")
            filename = f"okr_data_{tag}_{ts}.json"
            target = os.path.join(self.backup_dir, filename)
            shutil.copy2(self.data_file_path, target)
            self._prune_old_backups(keep=15)
            return target
        except OSError as e:
            print(f"[BackupService Warning] 创建快照失败: {e}")
            return ""

    def backup_corrupt_file(self) -> str:
        """备份异常损坏文件"""
        if not os.path.exists(self.data_file_path):
            return ""
        try:
            ts = int(time.time())
            target = os.path.join(self.backup_dir, f"corrupt_{ts}.json")
            shutil.copy2(self.data_file_path, target)
            return target
        except OSError as e:
            print(f"[BackupService Warning] 损坏备份失败: {e}")
            return ""

    def _prune_old_backups(self, keep: int = 15):
        """保留最近指定份数的备份，清理旧文件"""
        try:
            files = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir) if f.endswith(".json")]
            files.sort(key=os.path.getmtime)
            while len(files) > keep:
                oldest = files.pop(0)
                os.remove(oldest)
        except OSError:
            pass
