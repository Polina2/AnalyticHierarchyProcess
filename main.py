import sys
from PyQt6.QtWidgets import QApplication

from calculator.CalculatorFactory import CalculatorFactory
from domain.AHPState import AHPState
from presenter.AHPApplication import AHPApplication
from presenter.AHPPresenter import AHPPresenter
from prompt_generator.LingScalePromptGenerator import LingScalePromptGenerator


def main():
    app = QApplication(sys.argv)

    window = AHPApplication()
    state = AHPState()
    factory = CalculatorFactory()
    prompt_gen = LingScalePromptGenerator()
    presenter = AHPPresenter(window, state, factory, prompt_gen)

    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
