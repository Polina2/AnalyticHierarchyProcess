import pandas as pd
import numpy as np

from domain.AHPState import AHPState
from domain.CriterionNode import CriterionNode


def argsort(arr):
    idxs = list(range(len(arr)))
    zip_arr = list(zip(idxs, arr))
    zip_arr.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in zip_arr]


class ResultsFormatter:
    @staticmethod
    def format_results(state: AHPState) -> str:
        """
        Форматирует результаты AHP из состояния.
        Выводит все агрегированные матрицы, локальные и глобальные веса для каждого узла,
        включая корневой.

        :param state: AHPState с вычисленными результатами
        :return: Отформатированный текст результатов
        """
        result_text = "РЕЗУЛЬТАТЫ МЕТОДА АНАЛИЗА ИЕРАРХИЙ\n\n"

        # Структура дерева
        result_text += "СТРУКТУРА ДЕРЕВА КРИТЕРИЕВ:\n"
        result_text += ResultsFormatter._format_tree_structure(state.criteria_tree, 0)
        result_text += "\n" + "=" * 60 + "\n\n"

        # Вывод данных корневого узла
        root = state.criteria_tree
        if root.children:
            root_labels = [c.name for c in root.children]

            result_text += "Корень (сравнение критериев верхнего уровня)\n"

            # Агрегированная матрица
            if 'aggregated_matrix' in root.matrices:
                matrix = root.matrices['aggregated_matrix']
                result_text += "Агрегированная матрица парных сравнений:\n"
                result_text += ResultsFormatter._indent_text(
                    ResultsFormatter.matrix_to_string(matrix, root_labels),
                    "  "
                )

            # Локальные веса
            if root.weights is not None:
                result_text += "Локальные веса:\n"
                for i, weight in enumerate(root.weights):
                    result_text += f"  {root_labels[i]}: {float(weight):.4f}\n"

            # Глобальные веса
            if root.global_weights is not None:
                result_text += "Глобальные веса:\n"
                for i, weight in enumerate(root.global_weights):
                    result_text += f"  {root_labels[i]}: {float(weight):.4f}\n"

            # Согласованность
            result_text += ResultsFormatter._format_consistency(root.consistency, "")

            result_text += "\n" + "=" * 60 + "\n\n"

        # Рекурсивно обходим потомков корня
        result_text += ResultsFormatter._format_node_results(
            state.criteria_tree,
            state.alternatives,
            depth=0
        )

        # Финальные оценки альтернатив
        result_text += "\n" + "=" * 60 + "\n"
        result_text += "ФИНАЛЬНЫЕ ОЦЕНКИ АЛЬТЕРНАТИВ:\n"
        result_text += "-" * 60 + "\n"

        alt_names = [alt.name for alt in state.alternatives]
        final_scores = state.final_scores  # numpy.ndarray

        # Сортируем по убыванию
        sorted_indices = np.argsort(final_scores)[::-1]

        for rank, idx in enumerate(sorted_indices, 1):
            result_text += f"{rank}. {alt_names[idx]}: {final_scores[idx]:.4f}\n"

        return result_text

    @staticmethod
    def _format_tree_structure(node: CriterionNode, depth: int) -> str:
        """Рекурсивно форматирует структуру дерева"""
        result = ""
        indent = "  " * depth

        if depth == 0:
            result += f"{indent}Root\n"

        for child in node.children:
            if child.is_leaf():
                result += f"{indent}└─ {child.name} [лист]\n"
            else:
                result += f"{indent}└─ {child.name}\n"
                result += ResultsFormatter._format_tree_structure(child, depth + 1)

        return result

    @staticmethod
    def _format_consistency(consistency: dict, indent: str) -> str:
        """
        Форматирует согласованность.
        consistency: dict[int, dict[str, float]] где str — 'index' и 'relation'
        """
        if not consistency:
            return ""

        result = f"{indent}Согласованность:\n"

        for key, metrics in consistency.items():
            # Подпись ключа
            if isinstance(key, int):
                key_label = f"Эксперт {key + 1}"
            elif key == 'aggregated_matrix':
                key_label = 'Агрегированная матрица'
            else:
                key_label = str(key)

            result += f"{indent}  {key_label}:\n"

            if isinstance(metrics, dict):
                # Индекс согласованности (CI)
                if 'index' in metrics:
                    ci_value = float(metrics['index'])
                    result += f"{indent}    Индекс согласованности: {ci_value:.4f}\n"

                # Отношение согласованности (CR) в процентах
                if 'relation' in metrics:
                    cr_value = float(metrics['relation'])
                    cr_percent = cr_value * 100
                    result += f"{indent}    Отношение согласованности: {cr_percent:.2f}%\n"

                # Другие метрики (если появятся)
                for metric_key, metric_value in metrics.items():
                    if metric_key not in ('index', 'relation'):
                        if isinstance(metric_value, (int, float, np.floating)):
                            result += f"{indent}    {metric_key}: {float(metric_value):.4f}\n"
                        else:
                            result += f"{indent}    {metric_key}: {metric_value}\n"
            else:
                if isinstance(metrics, (int, float, np.floating)):
                    result += f"{indent}    {float(metrics):.4f}\n"
                else:
                    result += f"{indent}    {metrics}\n"

        return result

    @staticmethod
    def _format_node_results(
            node: CriterionNode,
            alternatives: list,
            depth: int
    ) -> str:
        """Рекурсивно форматирует результаты для потомков узла"""
        result = ""
        indent = "  " * depth

        for child in node.children:
            result += f"{indent}Критерий: {child.name}\n"

            # Определяем labels в зависимости от типа узла
            if child.is_leaf():
                labels = [alt.name for alt in alternatives]
            else:
                labels = [c.name for c in child.children]

            # Агрегированная матрица парных сравнений
            if 'aggregated_matrix' in child.matrices:
                matrix = child.matrices['aggregated_matrix']
                result += f"{indent}Агрегированная матрица парных сравнений:\n"
                result += ResultsFormatter._indent_text(
                    ResultsFormatter.matrix_to_string(matrix, labels),
                    indent + "  "
                )

            # Локальные веса
            if child.weights is not None:
                result += f"{indent}Локальные веса:\n"
                for i, weight in enumerate(child.weights):
                    result += f"{indent}  {labels[i]}: {float(weight):.4f}\n"

            # Глобальные веса
            if child.global_weights is not None:
                result += f"{indent}Глобальные веса:\n"
                for i, weight in enumerate(child.global_weights):
                    result += f"{indent}  {labels[i]}: {float(weight):.4f}\n"

            # Согласованность
            result += ResultsFormatter._format_consistency(child.consistency, indent)

            result += "\n"

            # Рекурсия для потомков
            if not child.is_leaf():
                result += ResultsFormatter._format_node_results(
                    child,
                    alternatives,
                    depth + 1
                )

        return result

    @staticmethod
    def _indent_text(text: str, indent: str) -> str:
        """Добавляет отступ к каждой строке текста"""
        lines = text.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)

    @staticmethod
    def matrix_to_string(matrix, labels) -> str:
        """Форматирует матрицу в строку"""
        n = len(labels)

        # Заголовки столбцов
        result = f"{' ':<25}" + "".join([f"{label:<12}" for label in labels]) + "\n"

        # Строки матрицы
        for i in range(n):
            result += f"{labels[i]:<20}"
            for j in range(n):
                value = float(matrix[i, j]) if isinstance(matrix, np.ndarray) else matrix[i][j]
                result += f"{value:<12.4f}"
            result += "\n"

        return result + "\n"

    @staticmethod
    def format_results1(data, criteria_matrix, alt_matrices, criteria_weights,
                       alt_weights, crit_consistency, alt_consistency, final_scores):
        result_text = "РЕЗУЛЬТАТЫ МЕТОДА АНАЛИЗА ИЕРАРХИЙ\n\n"

        result_text += "АГРЕГИРОВАННАЯ МАТРИЦА КРИТЕРИЕВ:\n"
        result_text += ResultsFormatter.matrix_to_string(criteria_matrix, data['criteria_names'])
        result_text += f"\nВЕКТОР ВЕСОВ КРИТЕРИЕВ:\n"
        for i, weight in enumerate(criteria_weights):
            result_text += f"{data['criteria_names'][i]}: {weight:.4f}\n"
        result_text += "\nИндекс согласованности:\n"
        result_text += str(crit_consistency[0])
        result_text += "\nОтношение согласованности:\n"
        result_text += str(crit_consistency[1])

        result_text += "\n" + "=" * 50 + "\n\n"

        result_text += "МАТРИЦЫ И ВЕСА АЛЬТЕРНАТИВ ПО КРИТЕРИЯМ:\n"
        for crit_idx in range(len(alt_matrices)):
            result_text += f"\nКритерий: {data['criteria_names'][crit_idx]}\n"
            result_text += ResultsFormatter.matrix_to_string(alt_matrices[crit_idx], data['alternative_names'])
            result_text += f"Веса альтернатив:\n"
            for i, weight in enumerate(alt_weights[crit_idx]):
                result_text += f"{data['alternative_names'][i]}: {weight:.4f}\n"
            result_text += "\nИндекс согласованности:\n"
            result_text += str(alt_consistency[crit_idx][0])
            result_text += "\nОтношение согласованности:\n"
            result_text += str(alt_consistency[crit_idx][1]) + "\n"

        result_text += "\n" + "=" * 50 + "\n\n"
        result_text += "ФИНАЛЬНЫЕ РЕЗУЛЬТАТЫ:\n"

        # Сортируем альтернативы по убыванию итоговой оценки
        sorted_indices = argsort(final_scores)

        for idx in sorted_indices:
            result_text += f"{data['alternative_names'][idx]}: {final_scores[idx]:.4f}\n"

        return result_text

    @staticmethod
    def matrix_to_string1(matrix, labels):
        n = len(labels)
        result = f"{' ':<30}" + "".join([f"{label:<15}" for label in labels]) + "\n"
        for i in range(n):
            result += f"{labels[i]:<20}"
            for j in range(n):
                result += f"{f"{matrix[i, j]:12.4f}":<20}"
            result += "\n"
        return result + "\n"

    @staticmethod
    def export_to_excel(data, criteria_matrix, alt_matrices, criteria_weights, alt_weights,
                        crit_consistency, alt_consistency, final_scores, file_path):
        # Создаем список данных для Excel
        excel_data = ["АГРЕГИРОВАННАЯ МАТРИЦА КРИТЕРИЕВ", ""]

        # Заголовки для матрицы критериев
        header = [""] + data['criteria_names']
        excel_data.append(header)

        # Данные матрицы критериев
        for i, criterion in enumerate(data['criteria_names']):
            row = [criterion] + [f"{criteria_matrix[i, j]:.4f}" for j in range(len(data['criteria_names']))]
            excel_data.append(row)

        excel_data.append([])
        excel_data.append([])

        # 2. Вектор весов критериев
        excel_data.append("ВЕКТОР ВЕСОВ КРИТЕРИЕВ")
        excel_data.append([])
        excel_data.append(["Критерий", "Вес"])

        for i, criterion in enumerate(data['criteria_names']):
            excel_data.append([criterion, f"{criteria_weights[i]:.4f}"])

        excel_data.append([])
        excel_data.append("Индекс согласованности")
        excel_data.append(str(crit_consistency[0]))
        excel_data.append("Отношение согласованности")
        excel_data.append(str(crit_consistency[1]))

        excel_data.append([])
        excel_data.append([])

        # 3. Матрицы альтернатив по критериям
        excel_data.append("МАТРИЦЫ АЛЬТЕРНАТИВ ПО КРИТЕРИЯМ")
        excel_data.append([])

        for crit_idx in range(len(alt_matrices)):
            excel_data.append([f"Критерий: {data['criteria_names'][crit_idx]}"])
            excel_data.append([])

            # Заголовки для матрицы альтернатив
            header = [""] + data['alternative_names']
            excel_data.append(header)

            # Данные матрицы альтернатив
            for i, alternative in enumerate(data['alternative_names']):
                row = [alternative] + [f"{alt_matrices[crit_idx][i, j]:.4f}" for j in
                                       range(len(data['alternative_names']))]
                excel_data.append(row)

            excel_data.append([])

            # Вектор весов альтернатив для этого критерия
            excel_data.append(["Вес альтернатив для данного критерия:"])
            excel_data.append(["Альтернатива", "Вес"])

            for i, alternative in enumerate(data['alternative_names']):
                excel_data.append([alternative, f"{alt_weights[crit_idx][i]:.4f}"])

            excel_data.append([])
            excel_data.append("Индекс согласованности")
            excel_data.append(str(alt_consistency[crit_idx][0]))
            excel_data.append("Отношение согласованности")
            excel_data.append(str(alt_consistency[crit_idx][1]))

            excel_data.append([])
            excel_data.append([])

        # 4. Итоговые результаты
        excel_data.append("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        excel_data.append([])
        excel_data.append(["Альтернатива", "Итоговый балл", "Ранг"])

        # Сортируем по убыванию итогового балла
        sorted_indices = argsort(final_scores)
        for rank, idx in enumerate(sorted_indices, 1):
            excel_data.append([
                data['alternative_names'][idx],
                f"{final_scores[idx]:.4f}",
                rank
            ])

        # Создаем DataFrame и экспортируем в Excel
        # Преобразуем данные в плоский список для DataFrame
        flat_data = []
        for item in excel_data:
            max_len = max(len(row) for row in excel_data if isinstance(row, list))
            if isinstance(item, list):
                # Дополняем строку до максимальной длины
                item = item + [""] * (max_len - len(item))
                item = list(map(lambda x: str(x).replace('.', ','), item))
                flat_data.append(item)
            else:
                # Для одиночных строк создаем список с одним элементом
                flat_data.append([item.replace('.', ',')] + [""] * (max_len - 1))

        df = pd.DataFrame(flat_data)
        df.to_excel(file_path, index=False, header=False)
