import numpy as np


class CriterionNode:
    def __init__(self, name):
        self.name = name
        self.children = []
        self.matrices = dict()
        self.weights = None
        self.global_weights = None
        self.consistency = dict()

    def is_leaf(self) -> bool:
        return len(self.children) == 0

    def add_child(self, child):
        self.children.append(child)

    def to_dict(self) -> dict:
        """Преобразует узел и его потомков в словарь для JSON."""
        # Конвертируем numpy массивы в списки, а ключи (int) в строки
        matrices_dict = {}
        for k, v in self.matrices.items():
            key_str = str(k)
            if isinstance(v, np.ndarray):
                matrices_dict[key_str] = v.tolist()
            else:
                matrices_dict[key_str] = v

        return {
            'name': self.name,
            'children': [child.to_dict() for child in self.children],
            'matrices': matrices_dict,
            'weights': self.weights.tolist() if self.weights is not None else None,
            'global_weights': self.global_weights.tolist() if self.global_weights is not None else None,
            'consistency': self.consistency
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'CriterionNode':
        """Восстанавливает узел из словаря."""
        node = cls(name=data['name'])

        # Восстанавливаем матрицы (списки обратно в numpy)
        for k_str, v in data.get('matrices', {}).items():
            # Пытаемся вернуть int ключ, если это был ID эксперта
            try:
                key = int(k_str)
            except ValueError:
                key = k_str  # Например, 'aggregated_matrix'

            if isinstance(v, list):
                node.matrices[key] = np.array(v)
            else:
                node.matrices[key] = v

        # Восстанавливаем веса
        if data.get('weights') is not None:
            node.weights = np.array(data['weights'])
        if data.get('global_weights') is not None:
            node.global_weights = np.array(data['global_weights'])

        node.consistency = data.get('consistency', {})

        # Рекурсивно восстанавливаем детей
        for child_data in data.get('children', []):
            node.children.append(cls.from_dict(child_data))

        return node
