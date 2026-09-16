import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, logging
from PyQt6.QtCore import pyqtSignal
from LLM_service.BaseLLMProvider import BaseLLMProvider


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



class LocalLLMProvider(BaseLLMProvider):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, model_path, prompt_generator, state):
        super().__init__()
        self.model_path = model_path
        self.prompt_generator = prompt_generator
        self.state = state
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
            criteria_names = [crit.name for crit in self.state.criteria_tree.children]
            for crit_name in criteria_names:
                matrix = self.generate_alternative_matrix(crit_name)
                results['alternative_matrices'].append(matrix)
                print("alternative generated")

            print("signal emit")
            self.finished.emit(results)
            print("signal emitted")

        except Exception as e:
            self.error.emit(str(e))

    def generate_criteria_matrix(self):
        super().generate_criteria_matrix()

    def generate_alternative_matrix(self, criterion):
        super().generate_alternative_matrix(criterion)

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
