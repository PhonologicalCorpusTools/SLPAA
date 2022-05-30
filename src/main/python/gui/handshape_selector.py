from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFrame,
    QDialogButtonBox,
    QGridLayout,
    QScrollArea,
    QButtonGroup
)

from PyQt5.QtCore import (
    QSize,
    pyqtSignal
)

# from gui.panel import HandTranscriptionPanel
from gui.hand_configuration import ConfigGlobal, Config
# from gui.module_selector import HandSelectionLayout
from lexicon.lexicon_classes import HandshapeTranscription
from gui.module_selector import ModuleSpecificationLayout


class HandTranscriptionPanel(QScrollArea):
    selected_hand = pyqtSignal(int)

    def __init__(self, predefined_ctx, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        # main_layout = QGridLayout()
        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        self.global_info = ConfigGlobal(title='Handshape global options', parent=self)
        # main_layout.addWidget(self.global_info, 0, 0, 2, 1)
        main_layout.addWidget(self.global_info)

        self.config1 = Config(1, 'Configuration 1', predefined_ctx, parent=self)
        # main_layout.addWidget(self.config1, 0, 1, 1, 2)
        main_layout.addWidget(self.config1)

        # TODO KV delete
        # self.config2 = Config(2, 'Configuration 2', predefined_ctx, parent=self)
        # main_layout.addWidget(self.config2, 1, 1, 1, 2)

        self.setWidget(main_frame)

    def clear(self):
        self.global_info.clear()
        self.config1.clear()
        # TODO KV delete
        # self.config2.clear()

    def set_value(self, global_handshape_info, hand_transcription):
        self.global_info.set_value(global_handshape_info)
        self.config1.set_value(hand_transcription.config)  #1)
        # TODO KV delete
        # self.config2.set_value(hand_transcription.config2)

    def change_hand_selection(self, hand):
        if hand == 1:
            self.button1.setChecked(True)
        elif hand == 2:
            self.button2.setChecked(True)
        # TODO KV delete
        # elif hand == 3:
        #     self.button3.setChecked(True)
        # elif hand == 4:
        #     self.button4.setChecked(True)

    def insert_radio_button(self, focused_hand):
        self.selected_hand_group = QButtonGroup(parent=self)
        self.button1, self.button2 = self.config1.insert_radio_button()
        # TODO KV delete
        # self.button3, self.button4 = self.config2.insert_radio_button()

        self.button1.clicked.connect(lambda: self.selected_hand.emit(1))
        self.button2.clicked.connect(lambda: self.selected_hand.emit(2))
        # TODO KV delete
        # self.button3.clicked.connect(lambda: self.selected_hand.emit(3))
        # self.button4.clicked.connect(lambda: self.selected_hand.emit(4))

        if focused_hand == 1:
            self.button1.setChecked(True)
        elif focused_hand == 2:
            self.button2.setChecked(True)
        # TODO KV delete
        # elif focused_hand == 3:
        #     self.button3.setChecked(True)
        # elif focused_hand == 4:
        #     self.button4.setChecked(True)

        self.selected_hand_group.addButton(self.button1, 1)
        self.selected_hand_group.addButton(self.button2, 2)
        # TODO KV delete
        # self.selected_hand_group.addButton(self.button3, 3)
        # self.selected_hand_group.addButton(self.button4, 4)

    def remove_radio_button(self):
        self.config1.remove_radio_button()
        # TODO KV delete
        # self.config2.remove_radio_button()
        self.selected_hand_group.deleteLater()

    def get_hand_transcription(self, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            return self.config1.hand1.get_hand_transcription_list()
        elif hand == 2:
            return self.config1.hand2.get_hand_transcription_list()
        # TODO KV delete
        # elif hand == 3:
        #     return self.config2.hand1.get_hand_transcription_list()
        # elif hand == 4:
        #     return self.config2.hand2.get_hand_transcription_list()

    def set_predefined(self, transcription_list, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            self.config1.hand1.set_predefined(transcription_list)
        elif hand == 2:
            self.config1.hand2.set_predefined(transcription_list)
        # TODO KV delete
        # elif hand == 3:
        #     self.config2.hand1.set_predefined(transcription_list)
        # elif hand == 4:
        #     self.config2.hand2.set_predefined(transcription_list)


# class HandshapeSpecificationLayout(QVBoxLayout):
class HandshapeSpecificationLayout(ModuleSpecificationLayout):
    saved_handshape = pyqtSignal(ConfigGlobal, HandshapeTranscription, dict)

    def __init__(self, predefined_ctx, moduletoload=None, **kwargs):  # TODO KV app_ctx, movement_specifications,
        super().__init__(**kwargs)

        self.panel = HandTranscriptionPanel(predefined_ctx)
        if moduletoload is not None:
            self.panel.set_value(moduletoload[0], moduletoload[1])
        self.addWidget(self.panel)
        #
        # self.treemodel = MovementTreeModel()  # movementparameters=movement_specifications)
        # # if moduletoload is not None:
        # #     self.treemodel = moduletoload
        # # self.rootNode = self.treemodel.invisibleRootItem()
        # if moduletoload:
        #     if isinstance(moduletoload, MovementTreeModel):
        #         self.treemodel = moduletoload
        #     elif isinstance(moduletoload, MovementTree):
        #         # TODO KV - make sure listmodel & listitems are also populated
        #         self.treemodel = moduletoload.getMovementTreeModel()
        # else:
        #     # self.treemodel.populate(self.rootNode)
        #     self.treemodel.populate(self.treemodel.invisibleRootItem())
        #
        # self.listmodel = self.treemodel.listmodel
        #
        # self.comboproxymodel = MovementPathsProxyModel(wantselected=False)  # , parent=self.listmodel
        # self.comboproxymodel.setSourceModel(self.listmodel)
        #
        # self.listproxymodel = MovementPathsProxyModel(wantselected=True)
        # self.listproxymodel.setSourceModel(self.listmodel)
        #
        # search_layout = QHBoxLayout()
        # search_layout.addWidget(QLabel("Enter tree node"))  # TODO KV delete? , self))
        #
        # self.combobox = TreeSearchComboBox(self)
        # self.combobox.setModel(self.comboproxymodel)
        # self.combobox.setCurrentIndex(-1)
        # self.combobox.adjustSize()
        # self.combobox.setEditable(True)
        # self.combobox.setInsertPolicy(QComboBox.NoInsert)
        # self.combobox.setFocusPolicy(Qt.StrongFocus)
        # self.combobox.setEnabled(True)
        # self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        # self.combobox.completer().setFilterMode(Qt.MatchContains)
        # self.combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        # # tct = TreeClickTracker(self)  todo kv
        # # self.combobox.installEventFilter(tct)
        # search_layout.addWidget(self.combobox)
        #
        # self.addLayout(search_layout)
        #
        # selection_layout = QHBoxLayout()
        #
        # self.treedisplay = MovementTreeView()
        # self.treedisplay.setItemDelegate(TreeItemDelegate())
        # self.treedisplay.setHeaderHidden(True)
        # self.treedisplay.setModel(self.treemodel)
        # # TODO KV figure out adding number selector
        # items = self.treemodel.findItems("Number of repetitions", Qt.MatchRecursive)
        # repsindex = self.treemodel.indexFromItem(items[0].child(0, 0))
        # self.treedisplay.openPersistentEditor(repsindex)
        # self.treedisplay.installEventFilter(self)
        # self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        # self.treedisplay.setMinimumWidth(400)
        #
        # selection_layout.addWidget(self.treedisplay)
        #
        # list_layout = QVBoxLayout()
        #
        # self.pathslistview = TreeListView()
        # self.pathslistview.setSelectionMode(QAbstractItemView.MultiSelection)
        # self.pathslistview.setModel(self.listproxymodel)
        # self.pathslistview.setMinimumWidth(400)
        #
        # list_layout.addWidget(self.pathslistview)
        #
        # buttons_layout = QHBoxLayout()
        #
        # sortlabel = QLabel("Sort by:")
        # buttons_layout.addWidget(sortlabel)
        #
        # self.sortcombo = QComboBox()
        # self.sortcombo.addItems(
        #     ["order in tree (default)", "alpha by full path", "alpha by lowest node", "order of selection"])
        # self.sortcombo.setInsertPolicy(QComboBox.NoInsert)
        # # self.sortcombo.completer().setCompletionMode(QCompleter.PopupCompletion)
        # # self.sortcombo.currentTextChanged.connect(self.listproxymodel.sort(self.sortcombo.currentText()))
        # self.sortcombo.currentTextChanged.connect(self.sort)
        # buttons_layout.addWidget(self.sortcombo)
        # buttons_layout.addStretch()
        #
        # self.clearbutton = QPushButton("Clear")
        # self.clearbutton.clicked.connect(self.clearlist)
        # buttons_layout.addWidget(self.clearbutton)
        #
        # list_layout.addLayout(buttons_layout)
        # selection_layout.addLayout(list_layout)
        # self.addLayout(selection_layout)

    def get_savedmodule_signal(self):
        return self.saved_handshape

    def get_savedmodule_args(self):
        return (self.panel.global_info, HandshapeTranscription(self.panel.config1.get_value()))

    def clear(self):
        self.panel.clear()

#  TODO KV copied from movementselectordialog
# class HandshapeSelectorDialog(QDialog):
#     saved_handshape = pyqtSignal(ConfigGlobal, HandshapeTranscription)
#
#     def __init__(self, mainwindow, enable_addnew=False, moduletoload=None, hands=None, **kwargs):
#         super().__init__(**kwargs)
#         self.mainwindow = mainwindow
#         self.system_default_handshape_specifications = mainwindow.system_default_handshape
#
#         main_layout = QVBoxLayout()
#
#         self.hands_layout = HandSelectionLayout(hands)
#         main_layout.addLayout(self.hands_layout)
#
#         self.handshape_layout = HandshapeSpecificationLayout(mainwindow.app_ctx.predefined, moduletoload=moduletoload)
#         main_layout.addLayout(self.handshape_layout)
#
#         separate_line = QFrame()
#         separate_line.setFrameShape(QFrame.HLine)
#         separate_line.setFrameShadow(QFrame.Sunken)
#         main_layout.addWidget(separate_line)
#
#         buttons = None
#         applytext = ""
#         if enable_addnew:
#             buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
#             applytext = "Save and close"
#         else:
#             buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Apply | QDialogButtonBox.Cancel
#             applytext = "Save"
#
#         self.button_box = QDialogButtonBox(buttons, parent=self)
#         if enable_addnew:
#             self.button_box.button(QDialogButtonBox.Save).setText("Save and add another")
#         self.button_box.button(QDialogButtonBox.Apply).setText(applytext)
#
#         # TODO KV keep? from orig locationdefinerdialog:
#         #      Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
#         self.button_box.clicked.connect(self.handle_button_click)
#
#         main_layout.addWidget(self.button_box)
#
#         self.setLayout(main_layout)
#         self.setMinimumSize(QSize(1350, 600))
#
#     def handle_button_click(self, button):
#         standard = self.button_box.standardButton(button)
#
#         if standard == QDialogButtonBox.Cancel:
#             # TODO KV if we are editing an already-existing handshape module, this seems to save anyway
#             self.reject()
#
#         elif standard == QDialogButtonBox.Save:  # save and add another
#             # save info and then refresh screen to enter next handshape module
#             config = self.handshape_layout.panel.config1.get_value()  # TODO KV delete  , self.handshape_layout.panel.config2.get_value()]
#             self.saved_handshape.emit(self.handshape_layout.panel.global_info, HandshapeTranscription(config))
#             self.handshape_layout.clear()  # TODO KV should this use "restore defaults" instead?
#             # self.handshape_layout.refresh_treemodel()
#
#         elif standard == QDialogButtonBox.Apply:  # save and close
#             # save info and then close dialog
#             # configs = [self.handshape_layout.panel.config1.get_value()]  # TODO KV delete , self.handshape_layout.panel.config2.get_value()]
#             config = self.handshape_layout.panel.config1.get_value()
#             self.saved_handshape.emit(self.handshape_layout.panel.global_info, HandshapeTranscription(config)) # s))
#             self.accept()
#
#         elif standard == QDialogButtonBox.RestoreDefaults:  # restore defaults
#             # TODO KV -- where should the "defaults" be defined?
#             self.handshape_layout.clear()
