from abc import abstractmethod

from PyQt6.QtCore import QThread, pyqtSignal

from domain.AHPState import AHPState
from domain.CriterionNode import CriterionNode
from prompt_generator.PromptGenerator import PromptGenerator


class BaseLLMProvider(QThread):
    finished = pyqtSignal(CriterionNode)
    error = pyqtSignal(str)
    model_path: str
    prompt_generator: PromptGenerator
    state: AHPState

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def generate_matrices(self, node: CriterionNode, expert_idx):
        if not node.is_leaf():
            # Генерируем матрицу для детей текущего узла
            children_names = [child.name for child in node.children]
            node.matrices[expert_idx] = self.generate_criteria_matrix(children_names)
            # Рекурсивно обрабатываем потомков
            for child in node.children:
                self.generate_matrices(child, expert_idx)
        else:
            node.matrices[expert_idx] = self.generate_alternative_matrix(node.name)

    @abstractmethod
    def generate_criteria_matrix(self, criteria_names) -> list[list[float]]:
        n = len(criteria_names)
        matrix = [[1.0 for _ in range(n)] for _ in range(n)]
        for i in range(n - 1):
            for j in range(i + 1, n):
                prompt = self.prompt_generator.get_criteria_prompt(
                    criteria_names[i], criteria_names[j]
                )
                num = BaseLLMProvider.parse_response(self.call_model_stub(prompt))
                matrix[i][j] = num
        return matrix

    @abstractmethod
    def generate_alternative_matrix(self, criterion: str) -> list[list[float]]:
        alternative_names = [alt.name for alt in self.state.alternatives]
        n = len(alternative_names)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n - 1):
            for j in range(i + 1, n):
                prompt = self.prompt_generator.get_alternative_prompt(
                    alternative_names[i], alternative_names[j], criterion
                )
                num = BaseLLMProvider.parse_response(self.call_model_stub(prompt))
                matrix[i][j] = num
        return matrix

    def call_model_stub(self, prompt):
        return '1 - умеренное превосходство'

    @abstractmethod
    def call_model(self, prompt: str) -> str:
        pass

    @staticmethod
    def parse_response(response):
        print(f'response: {response}')
        strs = list(response.split('\n'))
        for s in strs:
            if ' - ' in s:
                response = s
                break
        scale = {
            'равенство': 1,
            'умеренное превосходство': 3,
            'сильное превосходство': 5,
            'очень сильное превосходство': 7,
            'абсолютное превосходство': 9,
            'один из вариантов': 2
        }
        alt, res = response.split(' - ')
        num_res = scale[res]
        if alt == '1':
            return num_res
        return 1/num_res
