from datetime import datetime

from PyQt5.QtWidgets import (
    QLineEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QFormLayout,
    QRadioButton,
    QVBoxLayout,
    QDialogButtonBox,
    QPlainTextEdit,
    QButtonGroup,
    QCheckBox,
    QLabel,
    QListView,
    QMessageBox
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QSize,
    QStringListModel
)

from lexicon.lexicon_classes import SignLevelInformation
from lexicon.module_classes import EntryID
from gui.decorator import check_empty_gloss, check_duplicated_lemma, check_empty_glosslemmaIDgloss
from gui.modulespecification_widgets import TreeListView


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


# This model supplies the data for the multiple-glosses editor QListView() in the SignLevelInfoPanel
class GlossesListModel(QStringListModel):
    enterglosshere_label = 'Double-click to enter gloss here (cannot be empty)'

    def __init__(self, gloss_strings=None, **kwargs):
        super().__init__(**kwargs)
        self.setStringList(gloss_strings)
        self.dataChanged.connect(lambda tl, br: self.setStringList(self.glosses()))

    # Set the model's stringList to the list of glosses provided, plus:
    #   (a) if empty, a default placeholder item, and
    #   (b) no matter what, a final empty item that is used by the view to allow users to add items.
    def setStringList(self, gloss_strings):
        if gloss_strings is None:
            gloss_strings = []
        gloss_strings = [g for g in gloss_strings if len(g.strip()) > 0]
        if len(gloss_strings) == 0:
            gloss_strings = [self.enterglosshere_label]
        gloss_strings += [""]

        super().setStringList(gloss_strings)

    # This function returns the list of actual glosses in the model.
    # The return list does *not* include
    #   (a) entries with length 0 or consisting solely of whitespace, or
    #   (b) the default placeholder entry 'Double-click to enter gloss here (cannot be empty)'.
    # This is as opposed to stringList(), which returns *all* the items in the model, including
    # potentially empty and/or default entries.
    # The intention is that stringList() should be used by GUI elements such as the model view,
    # whereas glosses() should be used by data elements such as SignLevelInformation.
    def glosses(self):
        glosses = self.stringList()
        return [g for g in glosses if len(g.strip()) > 0 and g != self.enterglosshere_label]

    def clear(self):
        self.setStringList(None)


class GlossesListView(QListView):

    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        key = event.key()
        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
            indexesofselectedrows = self.selectionModel().selectedRows()
            for itemindex in indexesofselectedrows:
                self.model().removeRow(itemindex.row())


