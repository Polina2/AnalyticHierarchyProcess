import numpy as np


class AHP:
    def __init__(self, data):
        self.data = data

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
    def aggregate_matrices(matrices):
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

    @staticmethod
    def calculate_eigenvector(matrix):
        # normalized = matrix / matrix.sum(axis=0)
        # weights = normalized.mean(axis=1)
        weights = np.power(np.prod(matrix, axis=1), 1/len(matrix))
        weights /= sum(weights)
        return weights

    def calculate_results(self):
        # Собираем данные от всех экспертов
        n_experts = self.data['num_experts']
        n_criteria = self.data['num_criteria']
        n_alternatives = self.data['num_alternatives']

        # Массивы для хранения матриц всех экспертов
        all_criteria_matrices = []
        all_alternatives_matrices = [[] for _ in range(n_criteria)]

        for expert_idx in range(n_experts):
            expert_data = self.data['expert_data'][expert_idx]

            # Матрица критериев для текущего эксперта
            criteria_matrix = self.build_matrix_from_inputs(
                expert_data['criteria_matrix'], n_criteria
            )
            all_criteria_matrices.append(criteria_matrix)

            # Матрицы альтернатив для текущего эксперта
            for crit_idx in range(n_criteria):
                alt_matrix = self.build_matrix_from_inputs(
                    expert_data['alternatives_matrices'][crit_idx], n_alternatives
                )
                all_alternatives_matrices[crit_idx].append(alt_matrix)

        # Агрегируем матрицы средним геометрическим
        aggregated_criteria = self.aggregate_matrices(all_criteria_matrices)
        aggregated_alternatives = []
        for crit_matrices in all_alternatives_matrices:
            aggregated_alternatives.append(self.aggregate_matrices(crit_matrices))

        # Вычисляем собственные векторы
        criteria_weights = self.calculate_eigenvector(aggregated_criteria)
        alternative_weights = []
        for alt_matrix in aggregated_alternatives:
            alternative_weights.append(self.calculate_eigenvector(alt_matrix))

        # Формируем матрицу весов альтернатив
        alternatives_matrix = np.array(alternative_weights).T

        # Умножаем матрицу альтернатив на веса критериев
        final_scores = alternatives_matrix @ criteria_weights

        criteria_consistency = AHP.estimate_consistency(aggregated_criteria, criteria_weights)
        alternatives_consistency = []
        for i in range(n_criteria):
            alternatives_consistency.append(
                AHP.estimate_consistency(aggregated_alternatives[i], alternative_weights[i])
            )

        # Выводим результаты
        return (
            aggregated_criteria, aggregated_alternatives,
            criteria_weights, alternative_weights,
            criteria_consistency, alternatives_consistency, final_scores
        )

    @staticmethod
    def estimate_consistency(matrix, weights):
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
