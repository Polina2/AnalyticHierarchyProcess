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