class SignLevelInfoPanel(QFrame):

    def __init__(self, signlevelinfo, **kwargs):
        super().__init__(**kwargs)

        self.mainwindow = self.parent().mainwindow

        self.settings = self.mainwindow.app_settings
        self.coder = self.settings['metadata']['coder']
        self.defaulthand = self.settings['signdefaults']['handdominance']

        self.signlevelinfo = signlevelinfo

        main_layout = QFormLayout()
        main_layout.setSpacing(5)

        entryid_label = QLabel("Entry ID:")
        self.entryid_value = QLineEdit()
        self.entryid_value.setEnabled(False)

        gloss_label = QLabel('Gloss(es):')
        # as of 20231208, gloss is now a list rather than a string
        self.glosses_view = GlossesListView()
        self.glosses_view.setMaximumHeight(100)
        self.glosses_model = GlossesListModel()
        self.glosses_view.setModel(self.glosses_model)
        self.glosses_view.setFocusPolicy(Qt.StrongFocus)

        lemma_label = QLabel('Lemma:')
        self.lemma_edit = QLineEdit()
        idgloss_label = QLabel('ID-gloss:')
        self.idgloss_edit = QLineEdit()
        source_label = QLabel('Source:')
        self.source_edit = QLineEdit()
        signer_label = QLabel('Signer:')
        self.signer_edit = QLineEdit()
        freq_label = QLabel('Frequency:')
        self.freq_edit = QLineEdit()
        coder_label = QLabel('Coder:')
        self.coder_edit = QLineEdit()
        created_label = QLabel('Date created:')
        self.created_display = SignLevelDateDisplay()
        modified_label = QLabel('Date last modified:')
        self.modified_display = SignLevelDateDisplay()
        note_label = QLabel('Notes:')
        self.note_edit = QPlainTextEdit()
        fingerspelled_label = QLabel('Fingerspelled:')
        self.fingerspelled_cb = QCheckBox()
        compoundsign_label = QLabel('Compound sign:')
        self.compoundsign_cb = QCheckBox()

        handdominance_label = QLabel("Hand dominance:")
        self.handdominance_buttongroup = QButtonGroup()
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
        main_layout.addRow(gloss_label, self.glosses_view)
        main_layout.addRow(lemma_label, self.lemma_edit)
        main_layout.addRow(idgloss_label, self.idgloss_edit)
        main_layout.addRow(source_label, self.source_edit)
        main_layout.addRow(signer_label, self.signer_edit)
        main_layout.addRow(freq_label, self.freq_edit)
        main_layout.addRow(coder_label, self.coder_edit)
        main_layout.addRow(created_label, self.created_display)
        main_layout.addRow(modified_label, self.modified_display)
        main_layout.addRow(note_label, self.note_edit)
        main_layout.addRow(fingerspelled_label, self.fingerspelled_cb)
        main_layout.addRow(compoundsign_label, self.compoundsign_cb)
        main_layout.addRow(handdominance_label, self.handdominance_layout)

        self.set_value()

        self.setLayout(main_layout)

    def entryid_counter(self):
        if self.signlevelinfo is not None:
            return self.signlevelinfo.entryid.counter
        else:
            return self.mainwindow.corpus.highestID+1

    def entryid_string(self):
        if self.signlevelinfo is not None:
            return self.signlevelinfo.entryid.display_string()
        else:
            return ""

    def set_starting_focus(self):
        self.glosses_view.setFocus()

    def set_value(self, signlevelinfo=None):
        if not signlevelinfo:
            signlevelinfo = self.signlevelinfo
        if self.signlevelinfo:
