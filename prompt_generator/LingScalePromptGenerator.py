from domain.Alternative import Alternative
from domain.CriterionNode import CriterionNode
from prompt_generator.PromptGenerator import PromptGenerator


class LingScalePromptGenerator(PromptGenerator):
    def __init__(self):
        self.basic_prompt = f"""Ты эксперт по принятию решений методом анализа иерархий.
            Сравни элементы по шкале Саати. Выбирай один из вариантов:
            равенство, умеренное превосходство,
            сильное превосходство, очень сильное превосходство,
            абсолютное превосходство."""

    def get_criteria_prompt(self, crit1: CriterionNode, crit2: CriterionNode):
        return (f"""Используй шкалу Саати для сравнения следующих 2 критериев по важности.
                Если первый критерий важнее, верни ответ в виде "1 - один из вариантов",
                если второй критерий важнее, верни ответ в виде "2 - один из вариантов".
                Критерий 1: {crit1.name}.""" +
                (f" Описание критерия 1: {crit1.description}" if crit1.description else "") +
                f"Критерий 2: {crit2.name}." +
                (f" Описание критерия 2: {crit2.description}" if crit2.description else ""))

    def get_alternative_prompt(self, alt1: Alternative, alt2: Alternative, crit: CriterionNode):
        return (f"Используй шкалу Саати для сравнения следующих 2 альтернатив по критерию {crit.name}." +
                (f"Пояснения по критерию: {crit.description}" if crit.description else "") +
                (f"""Если первая альтернатива лучше, верни ответ в виде "1 - один из вариантов",
                если вторая альтернатива лучше, верни ответ в виде "2 - один из вариантов".
                Альтернатива 1: {alt1.name}.""") +
                (f" Описание: {alt1.description}" if alt1.description else "") +
                f"Альтернатива 2: {alt2.name}." +
                (f" Описание: {alt2.description}" if alt2.description else ""))
