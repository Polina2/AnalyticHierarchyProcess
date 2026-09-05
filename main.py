import sys
from PyQt6.QtWidgets import QApplication
from presenter.AHPApplication import AHPApplication


def main():
    app = QApplication(sys.argv)
    window = AHPApplication()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
