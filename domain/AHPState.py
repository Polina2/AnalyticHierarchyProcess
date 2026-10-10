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

    def save(self, file_path: str):
        pass

    @staticmethod
    def load(cls, file_path: str):
        pass

    def from_data(self, data):
        self.experts_count = data['num_experts']
        self.criteria_tree = data['criteria_tree']
        for i in range(data['num_alternatives']):
            self.alternatives.append(Alternative(data['alternative_names'][i]))

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
