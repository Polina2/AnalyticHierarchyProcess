import os

from domain.AHPState import AHPState


class StateRepository:
    def save(self, state: AHPState, file_path: str):
        """Сохраняет состояние в файл."""
        json_str = state.to_json()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_str)

    def load(self, file_path: str) -> AHPState:
        """Загружает состояние из файла."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден")

        with open(file_path, 'r', encoding='utf-8') as f:
            json_str = f.read()

        return AHPState.from_json(json_str)