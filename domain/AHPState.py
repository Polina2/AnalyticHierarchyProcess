from domain.Alternative import Alternative
from domain.CriterionNode import CriterionNode


class AHPState:
    criteria_tree: CriterionNode
    alternatives: list[Alternative]
    experts_count: int
    current_expert_id: int
    genre_preset: str
    method_type: str  # "crisp" | "fuzzy"
    
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

    def to_json(self) -> str:
        pass

    @staticmethod
    def from_json(cls, json_str: str):
        pass
