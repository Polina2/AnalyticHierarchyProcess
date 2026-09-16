from PyQt6.QtCore import pyqtSignal
from huggingface_hub import InferenceClient
from os import environ

from LLM_service.BaseLLMProvider import BaseLLMProvider


class APILLMProvider(BaseLLMProvider):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, state):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.client = None
        self.state = state
        # self.paths1 = ['google/gemma-4-26B-A4B-it', 'openai/gpt-oss-20b', 'meta-llama/Llama-3.3-70B-Instruct', 'openai/gpt-oss-20b']
        self.paths = ['Qwen/Qwen3-235B-A22B-Instruct-2507', 'Qwen/Qwen2.5-32B-Instruct', 'Qwen/Qwen3-32B', 'Qwen/Qwen3.5-27B', 'Qwen/Qwen3-8B']# 'Qwen/Qwen3-Coder-480B-A35B-Instruct'
        self.providers = ['together', 'featherless-ai', 'ovhcloud', 'novita', 'fireworks-ai']
        self.i = 0

    def run(self):
        self.client = InferenceClient(
            model=self.model_path,
            token=environ['TOKEN']
        )
        results = {
            'criteria_matrix': self.generate_criteria_matrix(),
            'alternative_matrices': []
        }
        print("criteria generated")
        alternative_descriptions = [alt.description for alt in self.state.alternatives]
        if not alternative_descriptions:
            alternative_descriptions = self.get_alt_descriptions_without_prompt()
        self.prompt_generator.add_desc_to_basic_prompt(alternative_descriptions)
        criteria_names = [crit.name for crit in self.state.criteria_tree.children]
        for crit_name in criteria_names:
            matrix = self.generate_alternative_matrix(crit_name)
            results['alternative_matrices'].append(matrix)
            print("alternative generated")
        self.finished.emit(results)

    def get_alt_descriptions_without_prompt(self):
        return open('../static/translations_short.txt', 'r', encoding='utf8').read()

    def get_alt_descriptions(self, criteria_names, alternative_descriptions_file):
        prompt = self.prompt_generator.get_alt_description_prompt(
            criteria_names, alternative_descriptions_file
        )
        res = self.call_model(prompt)
        return res

    def generate_criteria_matrix(self):
        super().generate_criteria_matrix()

    def generate_alternative_matrix(self, criterion):
        super().generate_alternative_matrix(criterion)

    def call_model(self, prompt):
        print(f'basic_prompt: {self.prompt_generator.get_basic_prompt()}\nprompt{prompt}')
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
