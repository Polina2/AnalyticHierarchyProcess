from abc import ABC, abstractmethod
import numpy as np

from domain.AHPState import AHPState
from domain.CriterionNode import CriterionNode


class AHPCalculator (ABC):
    @abstractmethod
    def estimate_consistency(self, matrix: np.ndarray, weights: np.ndarray) -> float:
        pass

    @abstractmethod
    def aggregate_experts(self, tree: CriterionNode):
        pass

    @abstractmethod
    def calculate_eigenvector(self, matrix: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def aggregate_criteria_tree(self, tree: CriterionNode) -> np.ndarray:
        pass

    @abstractmethod
    def get_alternatives_matrix(self, tree: CriterionNode) -> np.ndarray:
        pass

    @abstractmethod
    def get_result(self, alt_matrix: np.ndarray, crit_vector: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def apply(self, state: AHPState) -> np.ndarray:
        pass

    @staticmethod
    def aggregate_matrices(matrices: list[list[list[float]]]) -> list[list[float]] | None:
        n = len(matrices)
        if n == 0:
            return None

        result = np.ones_like(matrices[0])
        rows, cols = result.shape

        for i in range(rows):
            for j in range(cols):
                values = [matrices[k][i, j] for k in range(n)]
                # Среднее геометрическое
                geo_mean = np.power(np.prod(values), 1 / n)
                result[i, j] = geo_mean

        return result
