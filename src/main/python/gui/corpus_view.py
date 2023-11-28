from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QItemSelectionModel
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QAbstractItemView,
    QRadioButton,
    QButtonGroup
)

from models.corpus_models import CorpusModel, CorpusSortProxyModel
from lexicon.lexicon_classes import Sign
from gui.helper_widget import OptionSwitch


class CorpusTitleEdit(QLineEdit):
    focus_out = pyqtSignal(str)

    def __init__(self, corpus_title, **kwargs):
        super().__init__(**kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def focusOutEvent(self, event):
        # use focusOutEvent as the proxy for finishing editing
        self.focus_out.emit(self.text())
        super().focusInEvent(event)


class CorpusDisplay(QWidget):
    selected_sign = pyqtSignal(Sign)
    title_changed = pyqtSignal(str)

    def __init__(self, corpus_title="", **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # self.corpus_title = QLineEdit(corpus_title, parent=self)
        self.corpus_title = CorpusTitleEdit(corpus_title, parent=self)
        self.corpus_title.focus_out.connect(lambda title: self.title_changed.emit(title))
        self.corpus_title.setPlaceholderText('Untitled')
        main_layout.addWidget(self.corpus_title)

        self.corpus_model = CorpusModel(parent=self)
        self.corpus_view = QListView(parent=self)
        self.corpus_sortproxy = CorpusSortProxyModel(parent=self)
        self.corpus_sortproxy.setSourceModel(self.corpus_model)
        self.corpus_model.modelupdated.connect(lambda: self.corpus_sortproxy.sortnow())
        # self.corpus_view.setModel(self.corpus_model)
        self.corpus_view.setModel(self.corpus_sortproxy)
        self.corpus_view.clicked.connect(self.handle_selection)
        self.corpus_view.setEditTriggers(QAbstractItemView.NoEditTriggers)  # disable edit by double-clicking an item

        # Corpus filter by gloss
        self.corpus_filter_input = QLineEdit()
        self.corpus_filter_input.setPlaceholderText('Filter by gloss')
        self.corpus_filter_input.textChanged.connect(self.filter_corpus_list)
        main_layout.addWidget(self.corpus_filter_input)
        main_layout.addWidget(self.corpus_view)

        sort_layout = QHBoxLayout()
        sortlabel = QLabel("Sort by:")
        sort_layout.addWidget(sortlabel)
        self.sortcombo = QComboBox()
        self.sortcombo.addItems(
            ["alpha by gloss (default)", "alpha by lemma", "date created", "date last modified"])
        self.sortcombo.setInsertPolicy(QComboBox.NoInsert)
        self.sortcombo.currentTextChanged.connect(lambda txt: self.sort(sorttext=txt))
        sort_layout.addWidget(self.sortcombo)
        self.ascend_radio = QRadioButton("↑")
        self.descend_radio = QRadioButton("↓")
        # self.ascend_radio = QRadioButton("∧")
        # self.descend_radio = QRadioButton("∨")
        self.ascenddescend_group = QButtonGroup()
        self.ascenddescend_group.addButton(self.ascend_radio)
        self.ascenddescend_group.addButton(self.descend_radio)
        self.ascend_radio.setChecked(True)
        self.ascenddescend_group.buttonToggled.connect(lambda: self.sort(sortorder=('ascending' if self.ascend_radio.isChecked() else 'descending')))
        sort_layout.addWidget(self.ascend_radio)
        sort_layout.addWidget(self.descend_radio)
        # self.ascenddescend_switch = OptionSwitch("↑", "↓")
        # # self.ascenddescend_switch = OptionSwitch("∧", "∨")
        # self.ascenddescend_switch.left_btn.setChecked(True)
        # self.ascenddescend_switch.shrinksizetotext()
        # self.ascenddescend_switch.toggled.connect(lambda LRdict: self.sort(sortorder=('ascending' if LRdict[1] else 'descending')))
        # sort_layout.addWidget(self.ascenddescend_switch)
        sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

    def sort(self, sorttext=None, sortorder=None):
        self.corpus_sortproxy.updatesorttype(sorttext, sortorder)

    def handle_selection(self, index):
        # gloss = self.corpus_model.glosses[index.row()]
        # themodel = index.model()
        # if hasattr(themodel, 'mapToSource'):
        #     print("selected index is from a proxy model!")
        #     underlyingindex = themodel.mapToSource(index)
        #     underlyingsign = self.corpus_model.signs[underlyingindex.row()]
        #     print("row: ", underlyingindex.row(), " / sign gloss: ", underlyingsign.signlevel_information.gloss)
        # else:
        #     print("selected index is no from from a uproxy model!")

        index = index.model().mapToSource(index)
        sign = self.corpus_model.itemFromIndex(index).sign  #  signs[index.row()]  #.signlevel_information.gloss
        # print("row: ", index.row(), " / sign gloss: ", sign.signlevel_information.gloss)
        # self.selected_gloss.emit(gloss)
        self.selected_sign.emit(sign)

    def updated_signs(self, signs, current_sign=None):
        self.corpus_model.setsigns(signs)
        self.corpus_model.layoutChanged.emit()
        
        # Reset the selection mode
        try:
            index = 0 if current_sign is None else list(signs).index(current_sign)
            # Ref: https://www.qtcentre.org/threads/32007-SetSelection-QListView-Pyqt
            # # sourcemodelindex = self.corpus_view.model().index(index, 0)
            # # proxymodelindex = self.corpus_view.model().mapFromSource(sourcemodelindex)
            # # self.corpus_view.selectionModel().setCurrentIndex(proxymodelindex, QItemSelectionModel.SelectCurrent)
            self.corpus_view.selectionModel().setCurrentIndex(self.corpus_view.model().index(index, 0), 
                                                              QItemSelectionModel.SelectCurrent)

        except ValueError:
            self.clear()
             
    def remove_sign(self, sign):
        self.corpus_model.signs.remove(sign)
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()

    def clear(self):
        self.corpus_title.setText("")

        self.corpus_model.clear()
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()

    def filter_corpus_list(self):
        self.corpus_sortproxy.setFilterRegExp(self.sender().text())
        self.corpus_view.clearSelection() # Deselects all signs in the corpus list 