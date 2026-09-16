import sys
import torch
from PyQt6.QtWidgets import QApplication

from calculator.CalculatorFactory import CalculatorFactory
from domain.AHPState import AHPState
from presenter.AHPApplication import AHPApplication
from presenter.AHPPresenter import AHPPresenter


def main():
    app = QApplication(sys.argv)

    window = AHPApplication()
    state = AHPState()
    factory = CalculatorFactory()
    presenter = AHPPresenter(window, state, factory)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
