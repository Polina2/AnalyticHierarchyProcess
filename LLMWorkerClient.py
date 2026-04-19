from PyQt6.QtCore import QThread, pyqtSignal
from huggingface_hub import InferenceClient
# from LLMController import parse_response
from os import environ
from re import fullmatch


class LLMWorkerClient(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, criteria_names, alternative_names, alternative_descriptions):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.client = None
        self.criteria_names = criteria_names
        self.alternative_names = alternative_names
        self.alternative_descriptions = alternative_descriptions

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
            for crit_name in self.criteria_names:
                matrix = self.generate_alternative_matrix(crit_name)
                results['alternative_matrices'].append(matrix)
                print("alternative generated")
            self.finished.emit(results)

        except Exception as e:
            self.error.emit(str(e))

    def generate_criteria_matrix(self):
        n = len(self.criteria_names)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n):
            for j in range(i+1, n):
                prompt = self.prompt_generator.get_criteria_prompt(self.criteria_names[i], self.criteria_names[j])
                num = self._generate_number(prompt)
                print(num)
                matrix[i][j] = int(num) if '/' not in num else 1/int(num[-1])
        return matrix

    def generate_alternative_matrix(self, crit):
        n = len(self.alternative_descriptions)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n):
            for j in range(i+1, n):
                alt1 = self.alternative_descriptions[i]
                alt2 = self.alternative_descriptions[j]
                prompt = self.prompt_generator.get_alternative_prompt(alt1, alt2, crit)
                num = self._generate_number(prompt)
                print(num)
                if fullmatch(r'\d', num):
                    matrix[i][j] = int(num)
                elif fullmatch(r'1/\d', num):
                    matrix[i][j] = 1/int(num[-1])
                else:
                    matrix[i][j] = 1
                # matrix[i][j] = int(num) if '/' not in num else 1/int(num[-1])
        return matrix

    def _generate_number(self, prompt):
        messages = [
            {
                "role": "system",
                "content": self.prompt_generator.basic_prompt
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
            return result
        except Exception as e:
            print(f"Ошибка генерации: {e}")

    def generate_criteria_matrix_long(self):
        criteria_names = self.prompt_generator.criteria_names
        criteria_list = "\n".join([f"{i + 1}. {name}" for i, name in enumerate(criteria_names)])
        n = len(criteria_names)

        prompt = self.prompt_generator.get_criteria_prompt_for_client(criteria_list, n)

        return self._generate_matrix(prompt, n)

    def generate_alternative_matrix_long(self, criterion_name):
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
            # result = parse_response(prompt, result, n)
            return result
        except Exception as e:
            print(f"Ошибка генерации: {e}")
