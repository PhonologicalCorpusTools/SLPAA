# Nonmanual module debugging. make sure to remove this when PR.

from gui.nonmanualspecification_view import NonManualSpecificationPanel

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget


class NonManTest(NonManualSpecificationPanel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 1400, 600)
        self.setWindowTitle("Debugging the non-manual module")

        self.mainwindow = self
        self.module_widget = QWidget()
        self.module_widget = NonManTest(parent=self)

        self.setCentralWidget(self.module_widget)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = TestWindow()
    main_window.show()
    sys.exit(app.exec_())
