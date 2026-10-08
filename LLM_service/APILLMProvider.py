from PyQt6.QtCore import pyqtSignal
from huggingface_hub import InferenceClient
from os import environ

from LLM_service.BaseLLMProvider import BaseLLMProvider
from domain.CriterionNode import CriterionNode


class APILLMProvider(BaseLLMProvider):
    finished = pyqtSignal(CriterionNode)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, state):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.client = None
        self.state = state
        self.paths = ['Qwen/Qwen3-235B-A22B-Instruct-2507', 'Qwen/Qwen2.5-32B-Instruct', 'Qwen/Qwen3-32B', 'Qwen/Qwen3.5-27B', 'Qwen/Qwen3-8B']
        self.providers = ['together', 'featherless-ai', 'ovhcloud', 'novita', 'fireworks-ai']
        self.i = 0

    def run(self):
        self.client = InferenceClient(
            model=self.model_path,
            token=environ['TOKEN']
        )

        tree = self.state.criteria_tree
        self.generate_matrices(tree, 0)
        self.finished.emit(tree)

    def get_alt_descriptions(self, criteria_names, alternative_descriptions_file):
        prompt = self.prompt_generator.get_alt_description_prompt(
            criteria_names, alternative_descriptions_file
        )
        res = self.call_model(prompt)
        return res

    def generate_matrices(self, node, expert_idx):
        super().generate_matrices(node, expert_idx)

    def generate_criteria_matrix(self, names):
        return super().generate_criteria_matrix(names)

    def generate_alternative_matrix(self, criterion):
        return super().generate_alternative_matrix(criterion)

    def call_model(self, prompt):
        print(f'prompt {prompt}')
        messages = [
            {
                "role": "system",
                "content": self.prompt_generator.get_basic_prompt()
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        self.sleep(10)
        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=32,
                temperature=0.6
            )
            result = response.choices[0].message.content
            return result
        except Exception as e:
            print(f"Ошибка генерации: {e}")
            print(self.paths[self.i % len(self.paths)])
            self.client = InferenceClient(
                model=self.paths[self.i % len(self.paths)],
                provider=self.providers[self.i % len(self.paths)],
                token=environ['TOKEN']
            )
            self.i += 1
            return self.call_model(prompt)
