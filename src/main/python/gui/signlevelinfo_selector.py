from datetime import date

from PyQt5.QtWidgets import (
    QFrame,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QRadioButton,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QPlainTextEdit,
    QButtonGroup,
    QComboBox,
    QLabel,
    QCompleter,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QErrorMessage
)

from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    pyqtSignal,
    QSize,
    QEvent
)

from lexicon.lexicon_classes import SignLevelInformation
from gui.decorator import check_date_format, check_empty_gloss


class SignLevelNote(QPlainTextEdit):
    # focus_out = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # def focusOutEvent(self, event):
    #     # use focusOutEvent as the proxy for finishing editing
    #     self.focus_out.emit()
    #     super().focusInEvent(event)


class SignLevelInfoLayout(QVBoxLayout):

    def __init__(self, signlevelinfo, mainwindow, app_settings, **kwargs):
        super().__init__(**kwargs)

        self.coder = app_settings['metadata']['coder']
        self.defaulthand = app_settings['signdefaults']['handdominance']

        self.signlevelinfo = signlevelinfo

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)

        gloss_label = QLabel('Gloss:') #  , parent=self)
        lemma_label = QLabel('Lemma:') #  , parent=self)
        source_label = QLabel('Source:') #  , parent=self)
        signer_label = QLabel('Signer:') #  , parent=self)
        freq_label = QLabel('Frequency:') #  , parent=self)
        coder_label = QLabel('Coder:') #  , parent=self)
        update_label = QLabel('Last updated:') #  , parent=self)
        note_label = QLabel('Notes:') #  , parent=self)

        self.gloss_edit = QLineEdit()
        self.gloss_edit.setFocusPolicy(Qt.StrongFocus)
        self.lemma_edit = QLineEdit()
        self.source_edit = QLineEdit()
        self.signer_edit = QLineEdit()
        self.freq_edit = QLineEdit()
        self.coder_edit = QLineEdit()
        self.update_edit = QLineEdit()
        self.note_edit = QPlainTextEdit()

        self.handdominance_buttongroup = QButtonGroup()  # parent=self)
        self.handdominance_l_radio = QRadioButton('Left')
        self.handdominance_l_radio.setProperty('hand', 'L')
        self.handdominance_r_radio = QRadioButton('Right')
        self.handdominance_r_radio.setProperty('hand', 'R')
        self.handdominance_buttongroup.addButton(self.handdominance_l_radio)
        self.handdominance_buttongroup.addButton(self.handdominance_r_radio)

        self.handdominance_layout = QHBoxLayout()
        self.handdominance_box = QGroupBox('Hand dominance')
        self.handdominance_layout.addWidget(self.handdominance_l_radio)
        self.handdominance_layout.addWidget(self.handdominance_r_radio)
        self.handdominance_box.setLayout(self.handdominance_layout)

        self.clear()

        main_layout.addWidget(gloss_label)
        main_layout.addWidget(self.gloss_edit)
        main_layout.addWidget(lemma_label)
        main_layout.addWidget(self.lemma_edit)
        main_layout.addWidget(source_label)
        main_layout.addWidget(self.source_edit)
        main_layout.addWidget(signer_label)
        main_layout.addWidget(self.signer_edit)
        main_layout.addWidget(freq_label)
        main_layout.addWidget(self.freq_edit)
        main_layout.addWidget(coder_label)
        main_layout.addWidget(self.coder_edit)
        main_layout.addWidget(update_label)
        main_layout.addWidget(self.update_edit)
        main_layout.addWidget(note_label)
        main_layout.addWidget(self.note_edit)
        main_layout.addWidget(self.handdominance_box)

        self.set_value()

        self.addLayout(main_layout)

    def set_starting_focus(self):
        self.gloss_edit.setFocus()

    def set_value(self, signlevelinfo=None):
        if not signlevelinfo:
            signlevelinfo = self.signlevelinfo
        if self.signlevelinfo:
            self.gloss_edit.setText(signlevelinfo.gloss)
            self.lemma_edit.setText(signlevelinfo.lemma)
            self.source_edit.setText(signlevelinfo.source)
            self.signer_edit.setText(signlevelinfo.signer)
            self.freq_edit.setText(str(signlevelinfo.frequency))
            self.coder_edit.setText(signlevelinfo.coder)
            self.update_edit.setText(str(signlevelinfo.update_date))
            self.note_edit.setPlainText(signlevelinfo.note if signlevelinfo.note is not None else "")
            self.set_handdominance(signlevelinfo.handdominance)

    def clear(self):
        self.gloss_edit.setPlaceholderText('Enter gloss here... (Cannot be empty)')
        self.lemma_edit.setText("")
        self.source_edit.setText("")
        self.signer_edit.setText("")
        self.freq_edit.setText('1.0')
        self.coder_edit.setText(self.coder)
        self.update_edit.setPlaceholderText('YYYY-MM-DD')
        self.update_edit.setText(str(date.today()))
        # self.note_edit = QPlainTextEdit()  # parent=self)
        self.note_edit.setPlaceholderText('Enter note here...')
        self.set_handdominance(self.defaulthand)

    def set_handdominance(self, handdominance):
        if handdominance == 'R':
            self.handdominance_r_radio.setChecked(True)
        elif handdominance == 'L':
            self.handdominance_l_radio.setChecked(True)

    def get_handdominance(self):
        return 'R' if self.handdominance_r_radio.isChecked() else 'L'

    def get_value(self):
        if self.get_date() and self.get_gloss():
            return {
                'gloss': self.get_gloss(),
                'lemma': self.lemma_edit.text(),
                'source': self.source_edit.text(),
                'signer': self.signer_edit.text(),
                'frequency': float(self.freq_edit.text()),
                'coder': self.coder_edit.text(),
                'date': self.get_date(),
                'note': self.note_edit.toPlainText(),
                'handdominance': self.get_handdominance()
            }

    @check_date_format
    def get_date(self):
        year, month, day = self.update_edit.text().split(sep='-')
        return date(int(year), int(month), int(day))

    @check_empty_gloss
    def get_gloss(self):
        return self.gloss_edit.text()


class SignlevelinfoSelectorDialog(QDialog):
    saved_signlevelinfo = pyqtSignal(SignLevelInformation)

    def __init__(self, signlevelinfo, mainwindow, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        self.settings = app_settings

        self.signlevelinfo_layout = SignLevelInfoLayout(signlevelinfo, mainwindow, app_settings)  # TODO KV delete app_ctx)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.signlevelinfo_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)

        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.signlevelinfo_layout.set_starting_focus()
        self.setMinimumSize(QSize(500, 850))

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:
            signlevelinfo = self.signlevelinfo_layout.get_value()
            self.saved_signlevelinfo.emit(SignLevelInformation(signlevelinfo))
            self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signlevelinfo_layout.clear()
