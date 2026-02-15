import pandas as pd


def argsort(arr):
    idxs = list(range(len(arr)))
    zip_arr = list(zip(idxs, arr))
    zip_arr.sort(key=lambda x: x[1], reverse=True)
    return [x[0] for x in zip_arr]


class Presenter:
    @staticmethod
    def display_results(data, criteria_matrix, alt_matrices, criteria_weights,
                        alt_weights, crit_consistency, alt_consistency, final_scores):
        result_text = "РЕЗУЛЬТАТЫ МЕТОДА АНАЛИЗА ИЕРАРХИЙ\n\n"

        result_text += "АГРЕГИРОВАННАЯ МАТРИЦА КРИТЕРИЕВ:\n"
        result_text += Presenter.matrix_to_string(criteria_matrix, data['criteria_names'])
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
            result_text += Presenter.matrix_to_string(alt_matrices[crit_idx], data['alternative_names'])
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
    def matrix_to_string(matrix, labels):
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
