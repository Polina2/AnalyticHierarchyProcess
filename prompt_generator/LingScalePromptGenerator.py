from domain.Alternative import Alternative
from domain.CriterionNode import CriterionNode
from prompt_generator.PromptGenerator import PromptGenerator


class LingScalePromptGenerator(PromptGenerator):
    def __init__(self):
        self.basic_prompt = f"""Ты эксперт по принятию решений методом анализа иерархий.
            Сравни элементы по шкале Саати. Выбирай один из вариантов:
            равенство, умеренное превосходство,
            сильное превосходство, очень сильное превосходство,
            абсолютное превосходство./no_think"""

    def get_criteria_prompt(self, crit1: CriterionNode, crit2: CriterionNode):
        return f"""Используй шкалу Саати для сравнения следующих 2 критериев по важности.
            Если первый критерий важнее, верни ответ в виде "1 - один из вариантов",
            если второй критерий важнее, верни ответ в виде "2 - один из вариантов".
            Критерий 1: {crit1.name}. Описание критерия 1: {crit1.description}
            Критерий 2: {crit2.name}. Описание критерия 2: {crit2.description}"""

    def get_alternative_prompt(self, alt1: Alternative, alt2: Alternative, crit: CriterionNode):
        return f"""Используй шкалу Саати для сравнения следующих 2 альтернатив по критерию {crit.name}.
            Пояснения по критерию: {crit.description}
            Если первая альтернатива лучше, верни ответ в виде "1 - один из вариантов",
            если вторая альтернатива лучше, верни ответ в виде "2 - один из вариантов".
            Альтернатива 1: {alt1.name}. Описание: {alt1.description}
            Альтернатива 2: {alt2.name}. Описание: {alt2.description}"""