# <<<<<<< HEAD
#             self.entryid_value.setText(self.entryid_string(signlevelinfo.entryid))
#             self.glosses_model.setStringList(signlevelinfo.gloss)
# =======
#             self.entryid_value.setText(self.entryid_string())
#             self.gloss_edit.setText(signlevelinfo.gloss)
# >>>>>>> main
            self.entryid_value.setText(self.entryid_string())
            self.glosses_model.setStringList(signlevelinfo.gloss)
            self.lemma_edit.setText(signlevelinfo.lemma)
            self.idgloss_edit.setText(signlevelinfo.idgloss)
            self.source_edit.setText(signlevelinfo.source)
            self.signer_edit.setText(signlevelinfo.signer)
            self.freq_edit.setText(str(signlevelinfo.frequency))
            self.coder_edit.setText(signlevelinfo.coder)
            self.created_display.set_datetime(signlevelinfo.datecreated)
            self.modified_display.set_datetime(signlevelinfo.datelastmodified)
            self.note_edit.setPlainText(signlevelinfo.note if signlevelinfo.note is not None else "")
            # backward compatibility for attribute added 20230412!
            self.fingerspelled_cb.setChecked(hasattr(signlevelinfo, '_fingerspelled') and signlevelinfo.fingerspelled)
            # backward compatibility for attribute added 20230503!
            self.compoundsign_cb.setChecked(hasattr(signlevelinfo, '_compoundsign') and signlevelinfo.compoundsign)
            self.set_handdominance(signlevelinfo.handdominance)

    def clear(self):
        self.restore_defaults()
        self.created_display.reset()
        self.modified_display.reset()

    def restore_defaults(self):
        self.glosses_model.clear()
        self.lemma_edit.setText("")
        self.idgloss_edit.setText("")
        self.source_edit.setText("")
        self.signer_edit.setText("")
        self.freq_edit.setText('1.0')
        self.coder_edit.setText(self.coder)
        self.note_edit.setPlaceholderText('Enter note here...')
        self.note_edit.clear()
        self.fingerspelled_cb.setChecked(False)
        self.compoundsign_cb.setChecked(False)
        self.set_handdominance(self.defaulthand)

    def set_handdominance(self, handdominance):
        if handdominance == 'R':
            self.handdominance_r_radio.setChecked(True)
        elif handdominance == 'L':
            self.handdominance_l_radio.setChecked(True)

    def get_handdominance(self):
        return 'R' if self.handdominance_r_radio.isChecked() else 'L'

    def get_value(self):
        gloss, lemma, idgloss = self.get_identifiers()
        if gloss or lemma or idgloss:
        # if self.get_gloss():  # and self.get_lemma():
            if self.created_display.text() == "" or self.modified_display.text() == "":
                newtime = datetime.now()
                self.created_display.set_datetime(newtime)
                self.modified_display.set_datetime(newtime)
            return {
                'entryid': self.entryid_counter(),
                'gloss': gloss,  # self.get_gloss(),
                'lemma': lemma,  # self.lemma_edit.text(),
                'idgloss': idgloss,  # self.idgloss_edit.text(),
                'source': self.source_edit.text(),
                'signer': self.signer_edit.text(),
                'frequency': float(self.freq_edit.text()),
                'coder': self.coder_edit.text(),
                'date created': self.created_display.get_datetime(),
                'date last modified': self.modified_display.get_datetime(),
                'note': self.note_edit.toPlainText(),
                'fingerspelled': self.fingerspelled_cb.isChecked(),
                'compoundsign': self.compoundsign_cb.isChecked(),
                'handdominance': self.get_handdominance()
            }

    # @check_empty_gloss
    # @check_empty_glosslemmaIDgloss
    def get_gloss(self):
        return self.glosses_model.glosses()

    @check_empty_glosslemmaIDgloss
    def get_identifiers(self):
        gloss = self.get_gloss()
        lemma = self.lemma_edit.text()
        idgloss = self.idgloss_edit.text()
        return gloss, lemma, idgloss

    # @check_duplicated_lemma
    # def get_lemma(self):
    #     return self.self.lemma_edit.text()


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
                if newsignlevelinfo != oldsignlevelinfo:
                    # if anything other than the last modified date has changed, then lastmodified should be set to now
                    newsignlevelinfo.lastmodifiednow()
                self.check_duplicate_lemma(sli)
                self.saved_signlevelinfo.emit(newsignlevelinfo)
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.signlevelinfo_widget.restore_defaults()

    def check_duplicate_lemma(self, signlevelinfo_dict):
        if not self.settings['reminder']['duplicatelemma']:
            # user doesn't want to see warnings for duplicate lemmas
            return

        if signlevelinfo_dict is None:
            return
        else:
            thislemma = signlevelinfo_dict['lemma']
            lemmasincorpus = self.mainwindow.corpus.get_sign_lemmas()

            if thislemma not in lemmasincorpus:
                return
            elif self.mainwindow.current_sign and self.mainwindow.current_sign.signlevel_information.lemma == thislemma:
                return
            else:
                othersignswiththislemma = [sign for sign in self.mainwindow.corpus.signs
                                           if thislemma == sign.signlevel_information.lemma
                                           and sign != self.mainwindow.current_sign]
                messagetext = "This lemma is also used by the sign(s) listed below:"
                for sign in othersignswiththislemma:
                    glosseslist = sign.signlevel_information.gloss
                    messagetext += "\n - gloss" + \
                                   ("es" if len(glosseslist) > 1 else "") + \
                                   " " + \
                                   ", ".join(glosseslist)
                    if sign.signlevel_information.entryid.display_string() != EntryID.nodisplay:
                        messagetext += " / Entry ID " + sign.signlevel_information.entryid.display_string()
                QMessageBox.warning(self, "Duplicated Lemma", messagetext)

