from PyQt6.QtCore import QThread, pyqtSignal
from huggingface_hub import InferenceClient
# from LLMController import parse_response
from os import environ
from re import fullmatch


class LLMWorkerClient(QThread):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, criteria_names, alternative_names, alternative_descriptions_file):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.client = None
        self.criteria_names = criteria_names
        self.alternative_names = alternative_names
        self.alternative_descriptions = None
        self.alternative_descriptions_file = alternative_descriptions_file
        # self.paths1 = ['google/gemma-4-26B-A4B-it', 'openai/gpt-oss-20b', 'meta-llama/Llama-3.3-70B-Instruct', 'openai/gpt-oss-20b']
        self.paths = ['Qwen/Qwen3-235B-A22B-Instruct-2507', 'Qwen/Qwen2.5-32B-Instruct', 'Qwen/Qwen3-32B', 'Qwen/Qwen3.5-27B', 'Qwen/Qwen3-8B']# 'Qwen/Qwen3-Coder-480B-A35B-Instruct'
        self.providers = ['together', 'featherless-ai', 'ovhcloud', 'novita', 'fireworks-ai']
        self.i = 0

    def run(self):
        # try:
        self.client = InferenceClient(
            model=self.model_path,
            token=environ['TOKEN']
        )
        results = {
            'criteria_matrix': self.generate_criteria_matrix(),
            'alternative_matrices': []
        }
        print("criteria generated")
        self.alternative_descriptions = self.get_alt_descriptions_without_prompt()
        self.prompt_generator.add_desc_to_basic_prompt(self.alternative_descriptions)
        for crit_name in self.criteria_names:
            matrix = self.generate_alternative_matrix(crit_name)
            results['alternative_matrices'].append(matrix)
            print("alternative generated")
        self.finished.emit(results)

        # except Exception as e:
        #     print(e)
            # self.error.emit(str(e))

    def get_alt_descriptions_without_prompt(self):
        return open('./static/translations_short.txt', 'r', encoding='utf8').read()

    def get_alt_descriptions(self):
        prompt = self.prompt_generator.get_alt_description_prompt(
            self.criteria_names, self.alternative_descriptions_file
        )
        res = self._get_response_from_llm(prompt)
        return res

    def _parse_response(self, response):
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
        if alt == 1:
            return num_res
        return 1/num_res

    def generate_criteria_matrix(self):
        n = len(self.criteria_names)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n-1):
            for j in range(i+1, n):
                prompt = self.prompt_generator.get_criteria_prompt(
                    self.criteria_names[i], self.criteria_names[j]
                )
                num = self._parse_response(self._get_response_from_llm(prompt))
                matrix[i][j] = num
        return matrix

    def generate_alternative_matrix(self, crit):
        n = len(self.alternative_names)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n-1):
            for j in range(i+1, n):
                prompt = self.prompt_generator.get_alternative_prompt(
                    self.alternative_names[i], self.alternative_names[j], crit
                )
                num = self._parse_response(self._get_response_from_llm(prompt))
                matrix[i][j] = num
        return matrix

    def generate_criteria_matrix_short(self):
        n = len(self.criteria_names)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n):
            for j in range(i+1, n):
                prompt = self.prompt_generator.get_criteria_prompt(self.criteria_names[i], self.criteria_names[j])
                num = self._get_response_from_llm(prompt)
                print(num)
                matrix[i][j] = int(num) if '/' not in num else 1/int(num[-1])
        return matrix

    def generate_alternative_matrix_short(self, crit):
        n = len(self.alternative_descriptions)
        matrix = [[1 for _ in range(n)]] * n
        for i in range(n):
            for j in range(i+1, n):
                alt1 = self.alternative_descriptions[i]
                alt2 = self.alternative_descriptions[j]
                prompt = self.prompt_generator.get_alternative_prompt(alt1, alt2, crit)
                num = self._get_response_from_llm(prompt)
                print(num)
                if fullmatch(r'\d', num):
                    matrix[i][j] = int(num)
                elif fullmatch(r'1/\d', num):
                    matrix[i][j] = 1/int(num[-1])
                else:
                    matrix[i][j] = 1
                # matrix[i][j] = int(num) if '/' not in num else 1/int(num[-1])
        return matrix

    def _get_response_from_llm(self, prompt):
        print(f'basic_prompt: {self.prompt_generator.basic_prompt}\nprompt{prompt}')
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
            print(self.paths[self.i])
            self.client = InferenceClient(
                model=self.paths[self.i % len(self.paths)],
                provider=self.providers[self.i % len(self.paths)],
                token=environ['TOKEN']
            )
            self.i += 1
            return self._get_response_from_llm(prompt)

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
