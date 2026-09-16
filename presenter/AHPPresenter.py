from LLM_service.APILLMProvider import APILLMProvider
from LLM_service.BaseLLMProvider import BaseLLMProvider
from LLM_service.LocalLLMProvider import LocalLLMProvider
from calculator.CalculatorFactory import CalculatorFactory
from domain.AHPState import AHPState
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
        self.llm_provider = None
        self._connect_signals()

    def _connect_signals(self):
        self.view.generate_clicked.connect(self.on_generate_clicked)
        self.view.criteria_changed.connect(self.on_criteria_changed)
        self.view.alternatives_changed.connect(self.on_alternatives_changed)
        self.view.confirm_parameters_clicked.connect(self.on_confirm_parameters_clicked)
        self.view.calculate_results_clicked.connect(self.on_calculate_results_clicked)
        self.view.export_clicked.connect(self.on_export_clicked)

    def on_generate_clicked(self):
        prompt_generator = LingScalePromptGenerator()
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

    def on_confirm_parameters_clicked(self):
        data = self.view.get_parameters()
        self.state.from_data(data)
        self.view.setup_expert_data_input(data)

    def on_calculate_results_clicked(self):
        # get expert data from ui
        crit_matrices, alt_matrices = self.view.get_expert_data(self.state.to_data())
        self.state.criteria_tree.matrices = dict(zip(range(1, len(crit_matrices)+1), crit_matrices))
        for i in range(len(crit_matrices[0])):
            self.state.criteria_tree.children[i].matrices = dict(zip(range(1, len(alt_matrices[0])+1), alt_matrices[i]))

        final_scores = self.calculator.apply(self.state)
        self.state.final_scores = final_scores

        result_text = ResultsFormatter.format_results(self.state.to_data(), *self.state.to_results(), final_scores)
        self.view.show_results(result_text)

    def on_export_clicked(self):
        try:
            file_path = self.view.get_file_path_from_dialog()
            ResultsFormatter.export_to_excel(
                self.state.to_data(), *self.state.to_results(), self.state.final_scores, file_path
            )
            self.view.show_success(f"Результаты экспортированы в файл:\n{file_path}")
        except Exception as e:
            self.view.show_error(f"Ошибка при экспорте в Excel: {str(e)}")

    def on_criteria_changed(self, value):
        self.view.update_criteria_names_input(value)

    def on_alternatives_changed(self, value):
        self.view.update_alternative_names_input(value)
