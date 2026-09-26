from abc import ABC, abstractmethod

from domain.Alternative import Alternative
from domain.CriterionNode import CriterionNode


class IAHPView(ABC):
    @abstractmethod
    def show_error(self, message: str):
        pass

    @abstractmethod
    def show_success(self, message: str):
        pass

    @abstractmethod
    def show_results(self, results_text: str):
        pass

    @abstractmethod
    def update_alternative_names_input(self, count: int):
        pass

    @abstractmethod
    def get_file_path_from_dialog(self) -> str | None:
        pass

    @abstractmethod
    def setup_expert_data_input(self, data: dict):
        pass

    @abstractmethod
    def get_expert_data(self, data: dict):
        pass

    @abstractmethod
    def get_parameters(self) -> dict:
        pass

    @abstractmethod
    def get_model_path(self) -> str:
        pass

    @abstractmethod
    def on_llm_finished(self, results):
        pass

    @abstractmethod
    def on_llm_error(self, error_message):
        pass
