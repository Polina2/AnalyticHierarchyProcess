class PromptGenerator:
    def __init__(self, criteria_names, alternative_names):
        self.criteria_names = criteria_names
        self.alternative_names = alternative_names

    def get_criteria_prompt(self):
        return f"""Сравни эти критерии по важности: {', '.join(self.criteria_names)}
Верни только JSON с обратно-симметричной матрицей. Пример ответа для 3 элементов:
{{"matrix": [[1, 3, 5], [1/3, 1, 2], [1/5, 1/2, 1]]}}. 
Верни аналогичную матрицу для {len(self.criteria_names)} элементов"""

    @staticmethod
    def get_basic_prompt():
        return f"""Ты эксперт по принятию решений методом анализа иерархий.
Твоя задача - создать матрицу попарных сравнений.
Отвечай ТОЛЬКО в формате JSON без каких-либо объяснений.
Сравни элементы по шкале Саати от 1 до 9.
1 - равная важность, 3 - умеренное превосходство,
5 - сильное превосходство, 7 - очень сильное превосходство,
9 - абсолютное превосходство."""

    def get_alternative_prompt(self, criterion):
        return f"""Сравни альтернативы по критерию "{criterion}": {', '.join(self.alternative_names)}
Верни только JSON с обратно-симметричной матрицей. Пример ответа для 3 элементов:
{{"matrix": [[1, 3, 5], [1/3, 1, 2], [1/5, 1/2, 1]]}}. 
Верни аналогичную матрицу для {len(self.alternative_names)} элементов"""

    @staticmethod
    def get_criteria_prompt_for_client(criteria_list, n):
        return f"""Создай матрицу попарных сравнений для критериев:

        {criteria_list}

        Требования:
        - Матрица {n}x{n}
        - По диагонали 1
        - Значения по шкале Саати 1-9
        - Для a[i][j] = x, тогда a[j][i] = 1/x

        Верни ТОЛЬКО JSON по примеру, но со своими оценками:
        {{"matrix": [[1, 3, 5], [1/3, 1, 2], [1/5, 1/2, 1]]}}"""

    @staticmethod
    def get_alternative_prompt_for_client(criterion, alt_list, n, alt_description):
        return f"""Сравни альтернативы по критерию "{criterion}".
        Названия альтернатив:
        {alt_list}
        Информация об альтернативах:
        {alt_description}
        
        Верни JSON с матрицей попарных сравнений размера {n}x{n}."""

    def get_english_criteria_prompt(self):
        return f"""Compare these criteria by importance: {', '.join(self.criteria_names)}
Return only the JSON with a back-symmetric matrix. Sample response for 3 elements:
{{"matrix": [[1, 3, 5], [1/3, 1, 2], [1/5, 1/2, 1]]}}. 
Return a similar matrix for {len(self.criteria_names)} elements"""

    @staticmethod
    def get_english_basic_prompt():
        return f"""You are an expert in decision-making using hierarchy analysis.
Your task is to create a matrix of pairwise comparisons.
Reply ONLY in JSON format without any explanation.
Compare the elements on the Saati scale from 1 to 9.
1 - equal importance, 3 - moderate superiority,
5 - strong superiority, 7 - very strong superiority,
9 - absolute superiority."""

    def get_english_alternative_prompt(self, criterion):
        return f"""Compare the alternatives according to the criterion "{criterion}": {', '.join(self.alternative_names)}
Just return the JSON with a back-symmetric matrix. Sample response for 3 elements:
{{"matrix": [[1, 3, 5], [1/3, 1, 2], [1/5, 1/2, 1]]}}. 
Return a similar matrix for {len(self.alternative_names)} elements"""
