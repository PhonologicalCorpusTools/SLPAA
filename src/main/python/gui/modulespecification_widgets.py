from PyQt5.QtCore import (
    pyqtSignal,
    Qt,
    QItemSelectionModel
)

from PyQt5.QtWidgets import (
    QWidget,
    QAction,
    QWidgetAction,
    QLineEdit,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QMenu,
    QCheckBox,
    QPushButton,
    QLabel,
    QComboBox,
    QCompleter,
    QListView,
    QStyledItemDelegate,
    QSpacerItem,
    QGridLayout,
    QTextEdit,
    QButtonGroup,
    QRadioButton,
    QProxyStyle,
    QTabWidget
)

from PyQt5.QtGui import (
    QStandardItem,
)

from lexicon.module_classes import AddedInfo, PhonLocations, TimingInterval, Signtype, ParameterModule
from constant import treepathdelimiter, userdefinedroles as udr, ModuleTypes


class ModuleSpecificationPanel(QFrame):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.existingkey = None

    def getsavedmodule(self, articulators, timingintervals, phonlocs, addedinfo, inphase):
        pass

    def handle_articulator_changed(self, articulator):
        pass

    def validity_check(self):
        selectionsvalid = True
        warningmessage = ""
        return selectionsvalid, warningmessage


# Styled QPushButton whose text is bolded iff the _hascontent attribute is true
class SpecifyBodypartPushButton(QPushButton):

    def __init__(self, title, **kwargs):
        super().__init__(title, **kwargs)
        self._hascontent = False

        # styling
        qss = """   
            QPushButton[HasContent=true] {
                font: bold;
            }

            QPushButton[HasContent=false] {
                font: normal;
            }
        """
        self.setStyleSheet(qss)
        self.updateStyle()

    @property
    def hascontent(self):
        return self._hascontent

    @hascontent.setter
    def hascontent(self, hascontent):
        self._hascontent = hascontent
        self.updateStyle()

    def updateStyle(self):
        self.setProperty('HasContent', self._hascontent)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def clear(self):
        self._hascontent = False
        self.updateStyle()


