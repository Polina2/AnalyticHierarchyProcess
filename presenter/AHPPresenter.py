from LLM_service.APILLMProvider import APILLMProvider
from LLM_service.LocalLLMProvider import LocalLLMProvider
from calculator.CalculatorFactory import CalculatorFactory
from domain.AHPState import AHPState
from domain.StateRepository import StateRepository
from presenter.IAHPView import IAHPView
from presenter.ResultsFormatter import ResultsFormatter
from prompt_generator.LingScalePromptGenerator import LingScalePromptGenerator


class AHPPresenter:

    def __init__(
            self, view: IAHPView, state: AHPState, calculator_factory: CalculatorFactory
    ):
        self.view = view
        self.state = state
        self.calculator = calculator_factory.create('crisp')
        self.repository = StateRepository()
        self.llm_provider = None
        self._connect_signals()

    def _connect_signals(self):
        self.view.generate_clicked.connect(self.on_generate_clicked)
        self.view.alternatives_changed.connect(self.on_alternatives_changed)
        self.view.confirm_parameters_clicked.connect(self.on_confirm_parameters_clicked)
        self.view.calculate_results_clicked.connect(self.on_calculate_results_clicked)
        self.view.export_clicked.connect(self.on_export_clicked)
        self.view.save_state_clicked.connect(self.on_save_state)
        self.view.load_state_clicked.connect(self.on_load_state)

    def on_save_state(self, file_path: str):
        """Обработчик сохранения."""
        try:
            self.view.get_expert_data(self.state.to_data())

            self.repository.save(self.state, file_path)
            self.view.show_success("Прогресс успешно сохранен!")
        except Exception as e:
            self.view.show_error(f"Ошибка при сохранении:\n{str(e)}")

    def on_load_state(self, file_path: str):
        """Обработчик загрузки."""
        try:
            # Загружаем состояние из файла
            loaded_state = self.repository.load(file_path)

            # Заменяем текущее состояние на загруженное
            self.state = loaded_state

            # Перестраиваем UI на основе нового состояния
            self.view.rebuild_ui_from_state(self.state)

            self.view.show_success("Прогресс успешно загружен!")
        except Exception as e:
            self.view.show_error(f"Ошибка при загрузке:\n{str(e)}")

    def on_generate_clicked(self):
        prompt_generator = LingScalePromptGenerator()
        self._save_alternative_descriptions(prompt_generator)
        model_path = self.view.get_model_path()
        if model_path[0] == '.' or model_path[1] == ':':
            self.llm_provider = LocalLLMProvider(
                model_path=model_path,
                prompt_generator=prompt_generator,
                state=self.state
            )
        else:
            self.llm_provider = APILLMProvider(
                model_path=model_path,
                prompt_generator=prompt_generator,
                state=self.state
            )
        self.llm_provider.finished.connect(self.view.on_llm_finished)
        self.llm_provider.error.connect(self.view.on_llm_error)
        self.llm_provider.start()

    def _save_alternative_descriptions(self, prompt_generator):
        alt_descriptions = self.view.get_alternative_descriptions()
        orig_text = self.view.get_original_text()
        for alt in self.state.alternatives:
            alt.description = alt_descriptions[alt.name]
        alt_descriptions_str = ''
        for alt in self.state.alternatives:
            alt_descriptions_str = '\n'.join([alt_descriptions_str, alt.name, alt.description])
        if not alt_descriptions_str:
            alt_descriptions_str = open('../static/translations_short.txt', 'r', encoding='utf8').read()
        prompt_generator.add_desc_to_basic_prompt(alt_descriptions_str, orig_text)

    def on_confirm_parameters_clicked(self):
        data = self.view.get_parameters()
        self.state.from_data(data)
        self.view.setup_expert_data_input(data)
        self.view.update_llm_tab(data)

    def on_calculate_results_clicked(self):
        # get expert data from ui
        self.view.get_expert_data(self.state.to_data())

        try:
            final_scores = self.calculator.apply(self.state)
            self.state.final_scores = final_scores
        except Exception as e:
            self.view.show_error(str(e))

        result_text = ResultsFormatter.format_results(self.state)
        self.view.show_results(result_text)

    def on_export_clicked(self):
        try:
            file_path = self.view.get_file_path_from_dialog()
            ResultsFormatter.export_to_excel(
                self.state, file_path
            )
            self.view.show_success(f"Результаты экспортированы в файл:\n{file_path}")
        except Exception as e:
            self.view.show_error(f"Ошибка при экспорте в Excel: {str(e)}")

    def on_alternatives_changed(self, value):
        self.view.update_alternative_names_input(value)
