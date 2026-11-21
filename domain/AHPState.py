import json

from domain.Alternative import Alternative
from domain.CriterionNode import CriterionNode
import numpy as np


class AHPState:
    criteria_tree: CriterionNode
    alternatives: list[Alternative]
    experts_count: int
    current_expert_id: int
    genre_preset: str
    method_type: str  # "crisp" | "fuzzy"
    final_scores: np.ndarray

    def __init__(self):
        self.criteria_tree = CriterionNode("root")
        self.alternatives = []
        self.experts_count = 0
        self.current_expert_id = 0
        self.genre_preset = ''
        self.method_type = 'crisp'

    def from_data(self, data):
        self.experts_count = data['num_experts']
        self._sync_alternatives(
            data['alternative_names'],
            data['alternative_descriptions']
        )
        self.criteria_tree = self._sync_criteria_tree(
            self.criteria_tree,
            data['criteria_tree'],
            data.get('criteria_descriptions', {})
        )
        # self.criteria_tree = data['criteria_tree']

    def _sync_alternatives(self, new_names: list, new_descriptions: list):
        # Собираем существующие описания в словарь
        existing = {alt.name: alt.description for alt in self.alternatives}
        # Формируем новый список
        self.alternatives = []
        for i, name in enumerate(new_names):
            desc = new_descriptions[i] if i < len(new_descriptions) else ''
            # Если описание пустое, но альтернатива уже была — берём старое
            if not desc and name in existing:
                desc = existing[name]
            self.alternatives.append(Alternative(name=name, description=desc))

    def _sync_criteria_tree(self, old_tree: 'CriterionNode',
                            new_tree: 'CriterionNode',
                            descriptions: dict) -> 'CriterionNode':
        # Строим индекс старых детей по имени
        old_children_by_name = {child.name: child for child in old_tree.children}

        # Обновляем корень
        root = new_tree
        root.matrices = old_tree.matrices
        root.weights = old_tree.weights
        root.global_weights = old_tree.global_weights
        root.consistency = old_tree.consistency
        if root.name in descriptions:
            root.description = descriptions[root.name]

        # Для каждого нового ребёнка — ищем соответствующий старый
        for new_child in root.children:
            old_child = old_children_by_name.get(new_child.name)

            if old_child is not None:
                # Узел существовал — переносим заполненные данные
                new_child.matrices = old_child.matrices
                new_child.weights = old_child.weights
                new_child.global_weights = old_child.global_weights
                new_child.consistency = old_child.consistency
                if not new_child.description and old_child.description:
                    new_child.description = old_child.description

                # Рекурсивная синхронизация потомков
                self._sync_children(new_child, old_child, descriptions)
            else:
                # Новый узел — просто добавляем описание из словаря
                if new_child.name in descriptions:
                    new_child.description = descriptions[new_child.name]

        return root

    def _sync_children(self, new_node: 'CriterionNode',
                       old_node: 'CriterionNode',
                       descriptions: dict):
        old_children_by_name = {child.name: child for child in old_node.children}

        for new_child in new_node.children:
            old_child = old_children_by_name.get(new_child.name)

            if old_child is not None:
                new_child.matrices = old_child.matrices
                new_child.weights = old_child.weights
                new_child.global_weights = old_child.global_weights
                new_child.consistency = old_child.consistency
                if not new_child.description and old_child.description:
                    new_child.description = old_child.description
                self._sync_children(new_child, old_child, descriptions)
            else:
                if new_child.name in descriptions:
                    new_child.description = descriptions[new_child.name]

    def to_data(self) -> dict:
        data = {
            'num_alternatives': len(self.alternatives),
            'num_experts': self.experts_count,
            'alternative_names': [alt.name for alt in self.alternatives],
            'criteria_tree': self.criteria_tree
        }
        return data

    def to_results(self) -> tuple:
        aggregated_criteria = self.criteria_tree.matrices['aggregated_matrix']
        aggregated_alternatives = [ch.matrices['aggregated_matrix'] for ch in self.criteria_tree.children]
        criteria_weights = self.criteria_tree.global_weights
        alternative_weights = [ch.weights for ch in self.criteria_tree.children]
        criteria_consistency = self.criteria_tree.consistency['aggregated_matrix']
        criteria_consistency = (criteria_consistency['index'], criteria_consistency['relation'])
        alternatives_consistency = [
            (
                ch.consistency['aggregated_matrix']['index'], ch.consistency['aggregated_matrix']['relation']
            ) for ch in self.criteria_tree.children
        ]
        return (aggregated_criteria, aggregated_alternatives,
                criteria_weights, alternative_weights,
                criteria_consistency, alternatives_consistency)

    def to_json(self) -> str:
        """Сериализует всё состояние в JSON строку."""
        data = {
            'criteria_tree': self.criteria_tree.to_dict(),
            'alternatives': [alt.to_dict() for alt in self.alternatives],
            'experts_count': self.experts_count,
            'current_expert_id': self.current_expert_id,
            'genre_preset': self.genre_preset,
            'method_type': self.method_type
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'AHPState':
        """Десериализует состояние из JSON строки."""
        data = json.loads(json_str)
        state = cls()

        state.criteria_tree = CriterionNode.from_dict(data['criteria_tree'])
        state.alternatives = [Alternative.from_dict(alt) for alt in data['alternatives']]
        state.experts_count = data.get('experts_count', 1)
        state.current_expert_id = data.get('current_expert_id', 0)
        state.genre_preset = data.get('genre_preset', '')
        state.method_type = data.get('method_type', 'crisp')

        return state
