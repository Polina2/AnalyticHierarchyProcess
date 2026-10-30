import os
import sys
import json


class PresetInfo:
    """Информация о встроенном пресете."""

    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description


class CriteriaPresetManager:
    """
    Менеджер встроенных пресетов (только для чтения).
    Пользовательские пресеты не поддерживаются — для сохранения/загрузки
    состояний используйте StateRepository.
    """

    def __init__(self, builtin_dir: str = "presets_builtin"):
        self.builtin_dir = self._resolve_builtin_dir(builtin_dir)

    def _resolve_builtin_dir(self, path: str) -> str:
        """Путь к встроенным пресетам."""
        if getattr(sys, 'frozen', False):
            return os.path.join(sys._MEIPASS, path)
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

    def get_all_presets(self) -> list[PresetInfo]:
        """Список всех доступных встроенных пресетов."""
        presets = []
        if not os.path.exists(self.builtin_dir):
            return presets

        for file_name in sorted(os.listdir(self.builtin_dir)):
            if not file_name.endswith(".json"):
                continue

            name = file_name[:-5]
            file_path = os.path.join(self.builtin_dir, file_name)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                description = data.get('description', '')
                presets.append(PresetInfo(name, description))
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка чтения пресета {file_path}: {e}")

        return presets

    def load_preset(self, name: str) -> str:
        """
        Загружает встроенный пресет и возвращает JSON-строку состояния.
        Десериализацию в AHPState делает Presenter.
        """
        file_path = os.path.join(self.builtin_dir, f"{name}.json")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Пресет '{name}' не найден")

        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()