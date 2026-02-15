from PyQt6.QtCore import QThread, pyqtSignal
from huggingface_hub import InferenceClient
from LLMController import parse_response
from os import environ


class LLMWorkerClient(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, basic_prompt, alt_description):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.basic_prompt = basic_prompt
        self.alt_description = alt_description
        self.client = None

    def run(self):
        try:
            self.client = InferenceClient(
                model=self.model_path,
                token=environ['TOKEN']
            )
            results = {
                'criteria_matrix': self.generate_criteria_matrix(),
                'alternative_matrices': []
            }
            print("criteria generated")
            for crit_name in self.prompt_generator.criteria_names:
                matrix = self.generate_alternative_matrix(crit_name)
                results['alternative_matrices'].append(matrix)
                print("alternative generated")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def generate_criteria_matrix(self):
        criteria_names = self.prompt_generator.criteria_names
        criteria_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(criteria_names)])
        n = len(criteria_names)

        prompt = self.prompt_generator.get_criteria_prompt_for_client(criteria_list, n)

        return self._generate_matrix(prompt, n)

    def generate_alternative_matrix(self, criterion_name):
        alternative_names = self.prompt_generator.alternative_names
        alt_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(alternative_names)])
        n = len(alternative_names)

        prompt = (self.prompt_generator
                  .get_alternative_prompt_for_client(criterion_name, alt_list, n, self.alt_description))

        return self._generate_matrix(prompt, n)

    def _generate_matrix(self, prompt, n):
        messages = [
            {
                "role": "system",
                "content": self.basic_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        try:
            response = self.client.chat_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.4
            )

            result = response.choices[0].message.content
            result = parse_response(prompt, result, n)
            return result
        except Exception as e:
            print(f"Ошибка генерации: {e}")
