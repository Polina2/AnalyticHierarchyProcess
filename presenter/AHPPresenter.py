from LLM_service.APILLMProvider import APILLMProvider
from LLM_service.LocalLLMProvider import LocalLLMProvider
from calculator.CalculatorFactory import CalculatorFactory
from domain.AHPState import AHPState
from domain.StateRepository import StateRepository
from presenter.IAHPView import IAHPView
from presenter.ResultsFormatter import ResultsFormatter
from preset.CriteriaPresetManager import CriteriaPresetManager
from prompt_generator.LingScalePromptGenerator import LingScalePromptGenerator


class AHPPresenter:

    def __init__(
            self, view: IAHPView, state: AHPState, calculator_factory: CalculatorFactory
    ):
        self.view = view
        self.state = state
        self.calculator = calculator_factory.create('crisp')
        self.repository = StateRepository()
        self.preset_manager = CriteriaPresetManager()
        self.prompt_generator = LingScalePromptGenerator()
        self.llm_provider = None
        self._connect_signals()
        self._refresh_presets_ui()
        self.view.set_basic_prompt(self.prompt_generator.basic_prompt)

    def _connect_signals(self):
        self.view.basic_prompt_changed.connect(self.on_basic_prompt_changed)
        self.view.alternative_description_changed.connect(self.on_alt_desc_changed)
        self.view.criterion_description_changed.connect(self.on_crit_desc_changed)
        self.view.generate_criteria_clicked.connect(self.on_generate_criteria)
        self.view.generate_alternatives_clicked.connect(self.on_generate_alternatives)
        # self.view.generate_clicked.connect(self.on_generate_clicked)
        self.view.alternatives_changed.connect(self.on_alternatives_changed)
        self.view.confirm_parameters_clicked.connect(self.on_confirm_parameters_clicked)
        self.view.calculate_results_clicked.connect(self.on_calculate_results_clicked)
        self.view.export_clicked.connect(self.on_export_clicked)
        self.view.save_state_clicked.connect(self.on_save_state)
        self.view.load_state_clicked.connect(self.on_load_state)
        self.view.preset_load_requested.connect(self.on_preset_load)

    def on_basic_prompt_changed(self, text: str):
        """Обновляем базовый промпт в генераторе."""
        self.prompt_generator.basic_prompt = text

    def on_alt_desc_changed(self, name: str, description: str):
        """Обновляем описание альтернативы в состоянии."""
        for alt in self.state.alternatives:
            if alt.name == name:
                alt.description = description
                break

    def on_crit_desc_changed(self, name: str, description: str):
        """Обновляем описание критерия в дереве."""
        node = self._find_criterion_node(self.state.criteria_tree, name)
        if node:
            node.description = description

    def _find_criterion_node(self, node: 'CriterionNode', name: str) -> 'CriterionNode':
        """Рекурсивный поиск узла по имени."""
        if node.name == name:
            return node
        for child in node.children:
            found = self._find_criterion_node(child, name)
            if found:
                return found
        return None

    def on_generate_criteria(self):
        # Обработчик будет позже
        pass

    def on_generate_alternatives(self):
        # Обработчик будет позже
        pass

    def _refresh_presets_ui(self, selected: str = None):
        presets = self.preset_manager.get_all_presets()
        self.view.refresh_presets_list(presets, selected)

    def on_preset_load(self, name: str):
        """Загрузка встроенного пресета."""
        try:
            json_str = self.preset_manager.load_preset(name)
            loaded_state = AHPState.from_json(json_str)

            # Подменяем состояние
            self.state = loaded_state
            self.state.genre_preset = name

            # Перестраиваем UI
            self.view.rebuild_ui_from_state(self.state)
            self._refresh_presets_ui(selected=name)
            self.view.show_success(f"Стиль '{name}' загружен")
        except Exception as e:
            self.view.show_error(f"Ошибка загрузки:\n{e}")

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
        model_path = self.view.get_model_path()
        if model_path[0] == '.' or model_path[1] == ':':
            self.llm_provider = LocalLLMProvider(
                model_path=model_path,
                prompt_generator=self.prompt_generator,
                state=self.state
            )
        else:
            self.llm_provider = APILLMProvider(
                model_path=model_path,
                prompt_generator=self.prompt_generator,
                state=self.state
            )
        self.llm_provider.finished.connect(self.view.on_llm_finished)
        self.llm_provider.error.connect(self.view.on_llm_error)
        self.llm_provider.start()

    def on_confirm_parameters_clicked(self):
        try:
            data = self.view.get_parameters()
            self.state.from_data(data)
            self.view.setup_expert_data_input(data)
            self.view.update_alternatives_descriptions(self.state.alternatives)
            self.view.update_criteria_descriptions(self.state.criteria_tree)
        except Exception as e:
            self.view.show_error(str(e))
        # self.view.update_llm_tab(data)

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
