from PyQt5.QtCore import (
    Qt,
    QSize
)

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QGridLayout
)

from PyQt5.QtGui import (
    QPixmap
)

from .hand_configuration import ConfigGlobal, Config


class LexicalInformationPanel(QFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        self.setLayout(main_layout)

        gloss_label = QLabel('Gloss:', parent=self)
        freq_label = QLabel('Frequency:', parent=self)
        coder_label = QLabel('Coder:', parent=self)
        update_label = QLabel('Last updated:', parent=self)
        note_label = QLabel('Notes:', parent=self)

        self.gloss_edit = QLineEdit(parent=self)
        self.gloss_edit.setPlaceholderText('Enter gloss here...')
        self.freq_edit = QLineEdit('1.0', parent=self)
        self.coder_edit = QLineEdit(parent=self)
        self.update_edit = QLineEdit(parent=self)
        self.note_edit = QPlainTextEdit(parent=self)
        self.note_edit.setPlaceholderText('Enter note here...')

        main_layout.addWidget(gloss_label)
        main_layout.addWidget(self.gloss_edit)
        main_layout.addWidget(freq_label)
        main_layout.addWidget(self.freq_edit)
        main_layout.addWidget(coder_label)
        main_layout.addWidget(self.coder_edit)
        main_layout.addWidget(update_label)
        main_layout.addWidget(self.update_edit)
        main_layout.addWidget(note_label)
        main_layout.addWidget(self.note_edit)


class HandTranscriptionPanel(QFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)

        main_layout = QGridLayout()
        self.setLayout(main_layout)

        self.global_option = ConfigGlobal(title='Handshape global options', parent=self)
        main_layout.addWidget(self.global_option, 0, 0, 2, 1)

        self.config1 = Config(1, 'Configuration 1', parent=self)
        main_layout.addWidget(self.config1, 0, 1, 1, 2)

        self.config2 = Config(2, 'Configuration 2', parent=self)
        main_layout.addWidget(self.config2, 1, 1, 1, 2)


class HandIllustrationPanel(QFrame):
    def __init__(self, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx

        self.setFrameStyle(QFrame.StyledPanel)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.hand_illustration = QLabel()
        self.hand_illustration.setFixedSize(QSize(400, 400))
        neutral_img = QPixmap(self.app_ctx.hand_illustrations['neutral'])
        self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        main_layout.addWidget(self.hand_illustration)
