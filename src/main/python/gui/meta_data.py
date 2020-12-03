from PyQt5.QtCore import (
    Qt,
    QSize
)
from PyQt5.QtWidgets import (
    QGroupBox,
    QPlainTextEdit,
    QLineEdit,
    QGridLayout,
    QListView,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QAction,
    QStatusBar
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)


class MetaDataWidget(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        main_layout = QGridLayout()
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        gloss_label = QLabel('Gloss:')
        freq_label = QLabel('Frequency:')
        coder_label = QLabel('Coder:')
        update_label = QLabel('Last updated:')
        note_label = QLabel('Notes:')

        gloss_edit = QLineEdit(parent=self)
        gloss_edit.setPlaceholderText('Enter gloss here')
        freq_edit = QLineEdit('1', parent=self)
        coder_edit = QLineEdit(parent=self)
        update_edit = QLineEdit(parent=self)
        note_edit = QLineEdit(parent=self)

        main_layout.addWidget(gloss_label, 0, 0)
        main_layout.addWidget(gloss_edit, 0, 1)
        main_layout.addWidget(freq_label, 0, 2)
        main_layout.addWidget(freq_edit, 0, 3)
        main_layout.addWidget(coder_label, 1, 0)
        main_layout.addWidget(coder_edit, 1, 1)
        main_layout.addWidget(update_label, 1, 2)
        main_layout.addWidget(update_edit, 1, 3)
        main_layout.addWidget(note_label, 2, 0, 1, 1)
        main_layout.addWidget(note_edit, 2, 1, 1, 3)