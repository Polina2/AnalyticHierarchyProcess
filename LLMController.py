import json
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, logging, BitsAndBytesConfig
from PyQt6.QtCore import QThread, pyqtSignal


def _replace_fractions(s):
    i = 0
    new_str = []
    old_str = list(s)
    prev_i = 0
    while i < len(s):
        if s[i] == '/':
            new_str.extend(old_str[prev_i:i-1])
            new_str.extend(list(str(1/int(s[i+1]))))
            prev_i = i+2
            i += 2
        i += 1
    new_str.extend(old_str[prev_i:])
    return ''.join(new_str)


def parse_response(prompt, response, size):
    """Парсинг ответа модели"""
    try:
        # Ищем JSON в ответе
        if prompt in response:
            response = response[len(prompt):]
        print(response)
        start = response.find('{')
        end = response.find('}', start) + 1
        if start != -1 and end != 0:
            response = response[start:end]
            print(response)
            response = _replace_fractions(response)
            print(response)
            data = json.loads(response)
            matrix = data.get('matrix', np.ones((size, size)).tolist())
            return matrix
    except Exception as e:
        print(e)
    # Возвращаем единичную матрицу при ошибке
    return np.identity(size).tolist()


class LLMWorker(QThread):
    """Поток для работы с LLM"""
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, basic_prompt):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.basic_prompt = basic_prompt,
        self.model = None
        self.tokenizer = None
        logging.set_verbosity_info()

    def run(self):
        try:
            # Загружаем модель (кэшируем для скорости)
            self.tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                padding_side='left',
                trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token
                self.tokenizer.pad_token_id = self.tokenizer.eos_token_id
            print("tokenizer loaded, load model")

            # quantization_config = BitsAndBytesConfig(
            #     load_in_4bit=True,
            #     bnb_4bit_quant_type="nf4",
            #     bnb_4bit_compute_dtype="float16",
            # )
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                dtype=torch.bfloat16,
                device_map="cpu",
                trust_remote_code=True,
                attn_implementation="sdpa"#,
                # quantization_config=quantization_config
            )

            print("model loaded")

            print("generate matrices")
            # Генерируем матрицы
            results = {
                'criteria_matrix': self.generate_criteria_matrix(),
                'alternative_matrices': []
            }
            print("criteria generated")
            print(results['criteria_matrix'])
            # Генерируем матрицы для альтернатив по каждому критерию
            for crit_name in self.prompt_generator.criteria_names:
                matrix = self.generate_alternative_matrix(crit_name)
                results['alternative_matrices'].append(matrix)
                print("alternative generated")

            print("signal emit")
            self.finished.emit(results)
            print("signal emitted")

        except Exception as e:
            self.error.emit(str(e))

    def generate_criteria_matrix(self):
        """Генерация матрицы критериев"""
        prompt = self.basic_prompt + self.prompt_generator.get_criteria_prompt

        response = self.call_model(prompt)
        print("got criteria response")
        return parse_response(prompt, response, len(self.prompt_generator.criteria_names))

    def generate_alternative_matrix(self, criterion):
        """Генерация матрицы альтернатив для критерия"""
        prompt = self.basic_prompt + self.prompt_generator.get_alternative_prompt(criterion)

        response = self.call_model(prompt)
        print("got alternative response")
        return parse_response(prompt, response, len(self.prompt_generator.alternative_names))

    def call_model(self, prompt):
        """Вызов модели"""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        print("got input, call model")
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=100,
                temperature=0.7,
                do_sample=True,
                top_p=0.9,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id
            )
        print("got model result")

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
