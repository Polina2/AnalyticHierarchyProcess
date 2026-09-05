from abc import ABC, abstractmethod
import numpy as np


class AHPCalculator (ABC):
    @abstractmethod
    def calculate_eigenvector(self, matrix: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def estimate_consistency(self, matrix: np.ndarray, weights: np.ndarray) -> float:
        pass

    @staticmethod
    def build_matrix_from_inputs(input_matrix, size):
        matrix = np.ones((size, size))

        for i in range(size):
            for j in range(size):
                if i < j and input_matrix[i][j] is not None:
                    numerator_edit, denominator_edit = input_matrix[i][j]
                    try:
                        numerator = float(numerator_edit.text() or 1)
                        denominator = float(denominator_edit.text() or 1)
                        if denominator == 0:
                            denominator = 1
                        value = numerator / denominator
                        matrix[i, j] = value
                        matrix[j, i] = 1.0 / value
                    except ValueError:
                        matrix[i, j] = 1.0
                        matrix[j, i] = 1.0

        return matrix

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
