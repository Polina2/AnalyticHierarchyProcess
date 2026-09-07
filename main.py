import sys
from PyQt6.QtWidgets import QApplication

from domain.AHPState import AHPState
from presenter.AHPApplication import AHPApplication
from presenter.AHPPresenter import AHPPresenter


def main():
    app = QApplication(sys.argv)
    window = AHPApplication()
    state = AHPState()
    presenter = AHPPresenter(window, state)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
