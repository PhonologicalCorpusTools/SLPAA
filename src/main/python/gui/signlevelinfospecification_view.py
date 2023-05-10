from datetime import datetime

from PyQt5.QtWidgets import (
    QFrame,
    QLineEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QFormLayout,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QDialogButtonBox,
    QPlainTextEdit,
    QButtonGroup,
    QCheckBox,
    QLabel,
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QSize,
)

from lexicon.lexicon_classes import SignLevelInformation
from gui.decorator import check_empty_gloss


class SignLevelDateDisplay(QLabel):
    def __init__(self, thedatetime=None, **kwargs):
        super().__init__(**kwargs)
        self.set_datetime(thedatetime)
        self.setStyleSheet("border: 1px solid black;")

    def set_datetime(self, thedatetime):
        self.datetime = thedatetime
        if thedatetime is None:
            self.setText("")
        else:
            self.setText(self.datetime.strftime('%Y-%m-%d %I:%M:%S%p'))

    def get_datetime(self):
        return self.datetime

    def reset(self):
        self.set_datetime(None)


# TODO KV redo the order in which init creates itself
class SignLevelInfoPanel(QFrame):

    def __init__(self, signlevelinfo, **kwargs):
        super().__init__(**kwargs)

        self.mainwindow = self.parent().mainwindow
        # self.parentwidget = parentwidget

        self.settings = self.mainwindow.app_settings
        self.coder = self.settings['metadata']['coder']
        self.defaulthand = self.settings['signdefaults']['handdominance']

        self.signlevelinfo = signlevelinfo

        main_layout = QFormLayout()
        main_layout.setSpacing(5)  # TODO KV what is this?

        entryid_label = QLabel("Entry ID:")
        gloss_label = QLabel('Gloss:')
        lemma_label = QLabel('Lemma:')
        source_label = QLabel('Source:')
        signer_label = QLabel('Signer:')
        freq_label = QLabel('Frequency:')
        coder_label = QLabel('Coder:')
        created_label = QLabel('Date created:')
        modified_label = QLabel('Date last modified:')
        note_label = QLabel('Notes:')

        self.entryid_value = QLineEdit()
        self.entryid_value.setText(self.entryid_string())
        self.entryid_value.setEnabled(False)
        self.gloss_edit = QLineEdit()
        self.gloss_edit.setFocusPolicy(Qt.StrongFocus)
        self.lemma_edit = QLineEdit()
        self.source_edit = QLineEdit()
        self.signer_edit = QLineEdit()
        self.freq_edit = QLineEdit()
        self.coder_edit = QLineEdit()
        self.created_display = SignLevelDateDisplay()
        self.modified_display = SignLevelDateDisplay()
        self.note_edit = QPlainTextEdit()

        self.fingerspelled_cb = QCheckBox()
        fingerspelled_label = QLabel('Fingerspelled:')

        handdominance_label = QLabel("Hand dominance:")
        self.handdominance_buttongroup = QButtonGroup()  # parent=self)
        self.handdominance_l_radio = QRadioButton('Left')
        self.handdominance_l_radio.setProperty('hand', 'L')
        self.handdominance_r_radio = QRadioButton('Right')
        self.handdominance_r_radio.setProperty('hand', 'R')
        self.handdominance_buttongroup.addButton(self.handdominance_l_radio)
        self.handdominance_buttongroup.addButton(self.handdominance_r_radio)

        self.handdominance_layout = QHBoxLayout()
        self.handdominance_layout.addWidget(self.handdominance_l_radio)
        self.handdominance_layout.addWidget(self.handdominance_r_radio)
        self.handdominance_layout.addStretch()

        self.clear()

        main_layout.addRow(entryid_label, self.entryid_value)
        main_layout.addRow(gloss_label, self.gloss_edit)
        main_layout.addRow(lemma_label, self.lemma_edit)
        main_layout.addRow(source_label, self.source_edit)
        main_layout.addRow(signer_label, self.signer_edit)
        main_layout.addRow(freq_label, self.freq_edit)
        main_layout.addRow(coder_label, self.coder_edit)
        main_layout.addRow(created_label, self.created_display)
        main_layout.addRow(modified_label, self.modified_display)
        main_layout.addRow(note_label, self.note_edit)
        main_layout.addRow(fingerspelled_label, self.fingerspelled_cb)
        main_layout.addRow(handdominance_label, self.handdominance_layout)

        self.set_value()

        # self.addLayout(main_layout)
        self.setLayout(main_layout)

    def entryid(self):
        if self.signlevelinfo is not None:
            return self.signlevelinfo.entryid
        else:
            return self.mainwindow.corpus.highestID+1

    def entryid_string(self, entryid_int=None):
        numdigits = self.settings['display']['entryid_digits']
        if entryid_int is None:
            entryid_int = self.entryid()
        entryid_string = str(entryid_int)
        entryid_string = "0"*(numdigits-len(entryid_string)) + entryid_string
        return entryid_string

    def set_starting_focus(self):
        self.gloss_edit.setFocus()

    def set_value(self, signlevelinfo=None):
        if not signlevelinfo:
            signlevelinfo = self.signlevelinfo
        if self.signlevelinfo:
            self.entryid_value.setText(self.entryid_string(signlevelinfo.entryid))
            self.gloss_edit.setText(signlevelinfo.gloss)
            self.lemma_edit.setText(signlevelinfo.lemma)
            self.source_edit.setText(signlevelinfo.source)
            self.signer_edit.setText(signlevelinfo.signer)
            self.freq_edit.setText(str(signlevelinfo.frequency))
            self.coder_edit.setText(signlevelinfo.coder)
            self.created_display.set_datetime(signlevelinfo.datecreated)
            self.modified_display.set_datetime(signlevelinfo.datelastmodified)
            self.note_edit.setPlainText(signlevelinfo.note if signlevelinfo.note is not None else "")
            # backward compatibility for attribute added 20230412!
            self.fingerspelled_cb.setChecked(hasattr(signlevelinfo, '_fingerspelled') and signlevelinfo.fingerspelled)
            self.set_handdominance(signlevelinfo.handdominance)

    def clear(self):
        self.gloss_edit.setPlaceholderText('Enter gloss here... (Cannot be empty)')
        self.lemma_edit.setText("")
        self.source_edit.setText("")
        self.signer_edit.setText("")
        self.freq_edit.setText('1.0')
        self.coder_edit.setText(self.coder)
        self.created_display.reset()
        self.modified_display.reset()
        self.note_edit.setPlaceholderText('Enter note here...')
        self.fingerspelled_cb.setChecked(False)
        self.set_handdominance(self.defaulthand)

    def set_handdominance(self, handdominance):
        if handdominance == 'R':
            self.handdominance_r_radio.setChecked(True)
        elif handdominance == 'L':
            self.handdominance_l_radio.setChecked(True)

    def get_handdominance(self):
        return 'R' if self.handdominance_r_radio.isChecked() else 'L'

    def get_value(self):
        if self.get_gloss():
            if self.created_display.text() == "" or self.modified_display.text() == "":
                newtime = datetime.now()
                self.created_display.set_datetime(newtime)
                self.modified_display.set_datetime(newtime)
            return {
                'entryid': self.entryid(),
                'gloss': self.get_gloss(),
                'lemma': self.lemma_edit.text(),
                'source': self.source_edit.text(),
                'signer': self.signer_edit.text(),
                'frequency': float(self.freq_edit.text()),
                'coder': self.coder_edit.text(),
                'date created': self.created_display.get_datetime(),
                'date last modified': self.modified_display.get_datetime(),
                'note': self.note_edit.toPlainText(),
                'fingerspelled': self.fingerspelled_cb.isChecked(),
                'handdominance': self.get_handdominance()
            }

    @check_empty_gloss
    def get_gloss(self):
        return self.gloss_edit.text()


class SignlevelinfoSelectorDialog(QDialog):
    saved_signlevelinfo = pyqtSignal(SignLevelInformation)

    def __init__(self, signlevelinfo, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("Sign-level information")
        self.mainwindow = self.parent().mainwindow
        self.settings = self.mainwindow.app_settings

        self.signlevelinfo_widget = SignLevelInfoPanel(signlevelinfo, parent=self)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.signlevelinfo_widget)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)

        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.signlevelinfo_widget.set_starting_focus()
        self.setMinimumSize(QSize(700, 500))  # width, height

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Cancel:
            self.reject()

        elif standard == QDialogButtonBox.Save:
            sli = self.signlevelinfo_widget.get_value()
            if sli is not None:
                newsignlevelinfo = SignLevelInformation(signlevel_info=sli)
                oldsignlevelinfo = self.signlevelinfo_widget.signlevelinfo
                self.saved_signlevelinfo.emit(newsignlevelinfo)
                if self.mainwindow.current_sign is not None and newsignlevelinfo != oldsignlevelinfo:
                    self.mainwindow.current_sign.lastmodifiednow()
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signlevelinfo_widget.clear()
