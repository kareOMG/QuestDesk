# Project Guidelines for QuestDesk

## Git Commit & Push Rules
- **Language**: All git commit messages and pull request descriptions MUST be written in **English**.
- **Format**: Follow Conventional Commits (e.g., `feat: ...`, `fix: ...`, `refactor: ...`, `docs: ...`, `chore: ...`, `test: ...`).
- **Style**: Imperative mood, concise, and clear (e.g., `feat: add sound effect for task completion`, `fix: resolve DLL loading issue on Windows`).

## Architecture & Code Standards
- Keep path management centralized in `core/paths.py`.
- Maintain cross-platform parity (Windows & macOS).
- Ensure UI layout safety by using `ui/ui_utils.py` methods (`clear_layout`, `get_smooth_pixmap`, `load_app_icon`).
