import sys
from PyQt5.QtWidgets import QApplication
from model import main_widget


def main():
    app = QApplication(sys.argv)
    ex = main_widget.MainWindow()
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
