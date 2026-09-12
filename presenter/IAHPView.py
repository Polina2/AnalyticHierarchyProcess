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
    def update_criteria_tree_ui(self, tree: CriterionNode):
        pass

    @abstractmethod
    def update_criteria_names_input(self, count):
        pass

    @abstractmethod
    def update_alternative_names_input(self, count):
        pass

    @abstractmethod
    def update_expert_ui(self, expert_id: int, total: int):
        pass

    @abstractmethod
    def update_matrices_ui(self, node: CriterionNode, expert_id: int):
        pass

    @abstractmethod
    def get_current_expert_id(self) -> int:
        pass

    @abstractmethod
    def get_genres_list(self) -> list[str]:
        pass

    @abstractmethod
    def get_file_path_from_dialog(self) -> str | None:
        pass

    @abstractmethod
    def get_parameters(self) -> dict:
        pass
