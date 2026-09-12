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
        self.current_expert_id = 1

    def save(self, file_path: str):
        pass

    @staticmethod
    def load(cls, file_path: str):
        pass

    def from_data(self, data):
        self.experts_count = data['num_experts']
        for i in range(data['num_criteria']):
            self.criteria_tree.add_child(CriterionNode(data['criteria_names'][i]))
        for i in range(data['num_alternatives']):
            self.alternatives.append(Alternative(data['alternative_names'][i]))

    def to_data(self) -> dict:
        data = {
            'num_criteria': len(self.criteria_tree.children),
            'num_alternatives': len(self.alternatives),
            'num_experts': self.experts_count,
            'criteria_names': [child.name for child in self.criteria_tree.children],
            'alternative_names': [alt.name for alt in self.alternatives],
            'expert_data': None
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
        pass

    @staticmethod
    def from_json(cls, json_str: str):
        pass
