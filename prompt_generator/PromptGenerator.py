from abc import abstractmethod


class PromptGenerator:

    @abstractmethod
    def get_criteria_prompt(self, crit1, crit2):
        pass

    @staticmethod
    def get_basic_prompt():
        return f"""Ты эксперт по принятию решений методом анализа иерархий.
Твоя задача - создать матрицу попарных сравнений.
Отвечай ТОЛЬКО в формате JSON без каких-либо объяснений.
Сравни элементы по шкале Саати от 1 до 9.
1 - равная важность, 3 - умеренное превосходство,
5 - сильное превосходство, 7 - очень сильное превосходство,
9 - абсолютное превосходство."""

    @abstractmethod
    def get_alternative_prompt(self, alt1, alt2, crit):
        pass

    def get_english_criteria_prompt(self):
        pass

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
        pass
