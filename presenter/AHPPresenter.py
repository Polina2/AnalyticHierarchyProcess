from domain.AHPState import AHPState
from presenter.AHPApplication import AHPApplication
from presenter.IAHPView import IAHPView


class AHPPresenter:
    def __init__(self, view: IAHPView, state: AHPState):
        self.view = view
        self.state = state
        self._connect_signals()

    def _connect_signals(self):
        self.view.generate_clicked.connect(self.on_generate_clicked)
        self.view.criteria_changed.connect(self.on_criteria_changed)
        self.view.alternatives_changed.connect(self.on_alternatives_changed)
        self.view.confirm_parameters_clicked.connect(self.on_confirm_parameters_clicked)
        self.view.calculate_results_clicked.connect(self.on_calculate_results_clicked)
        self.view.export_clicked.connect(self.on_export_clicked)

    def on_generate_clicked(self):
        pass

    def on_confirm_parameters_clicked(self):
        pass

    def on_calculate_results_clicked(self):
        pass

    def on_export_clicked(self):
        self.view.export_to_excel()

    def on_criteria_changed(self, value):
        self.view.update_criteria_names_input(value)

    def on_alternatives_changed(self, value):
        self.view.update_alternative_names_input(value)