# Styled QPushButton whose text is bolded iff the associated AddedInfo object's _hascontent attribute is true
# clicking this type of button spawns an AddedInfoContextMenu
class AddedInfoPushButton(QPushButton):

    def __init__(self, title, **kwargs):
        super().__init__(title, **kwargs)
        self._addedinfo = AddedInfo()

        # styling
        qss = """   
            QPushButton[AddedInfo=true] {
                font: bold;
            }

            QPushButton[AddedInfo=false] {
                font: normal;
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

# menu allowing user to specify whether the relevant object/module/etc is
#   uncertain, estimated, not specified, variable, etc (and add notes for each)
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


# used in both Location and Movement modules to display flattened paths list of selected nodes in tree
class TreeListView(QListView):

    def __init__(self):
        super().__init__()

    # sets the currently selected index to be indexint
    # if indexint is -1:
    #   if there's at least one item in the list then the first one is selected
    #   if there's no content in the list then nothing happens
    def setindex(self, indexint):
        if indexint == -1:
            if self.model().rowCount() > 0:
                indexint = 0
            else:
                return
        indexobj = self.model().index(indexint, 0)
        self.setCurrentIndex(indexobj)

    def keyPressEvent(self, event):
        key = event.key()
        # modifiers = event.modifiers()

        if key == Qt.Key_Delete or key == Qt.Key_Backspace:
            indexesofselectedrows = self.selectionModel().selectedRows()
            selectedlistitems = []
            for itemindex in indexesofselectedrows:
                listitemindex = self.model().mapToSource(itemindex)
                listitem = self.model().sourceModel().itemFromIndex(listitemindex)
                selectedlistitems.append(listitem)
            for listitem in selectedlistitems:
                listitem.unselectpath()

            # select/highlight the item that gets focus after the deletion(s) are done
            currentitemindex = self.selectionModel().currentIndex()
            self.selectionModel().select(currentitemindex, QItemSelectionModel.ClearAndSelect)


# this class ensures that the items in the selected-paths list (for Location and Movement module dialogs, eg)
# are bolded iff they have some content in the right-click menu ("Estimated", "Variable", etc)
class TreePathsListItemDelegate(QStyledItemDelegate):

    def initStyleOption(self, option, index):
        # determine the actual tree item from the proxymodel index argument
        proxymodel = index.model()
        sourceindex = proxymodel.mapToSource(index)
        sourcemodel = proxymodel.sourceModel()
        treeitem = sourcemodel.itemFromIndex(sourceindex).treeitem

        # check whether the treeitem has addedinfo content and bold/unbold as appropriate
        hasaddedinfo = treeitem.addedinfo.hascontent()
        option.font.setBold(hasaddedinfo)

        super().initStyleOption(option, index)


class StatusDisplay(QTextEdit):
    def __init__(self, initialtext="", **kwargs):
        super().__init__(**kwargs)
        self.setText(initialtext)
        # self.setStyleSheet("border: 1px solid black;")  # from when this used to be a QLabel
        self.setReadOnly(True)

    def appendText(self, texttoappend, joinwithnewline=False, joinwithspace=False):
        curtext = self.toPlainText()
        separator = "" if curtext == "" else ("\n" if joinwithnewline else (" " if joinwithspace else ""))
        self.setPlainText(curtext + separator + texttoappend)


class TreeSearchComboBox(QComboBox):
    item_selected = pyqtSignal(QStandardItem)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.refresh_userinput()

    def refresh_userinput(self):
        # It seems silly to do this every time an item is selected, but it's the only way I could
        # figure out getting the user-entered text to clear after selecting a list item
        self.setEditable(False)
        self.setEditable(True)
        self.setInsertPolicy(QComboBox.NoInsert)
        self.setFocusPolicy(Qt.StrongFocus)
        self.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.completer().setFilterMode(Qt.MatchContains)
        self.completer().setCompletionMode(QCompleter.PopupCompletion)
        self.textActivated.connect(self.on_textactivated)
        # this does need to happen both here AND in the class where the combobox is initially created
        self.setCurrentIndex(-1)

    def on_textactivated(self, activatedtext):
        if activatedtext:
            itemstoselect = gettreeitemsinpath(self.parent().treemodel,
                                               activatedtext,
                                               treepathdelimiter)
            if itemstoselect:
                targetitem = itemstoselect[-1]
                if not targetitem.data(Qt.UserRole + udr.nocontrolrole):
                    # as long as the target is selectable, ensure that it's fully checked
                    # and that its ancestors are (at least) partially checked
                    targetitem.setCheckState(Qt.Checked)
                    for item in itemstoselect:
                        if item.checkState() == Qt.Unchecked:
                            item.setCheckState(Qt.PartiallyChecked)
                    self.item_selected.emit(targetitem)
                # either way, clear the combobox text
                self.refresh_userinput()


def gettreeitemsinpath(treemodel, pathstring, delim):
    pathlist = pathstring.split(delim)
    pathitemslists = []
    for level in pathlist:
        pathitemslists.append(treemodel.findItems(level, Qt.MatchRecursive))
    validpathsoftreeitems = findvaliditemspaths(pathitemslists)
    return validpathsoftreeitems[0] if len(validpathsoftreeitems) > 0 else []


def findvaliditemspaths(pathitemslists):
    validpaths = []
    if len(pathitemslists) > 1:  # the path is longer than 1 level
        for lastitem in pathitemslists[-1]:
            for secondlastitem in pathitemslists[-2]:
                if lastitem.parent() == secondlastitem:
                    higherpaths = findvaliditemspaths(pathitemslists[:-2]+[[secondlastitem]])
                    for higherpath in higherpaths:
                        if len(higherpath) == len(pathitemslists)-1:  # TODO KV
                            validpaths.append(higherpath + [lastitem])
    elif len(pathitemslists) == 1:  # the path is only 1 level long (but possibly with multiple options)
        for lastitem in pathitemslists[0]:
            validpaths.append([lastitem])
    else:
        # nothing to add to paths - this case shouldn't ever happen because base case is length==1 above
        # but just in case...
        validpaths = []

    return validpaths

class PhonLocSelection(QWidget): 
    def enable_majorminorphonological_cbs(self, checked):
        self.majorphonloc_cb.setEnabled(checked)
        self.minorphonloc_cb.setEnabled(checked)

    def check_phonologicalloc_cb(self, checked):
        self.phonological_cb.setChecked(True)
    
    def set_phonloc_buttons_from_content(self, phonlocs):
        self.phonological_cb.setChecked(phonlocs.phonologicalloc)
        self.phonetic_cb.setChecked(phonlocs.phoneticloc)

        if (hasattr(self, "majorphonloc_cb") and hasattr(self, "minorphonloc_cb")):
            self.majorphonloc_cb.setChecked(phonlocs.majorphonloc)
            self.minorphonloc_cb.setChecked(phonlocs.minorphonloc)
            self.majorphonloc_cb.setEnabled(phonlocs.phonologicalloc)
            self.minorphonloc_cb.setEnabled(phonlocs.phonologicalloc)
        
    def getcurrentphonlocs(self):
        phonlocs = PhonLocations(
            phonologicalloc=self.phonological_cb.isChecked(),
            majorphonloc= hasattr(self, "majorphonloc_cb") and self.majorphonloc_cb.isEnabled() and self.majorphonloc_cb.isChecked(),
            minorphonloc= hasattr(self, "minorphonloc_cb") and self.minorphonloc_cb.isEnabled() and self.minorphonloc_cb.isChecked(),
            phoneticloc=self.phonetic_cb.isChecked()
        )
        return phonlocs

    def clear(self):
        if (hasattr(self, "majorphonloc_cb") and hasattr(self, "minorphonloc_cb")):
            self.majorphonloc_cb.setChecked(False)
            self.minorphonloc_cb.setChecked(False)
            self.majorphonloc_cb.setEnabled(False)
            self.minorphonloc_cb.setEnabled(False)
        self.phonological_cb.setChecked(False)
        self.phonetic_cb.setChecked(False)


    def __init__(self, isLocationModule=False): 
        super().__init__() 
        phonloc_layout = QHBoxLayout()

        phonological_layout = QVBoxLayout()
        self.phonological_cb = QCheckBox("Phonological")
        phonological_layout.addWidget(self.phonological_cb)
        phonological_layout.setAlignment(self.phonological_cb, Qt.AlignTop)

        if (isLocationModule):
            phonological_sublayout = QGridLayout()
            self.phonological_cb.toggled.connect(self.enable_majorminorphonological_cbs)
            self.majorphonloc_cb = QCheckBox("Major")
            self.majorphonloc_cb.toggled.connect(self.check_phonologicalloc_cb)
            self.minorphonloc_cb = QCheckBox("Minor")
            self.minorphonloc_cb.toggled.connect(self.check_phonologicalloc_cb)
            phonological_sublayout.addWidget(self.majorphonloc_cb, 0,1)
            phonological_sublayout.addWidget(self.minorphonloc_cb, 1,1)
            phonological_sublayout.addItem(QSpacerItem(25,0), 0,0)
            
            self.majorphonloc_cb.setEnabled(False)
            self.minorphonloc_cb.setEnabled(False)
            self.majorphonloc_cb.setChecked(False)
            self.minorphonloc_cb.setChecked(False)
            phonological_layout.addLayout(phonological_sublayout)

        phonloc_layout.addLayout(phonological_layout)


        self.phonetic_cb = QCheckBox("Phonetic")
        phonloc_layout.addWidget(self.phonetic_cb)
        phonloc_layout.setAlignment(self.phonetic_cb, Qt.AlignTop)

        self.setLayout(phonloc_layout)

        # Set default state
        self.phonological_cb.setChecked(False)
        self.phonetic_cb.setChecked(False)


# this radio button class tracks not only its current state
#   (and, as usual, mutual exclusivity with buttons in the same group)
#   but also, when a group button is toggled, updates the group with its identity
#   for the purposes of being able to un-check when appropriate
class DeselectableRadioButton(QRadioButton):

    def __init__(self, text, **kwargs):
        super().__init__(text, **kwargs)

    def setChecked(self, checked):
        # can deal with programmatically unselected btns as well
        if self.group() is not None:
            if checked:
                self.group().previously_checked = self
            else:
                self.group().previously_checked = None
        super().setChecked(checked)


# this buttongroup allows for unchecking buttons even when the group is set to mutually exclusive
class DeselectableRadioButtonGroup(QButtonGroup):

    def __init__(self, buttonslist=None, **kwargs):
        # buttonslist: list of QRadioButton to be included as a group
        super().__init__(**kwargs)
        if buttonslist is not None:
            [self.addButton(button) for button in buttonslist]

        # in order to compare new checked button with previously-checked button
        self.previously_checked = None

        self.buttonClicked.connect(self.handle_button_clicked)

    def handle_button_clicked(self, btn):
        if self.previously_checked == btn:
            # user clicked an already-selected button; we'll uncheck it
            self.setExclusive(False)
            btn.setChecked(False)
            self.setExclusive(True)
            self.previously_checked = None
        else:
            # user clicked a previously-unselected button
            self.previously_checked = btn


class BoldableTabWidget(QTabWidget):
    def __init__(self):
        super().__init__()
        self.tab_bar = self.tabBar()
        self.tab_bar.setStyle(BoldTabBarStyle())
        self.currentChanged.connect(self.on_tab_change)

    def __repr__(self):
        current_index = self.currentIndex()
        current_tab = self.tabText(current_index) if current_index >= 0 else "None"
        count = self.count()
        return (f"<{self.__class__.__name__} "
                f"selected: '{current_tab}' (tab # {current_index} out of {count})")

    def check_components(self, widget):
        all_cb = widget.findChildren(QCheckBox)
        all_rb = widget.findChildren(QRadioButton)
        all_ai = widget.findChildren(AddedInfoPushButton)
        return any(btn.isChecked() for btn in all_rb+all_cb) or any(btn.addedinfo.hascontent() for btn in all_ai)

    def decide_bold_label(self):
        # called when tab selection updates.
        # it decides which tabs need the label bolded
        idx = 0
        while self.widget(idx) is not None:
            need_bold = self.check_components(self.widget(idx))
            self.tab_bar.style().setBoldTabIndex(idx, need_bold)
            idx += 1

    def get_bold_indices(self):
        return self.tab_bar.style().bold_tab_index

    def get_nested_tabs(self, idx):
        # returns None or QTabWidget
        widget = self.widget(idx)
        if widget is None:
            return False
        nested_tabs = widget.findChildren(QTabWidget)
        if len(nested_tabs) > 1:
            raise NotImplementedError("Hi future developers, nesting many QTabWidgets is not expected as of July 2025!")
        return nested_tabs[0] if nested_tabs else None

    # wrapper for decide_bold_label(). it applies bolding to matrix and nested tabs
    def on_tab_change(self, index):
        self.decide_bold_label()  # decide bold for the current tab

        # and then check if nested tab needs to be bolded
        nested_tab = self.get_nested_tabs(index)
        if nested_tab:
            nested_tab.decide_bold_label()

        self.setCurrentIndex(index)  # finally move the selection


class BoldTabBarStyle(QProxyStyle):
    def __init__(self, bold_tab_index=None):
        super().__init__()
        if bold_tab_index is not None:
            self.bold_tab_index = bold_tab_index
        else:
            self.bold_tab_index = []

    def drawControl(self, element, option, painter, widget=None):
        if element == self.CE_TabBarTabLabel:
            painter.save()

            # Check if the current tab index is the bold one
            font = painter.font()
            if widget.tabAt(option.rect.center()) in self.bold_tab_index:
                font.setBold(True)
            else:
                font.setBold(False)
            painter.setFont(font)

            super().drawControl(element, option, painter, widget)
            painter.restore()  # call painter.restore() as painter.save() called in the beginning of the conditional

        else:
            # for others, just pass to super()
            super().drawControl(element, option, painter, widget)

    def sizeFromContents(self, contents_type, option, size, widget=None):
        if contents_type == self.CT_TabBarTab:
            size = super().sizeFromContents(contents_type, option, size, widget)
            size.setWidth(int(size.width() * 1.15))  # Increase the rectangle width by 20%
            return size
        return super().sizeFromContents(contents_type, option, size, widget)

    def setBoldTabIndex(self, index, need_bold=True):
        if isinstance(index, int):
            if need_bold:
                # need bold tab label, so indicate this by adding index to the list
                self.bold_tab_index.append(index)
                self.bold_tab_index = list(set(self.bold_tab_index))
                return
            try:
                self.bold_tab_index.remove(index)
            except ValueError:  # index at hand not in bold_tab_index list but ok
                pass

        elif isinstance(index, list):
            self.bold_tab_index.extend(index)
