from PyQt5.QtCore import (
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QWidget,
    QAction,
    QWidgetAction,
    QLineEdit,
    QFrame,
    QHBoxLayout,
    QMenu,
    QCheckBox,
    QPushButton,
    QLabel,
    QComboBox
)

from lexicon.module_classes import AddedInfo


class ModuleSpecificationPanel(QFrame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.existingkey = None

    def getsavedmodule(self, articulators, timingintervals, addedinfo, inphase):
        pass

    def handle_articulator_changed(self, articulator):
        pass

    def validity_check(self):
        selectionsvalid = True
        warningmessage = ""
        return selectionsvalid, warningmessage


class AddedInfoPushButton(QPushButton):

    def __init__(self, title, **kwargs):
        super().__init__(title, **kwargs)
        self._addedinfo = AddedInfo()

        # styling
        qss = """   
            QPushButton[AddedInfo=true] {
                font: bold;
                /*border: 2px dashed black;*/
            }

            QPushButton[AddedInfo=false] {
                font: normal;
                /*border: 1px solid grey;*/
            }
        """
        self.setStyleSheet(qss)

        self.updateStyle()

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
        self.updateStyle()

    def mouseReleaseEvent(self, event):
        addedinfo_menu = AddedInfoContextMenu(self._addedinfo)
        addedinfo_menu.info_added.connect(self.updateStyle)
        addedinfo_menu.exec_(event.globalPos())

    def updateStyle(self, addedinfo=None):
        if addedinfo is not None:
            self._addedinfo = addedinfo
        self.setProperty('AddedInfo', self._addedinfo.hascontent())
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def clear(self):
        self.addedinfo = AddedInfo()


class AddedInfoContextMenu(QMenu):
    info_added = pyqtSignal(AddedInfo)

    def __init__(self, addedinfo):
        super().__init__()

        self.addedinfo = addedinfo

        self.iconic_action = CheckNoteAction("Iconic")
        self.iconic_action.setChecked(self.addedinfo.iconic_flag)
        self.iconic_action.setText(self.addedinfo.iconic_note)
        self.iconic_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.iconic_action))
        self.addAction(self.iconic_action)

        self.uncertain_action = CheckNoteAction("Uncertain")
        self.uncertain_action.setChecked(self.addedinfo.uncertain_flag)
        self.uncertain_action.setText(self.addedinfo.uncertain_note)
        self.uncertain_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.uncertain_action))
        self.addAction(self.uncertain_action)

        self.estimated_action = CheckNoteAction("Estimated")
        self.estimated_action.setChecked(self.addedinfo.estimated_flag)
        self.estimated_action.setText(self.addedinfo.estimated_note)
        self.estimated_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.estimated_action))
        self.addAction(self.estimated_action)

        self.notspecified_action = CheckNoteAction("Not specified")
        self.notspecified_action.setChecked(self.addedinfo.notspecified_flag)
        self.notspecified_action.setText(self.addedinfo.notspecified_note)
        self.notspecified_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.notspecified_action))
        self.addAction(self.notspecified_action)

        self.variable_action = CheckNoteAction("Variable")
        self.variable_action.setChecked(self.addedinfo.variable_flag)
        self.variable_action.setText(self.addedinfo.variable_note)
        self.variable_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.variable_action))
        self.addAction(self.variable_action)

        self.exceptional_action = CheckNoteAction("Exceptional")
        self.exceptional_action.setChecked(self.addedinfo.exceptional_flag)
        self.exceptional_action.setText(self.addedinfo.exceptional_note)
        self.exceptional_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.exceptional_action))
        self.addAction(self.exceptional_action)

        self.incomplete_action = CheckNoteAction("Incomplete")
        self.incomplete_action.setChecked(self.addedinfo.incomplete_flag)
        self.incomplete_action.setText(self.addedinfo.incomplete_note)
        self.incomplete_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.incomplete_action))
        self.addAction(self.incomplete_action)

        self.other_action = CheckNoteAction("Other")
        self.other_action.setChecked(self.addedinfo.other_flag)
        self.other_action.setText(self.addedinfo.other_note)
        self.other_action.toggled.connect(lambda state: self.checknoteaction_toggled(state, self.other_action))
        self.addAction(self.other_action)

        self.addSeparator()

        self.close_action = QAction("Close menu")
        self.addAction(self.close_action)

        self.aboutToHide.connect(self.savemenunotes)

    def checknoteaction_toggled(self, state, whichaction):

        if whichaction == self.iconic_action:
            self.addedinfo.iconic_flag = state
        elif whichaction == self.uncertain_action:
            self.addedinfo.uncertain_flag = state
        elif whichaction == self.estimated_action:
            self.addedinfo.estimated_flag = state
        elif whichaction == self.notspecified_action:
            self.addedinfo.notspecified_flag = state
        elif whichaction == self.variable_action:
            self.addedinfo.variable_flag = state
        elif whichaction == self.exceptional_action:
            self.addedinfo.exceptional_flag = state
        elif whichaction == self.incomplete_action:
            self.addedinfo.incomplete_flag = state
        elif whichaction == self.other_action:
            self.addedinfo.other_flag = state

    def focusOutEvent(self, event):
        self.savemenunotes()

    def savemenunotes(self):
        self.addedinfo.iconic_note = self.iconic_action.text()
        self.addedinfo.uncertain_note = self.uncertain_action.text()
        self.addedinfo.estimated_note = self.estimated_action.text()
        self.addedinfo.notspecified_note = self.notspecified_action.text()
        self.addedinfo.variable_note = self.variable_action.text()
        self.addedinfo.exceptional_note = self.exceptional_action.text()
        self.addedinfo.incomplete_note = self.incomplete_action.text()
        self.addedinfo.other_note = self.other_action.text()

        self.info_added.emit(self.addedinfo)


