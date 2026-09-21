from calculator.AHPCalculator import AHPCalculator
from collections import deque
import numpy as np

from domain.AHPState import AHPState
from domain.CriterionNode import CriterionNode


class CrispAHPCalculator(AHPCalculator):
    def aggregate_experts(self, tree: CriterionNode):
        node_queue = deque()
        node_queue.append(tree)
        while node_queue:
            cur_node = node_queue.popleft()
            cur_node.matrices['aggregated_matrix'] = (
                AHPCalculator
                .aggregate_matrices([cur_node.matrices[i] for i in range(len(cur_node.matrices))])
            )
            cur_node.weights = self.calculate_eigenvector(cur_node.matrices['aggregated_matrix'])
            for child in cur_node.children:
                node_queue.append(child)

    def aggregate_criteria_tree(self, tree: CriterionNode) -> np.ndarray:
        tree.global_weights = tree.weights
        result = []
        self._get_criteria_weights(tree, result)
        return np.array(result)

    def _get_criteria_weights(self, node: CriterionNode, result):
        weights = node.global_weights
        for i, ch in enumerate(node.children):
            if not ch.is_leaf():
                ch.global_weights = ch.weights * weights[i]
                self._get_criteria_weights(ch, result)
            else:
                result.append(weights[i])

    def get_alternatives_matrix(self, tree: CriterionNode) -> np.ndarray:
        alternative_weights = self._get_alternative_weights(tree)
        return np.array(alternative_weights).T

    def _get_alternative_weights(self, tree: CriterionNode) -> list[np.ndarray]:
        weights = []
        for child in tree.children:
            if child.is_leaf():
                weights.append(child.weights)
            else:
                weights.extend(self._get_alternative_weights(child))
        return weights

    def get_result(self, alt_matrix: np.ndarray, crit_vector: np.ndarray) -> np.ndarray:
        return alt_matrix @ crit_vector

    def calculate_eigenvector(self, matrix):
        weights = np.power(np.prod(matrix, axis=1), 1 / len(matrix))
        weights /= sum(weights)
        return weights

    def estimate_consistency(self, matrix, weights):
        random_consistency = [0, 0, 0, 0.58, 0.9, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]

        new_vector = matrix @ weights
        new_vector /= weights
        lambda_max = new_vector.mean()

        n = len(matrix)
        index = (lambda_max - n) / (n - 1)
        if 3 <= n <= 10:
            relation = index / random_consistency[n]
        else:
            relation = index
        return index, relation

    def estimate_experts_consistency(self, tree: CriterionNode):
        node_queue = deque()
        node_queue.append(tree)
        while node_queue:
            cur = node_queue.popleft()
            for ch in cur.children:
                node_queue.append(ch)
            for key in cur.matrices:
                matrix = cur.matrices[key]
                weights = self.calculate_eigenvector(matrix)
                index, relation = self.estimate_consistency(matrix, weights)
                cur.consistency[key] = {'index': index, 'relation': relation}

    def apply(self, state: AHPState):
        self.aggregate_experts(state.criteria_tree)
        self.estimate_experts_consistency(state.criteria_tree)
        global_weights = self.aggregate_criteria_tree(state.criteria_tree)
        alt_matrix = self.get_alternatives_matrix(state.criteria_tree)
        return self.get_result(alt_matrix, global_weights)
