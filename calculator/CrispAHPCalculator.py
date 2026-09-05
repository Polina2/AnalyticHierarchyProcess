from calculator.AHPCalculator import AHPCalculator
import numpy as np


class CrispAHPCalculator(AHPCalculator):
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