class AbstractLocationAction(QWidgetAction):
    textChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.actionwidget = QWidget()
        self.actionlayout = QHBoxLayout()


class CheckNoteAction(AbstractLocationAction):

    def __init__(self, label, parent=None):
        super().__init__(parent)

        self.label = label
        self.checkbox = QCheckBox(self.label)
        self.checkbox.setTristate(False)
        self.checkbox.toggled.connect(self.toggled)
        self.note = QLineEdit()
        self.note.textChanged.connect(self.textChanged.emit)
        self.actionlayout.addWidget(self.checkbox)
        self.actionlayout.addWidget(self.note)
        self.actionwidget.setLayout(self.actionlayout)
        self.setDefaultWidget(self.actionwidget)

    def setChecked(self, state):
        self.checkbox.setChecked(state)

    def isChecked(self):
        return self.checkbox.isChecked()

    def setText(self, text):
        self.note.setText(text)

    def text(self):
        return self.note.text()


class ArticulatorSelector(QWidget):
    articulatorchanged = pyqtSignal(str)

    def __init__(self, articulatorlist, **kwargs):
        super().__init__(**kwargs)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)
        self.multiple = len(articulatorlist) > 1

        self.label = QLabel()
        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.currentTextChanged.connect(lambda text: self.articulatorchanged.emit(self.pluralbrackets(text, False)))
        self.setarticulatoroptions(articulatorlist)

    def pluralbrackets(self, text, onoroff):
        if onoroff:
            return text + "(s)"
        else:
            return text.replace("(s)", "")

    def gettext(self):
        if self.multiple:
            return self.combo.currentText()
        else:
            return self.label.text()

    def getarticulator(self):
        return self.pluralbrackets(self.gettext(), False)

    def setarticulatoroptions(self, articulatorlist):
        self.multiple = len(articulatorlist) > 1
        for idx in range(self.layout.count()):
            w = self.layout.itemAt(idx).widget()
            self.layout.removeWidget(w)

        if self.multiple:
            self.combo.clear()
            self.combo.addItems([self.pluralbrackets(a, True) for a in articulatorlist])
            self.layout.addWidget(self.combo)
        else:
            self.label.clear()
            self.label.setText(self.pluralbrackets(articulatorlist[0], True) or "")
            self.layout.addWidget(self.label)

    def setselectedarticulator(self, articulator):
        if articulator is None or articulator == "":
            text = self.combo.itemText(0)
        else:
            text = self.pluralbrackets(articulator, True)
        if self.multiple:
            if text in [self.combo.itemText(i) for i in range(self.combo.count())]:
                self.combo.setCurrentText(text)
                return True
        else:
            if text == self.label.text():
                return True

        return False
