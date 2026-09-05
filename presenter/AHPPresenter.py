from domain.AHPState import AHPState
from presenter.IAHPView import IAHPView


class AHPPresenter:
    def __init__(self, view: IAHPView, state: AHPState):
        self.view = view
        self.state = state
