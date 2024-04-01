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


class CorpusDisplay(QWidget):
    selected_sign = pyqtSignal(Sign)

    def __init__(self, corpusfilename="", **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        filename_layout = QHBoxLayout()
        corpusfile_label = QLabel("Corpus file:")
        self.corpusfile_edit = QLineEdit(corpusfilename or "not yet saved")
        self.corpusfile_edit.setEnabled(False)
        filename_layout.addWidget(corpusfile_label)
        filename_layout.addWidget(self.corpusfile_edit)
        main_layout.addLayout(filename_layout)

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
        self.sortcombo.currentTextChanged.connect(lambda txt: self.corpus_sortproxy.updatesort(sortbytext=txt))
        sort_layout.addWidget(self.sortcombo)
        self.ascend_radio = QRadioButton("A→Z; 1→9")
        self.descend_radio = QRadioButton("Z→A; 9→1")
        self.ascdesc_grp = QButtonGroup()
        self.ascdesc_grp.addButton(self.ascend_radio)
        self.ascdesc_grp.addButton(self.descend_radio)
        self.ascend_radio.setChecked(True)
        self.ascdesc_grp.buttonToggled.connect(lambda: self.corpus_sortproxy.updatesort(ascending=self.ascend_radio.isChecked()))
        sort_layout.addWidget(self.ascend_radio)
        sort_layout.addWidget(self.descend_radio)
        sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

    def handle_selection(self, index):
        themodel = index.model()
        if themodel is not None:
            index = themodel.mapToSource(index)
            sign = self.corpus_model.itemFromIndex(index).sign  
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
        self.corpusfile_edit.setText("not yet saved")

        self.corpus_model.clear()
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()

    def filter_corpus_list(self):
        self.corpus_sortproxy.setFilterRegExp(self.sender().text())
        self.corpus_view.clearSelection() # Deselects all signs in the corpus list 