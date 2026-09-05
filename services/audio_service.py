import os
import math
import wave
import struct
from events.event_bus import (
    event_bus, TaskToggledEvent, LevelUpEvent, AchievementUnlockedEvent,
    AllDailyTasksCompletedEvent
)

try:
    import winsound
except ImportError:
    winsound = None


class AudioService:
    """极简无依赖音频服务：为任务攻克、角色升级、大任务完成与成就解锁提供轻柔音效"""

    @staticmethod
    def _get_sounds_dir() -> str:
        import sys
        if getattr(sys, "frozen", False):
            internal = os.path.join(getattr(sys, "_MEIPASS", ""), "assets", "sounds")
            if os.path.exists(internal):
                return internal
            return os.path.join(os.path.dirname(sys.executable), "assets", "sounds")
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "sounds")

    def __init__(self, enabled: bool = True):
        self.SOUNDS_DIR = self._get_sounds_dir()
        self.enabled = enabled
        self._ensure_sound_files()
        self._subscribe_events()

    def _ensure_sound_files(self):
        """若音频文件不存在，通过纯原生数学采样生成 44.1kHz 16-bit 温和纯净音效"""
        os.makedirs(self.SOUNDS_DIR, exist_ok=True)
        files = {
            "task_done.wav": ([(523.25, 0.00, 0.22, 0.70), (659.25, 0.04, 0.26, 0.75)], 0.26),
            "level_up.wav": ([(523.25, 0.00, 0.18, 0.6), (659.25, 0.12, 0.30, 0.7), (783.99, 0.24, 0.45, 0.8), (1046.50, 0.36, 0.75, 0.95)], 0.80),
            "quest_complete.wav": ([(440.0, 0.00, 0.35, 0.6), (554.37, 0.08, 0.42, 0.7), (659.25, 0.16, 0.52, 0.85), (880.0, 0.24, 0.70, 0.95)], 0.75),
            "achievement.wav": ([(1046.5, 0.00, 0.20, 0.6), (1318.5, 0.08, 0.28, 0.75), (1567.98, 0.16, 0.45, 0.9)], 0.50),
        }

        for filename, (notes, duration) in files.items():
            path = os.path.join(self.SOUNDS_DIR, filename)
            if not os.path.exists(path):
                self._synthesize_chime(path, notes, duration)

    @staticmethod
    def _synthesize_chime(filepath: str, notes: list, duration: float, sample_rate: int = 44100):
        num_samples = int(duration * sample_rate)
        with wave.open(filepath, "w") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            frames = []
            for i in range(num_samples):
                t = i / sample_rate
                val = 0.0
                for freq, start_t, end_t, amp in notes:
                    if start_t <= t <= end_t:
                        local_t = t - start_t
                        attack = min(1.0, local_t / 0.006)
                        envelope = math.exp(-local_t * 13.0)
                        wave_val = (
                            math.sin(2 * math.pi * freq * local_t) * 0.75
                            + math.sin(4 * math.pi * freq * local_t) * 0.25
                        )
                        val += wave_val * attack * envelope * amp
                val = max(-1.0, min(1.0, val))
                sample = int(val * 32767 * 0.42)
                frames.append(struct.pack("<h", sample))
            wav.writeframes(b"".join(frames))

    def _subscribe_events(self):
        event_bus.subscribe(TaskToggledEvent, self._on_task_toggled)
        event_bus.subscribe(LevelUpEvent, lambda ev: self.play_level_up())
        event_bus.subscribe(AchievementUnlockedEvent, lambda ev: self.play_achievement())
        event_bus.subscribe(AllDailyTasksCompletedEvent, lambda ev: self.play_daily_all_done())

    def _on_task_toggled(self, ev: TaskToggledEvent):
        if ev.done:
            self.play_task_done()

    def play(self, filename: str):
        if not self.enabled or not winsound:
            return
        path = os.path.join(self.SOUNDS_DIR, filename)
        if os.path.exists(path):
            try:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception:
                pass

    def play_task_done(self):
        self.play("task_done.wav")

    def play_level_up(self):
        self.play("level_up.wav")

    def play_quest_complete(self):
        self.play("quest_complete.wav")

    def play_achievement(self):
        self.play("achievement.wav")

    def play_daily_all_done(self):
        self.play("daily_all_done.wav")
