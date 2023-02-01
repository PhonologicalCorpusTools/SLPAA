from PyQt5.QtCore import (
    Qt,
    QSize
)

from PyQt5.QtWidgets import (
    QDialog,
    QGridLayout,
    QToolButton,
    QFrame,
    QDialogButtonBox,
)

from PyQt5.QtGui import (
    QIcon
)


class InitializationDialog(QDialog):
    def __init__(self, app_ctx, blank_func, load_func, preferred_coder_name, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle('Sign Language Phonetic Annotator and Analyzer')

        main_layout = QGridLayout()
        self.setLayout(main_layout)

        blank_corpus_button = QToolButton(parent=self)
        blank_corpus_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        blank_corpus_button.setIcon(QIcon(app_ctx.icons['blank']))
        blank_corpus_button.setIconSize(QSize(32, 32))
        blank_corpus_button.setText('Blank corpus')
        blank_corpus_button.clicked.connect(lambda clicked: self.create_blank_corpus(blank_func, clicked))

        load_corpus_button = QToolButton(parent=self)
        load_corpus_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        load_corpus_button.setIcon(QIcon(app_ctx.icons['load']))
        load_corpus_button.setIconSize(QSize(32, 32))
        load_corpus_button.setText('Load corpus')
        load_corpus_button.clicked.connect(lambda clicked: self.load_corpus(load_func, clicked))

        main_layout.addWidget(blank_corpus_button, 0, 0, 1, 1)
        main_layout.addWidget(load_corpus_button, 0, 1, 1, 1)

        separate_line1 = QFrame()
        separate_line1.setFrameShape(QFrame.HLine)
        separate_line1.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line1, 1, 0, 1, 2)

        # Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        buttons = QDialogButtonBox.Cancel
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box, 2, 0, 1, 2)

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()

    def create_blank_corpus(self, blank_func, clicked):
        # clicked: checked or not, so always false
        blank_func(clicked)
        self.accept()

    def load_corpus(self, load_func, clicked):
        # clicked: checked or not, so always false
        response = load_func(clicked)
        if response:
            self.accept()

