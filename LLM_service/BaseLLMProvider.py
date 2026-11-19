from abc import abstractmethod

from PyQt6.QtCore import QThread, pyqtSignal

from domain.AHPState import AHPState
from domain.CriterionNode import CriterionNode
from prompt_generator.PromptGenerator import PromptGenerator


class BaseLLMProvider(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    model_path: str
    prompt_generator: PromptGenerator
    state: AHPState
    mode: str

    @abstractmethod
    def run(self):
        pass

    @abstractmethod
    def generate_matrices(self, node: CriterionNode, expert_idx):
        if not node.is_leaf():
            if self.mode in ('all', 'criteria'):
                # Генерируем матрицу для детей текущего узла
                node.matrices[expert_idx] = self.generate_criteria_matrix(node.children)
            # Рекурсивно обрабатываем потомков
            for child in node.children:
                self.generate_matrices(child, expert_idx)
        else:
            if self.mode in ('all', 'alternatives'):
                node.matrices[expert_idx] = self.generate_alternative_matrix(node)

    @abstractmethod
    def generate_criteria_matrix(self, criteria) -> list[list[float]]:
        n = len(criteria)
        matrix = [[1.0 for _ in range(n)] for _ in range(n)]
        for i in range(n - 1):
            for j in range(i + 1, n):
                prompt = self.prompt_generator.get_criteria_prompt(
                    criteria[i], criteria[j]
                )
                num = BaseLLMProvider.parse_response(self.call_model(prompt))
                matrix[i][j] = num
        return matrix

    @abstractmethod
    def generate_alternative_matrix(self, criterion) -> list[list[float]]:
        alternatives = self.state.alternatives
        n = len(alternatives)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n - 1):
            for j in range(i + 1, n):
                prompt = self.prompt_generator.get_alternative_prompt(
                    alternatives[i], alternatives[j], criterion
                )
                num = BaseLLMProvider.parse_response(self.call_model(prompt))
                matrix[i][j] = num
        return matrix

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
            'абсолютное превосходство': 9
        }
        alt, res = response.split(' - ')
        num_res = scale[res]
        if alt == '1':
            return num_res
        return 1/num_res
