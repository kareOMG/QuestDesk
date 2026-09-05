from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class Achievement:
    """成就实体模型"""
    id: str
    name: str
    description: str
    icon: str
    category: str
    unlocked: bool = False
    unlocked_at: str = ""
    current_progress: int = 0
    target_progress: int = 1
    clue: str = ""

    @property
    def progress_percentage(self) -> int:
        if self.target_progress <= 0:
            return 100 if self.unlocked else 0
        return min(100, int(self.current_progress / self.target_progress * 100))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon,
            "category": self.category,
            "unlocked": self.unlocked,
            "unlocked_at": self.unlocked_at,
            "current_progress": self.current_progress,
            "target_progress": self.target_progress,
            "clue": self.clue,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Achievement':
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            icon=data.get("icon", "🏆"),
            category=data.get("category", "成就"),
            unlocked=data.get("unlocked", False),
            unlocked_at=data.get("unlocked_at", ""),
            current_progress=data.get("current_progress", 0),
            target_progress=data.get("target_progress", 1),
            clue=data.get("clue", ""),
        )
