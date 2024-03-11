from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QTableView,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QAbstractItemView,
    QRadioButton,
    QButtonGroup
)

from models.corpus_models import CorpusModel, CorpusSortProxyModel
from lexicon.lexicon_classes import Sign


class CorpusTitleEdit(QLineEdit):
    focus_out = pyqtSignal(str)

    def __init__(self, corpus_title, **kwargs):
        super().__init__(corpus_title, **kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def focusOutEvent(self, event):
        # use focusOutEvent as the proxy for finishing editing
        self.focus_out.emit(self.text())
        super().focusInEvent(event)


class CorpusDisplay(QWidget):
    selected_sign = pyqtSignal(Sign)
    selection_cleared = pyqtSignal()
    title_changed = pyqtSignal(str)

    def __init__(self, corpus_title="", **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.corpus_title = CorpusTitleEdit(corpus_title, parent=self)
        self.corpus_title.focus_out.connect(lambda title: self.title_changed.emit(title))
        self.corpus_title.setPlaceholderText('Untitled')
        main_layout.addWidget(self.corpus_title)

        self.corpus_model = CorpusModel(settings=self.mainwindow.app_settings, parent=self)
        self.corpus_view = QTableView(parent=self)
        self.corpus_view.verticalHeader().hide()
        self.corpus_sortproxy = CorpusSortProxyModel(parent=self)
        self.corpus_sortproxy.setSourceModel(self.corpus_model)
        self.corpus_model.modelupdated.connect(lambda: self.corpus_sortproxy.sortnow())
        self.corpus_view.setModel(self.corpus_sortproxy)
        self.corpus_view.clicked.connect(self.handle_selection)
        self.corpus_view.setEditTriggers(QAbstractItemView.NoEditTriggers)  # disable edit by double-clicking an item
        self.corpus_view.setSelectionBehavior(QAbstractItemView.SelectRows)

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
            ["entry ID", "alpha by gloss (default)", "alpha by lemma", "alpha by ID-gloss", "date created", "date last modified"])
        self.sortcombo.setCurrentIndex(1)
        self.sortcombo.setInsertPolicy(QComboBox.NoInsert)
        self.sortcombo.currentTextChanged.connect(lambda txt: self.corpus_sortproxy.updatesort(sortbytext=txt))
        sort_layout.addWidget(self.sortcombo)
        self.ascend_radio = QRadioButton("A→Z; 1→9")
        self.descend_radio = QRadioButton("Z→A; 9→1")
        self.ascdesc_grp = QButtonGroup()
        self.ascdesc_grp.addButton(self.ascend_radio)
        self.ascdesc_grp.addButton(self.descend_radio)
        self.ascend_radio.setChecked(True)
        self.ascdesc_grp.buttonToggled.connect(
            lambda: self.corpus_sortproxy.updatesort(ascending=self.ascend_radio.isChecked()))
        sort_layout.addWidget(self.ascend_radio)
        sort_layout.addWidget(self.descend_radio)
        sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

############## handle_selection from main branch
    # def handle_selection(self, index):
    #     themodel = index.model()
    #     if themodel is not None:
    #         index = themodel.mapToSource(index)
    #         sign = self.corpus_model.itemFromIndex(index).sign
    #         self.selected_sign.emit(sign)

############## handle_selection from 105 branch
    def handle_selection(self, proxyindex=None):
        if proxyindex is not None and proxyindex.model() is not None:
            sourceindex = self.corpus_sortproxy.mapToSource(proxyindex)
            sign = self.corpus_model.itemFromIndex(sourceindex).sign
            self.selected_sign.emit(sign)
        else:
            self.selection_cleared.emit()

############## updated_signs from main branch
    # def updated_signs(self, signs, current_sign=None):
    #     self.corpus_model.setsigns(signs)
    #     self.corpus_model.layoutChanged.emit()
    #
    #     # Reset the selection mode
    #     try:
    #         index = 0 if current_sign is None else list(signs).index(current_sign)
    #         # Ref: https://www.qtcentre.org/threads/32007-SetSelection-QListView-Pyqt
    #         # # sourcemodelindex = self.corpus_view.model().index(index, 0)
    #         # # proxymodelindex = self.corpus_view.model().mapFromSource(sourcemodelindex)
    #         # # self.corpus_view.selectionModel().setCurrentIndex(proxymodelindex, QItemSelectionModel.SelectCurrent)
    #         self.corpus_view.selectionModel().setCurrentIndex(self.corpus_view.model().index(index, 0),
    #                                                           QItemSelectionModel.SelectCurrent)
    #
    #     except ValueError:
    #         self.clear()

############## updated_signs from 105 branch
    # if deleted==True, then current_sign is the sign that was deleted and we should select the *next* one
    # but if deleted==False, then current_sign is the one that should be selected (because it was either just added or just updated)
    def updated_signs(self, signs, current_sign=None, deleted=False):
        selected_proxyindex = None
        rowtoselect = -1

        if deleted:
            curproxymodelindex = self.corpus_view.selectionModel().selectedRows()[-1]
            curselectedrownum = curproxymodelindex.row()

            deletedsignsrownums = self.corpus_sortproxy.getrownumsmatchingsign(current_sign)
            decreaseselectedrowby = len([rn for rn in deletedsignsrownums if rn <= curselectedrownum])
            rowtoselect = curselectedrownum - decreaseselectedrowby + 1

        self.corpus_model.setsigns(signs)

        # (re)set the selection
        try:
            if deleted:
                if rowtoselect not in range(self.getrowcount()):
                    rowtoselect = self.getrowcount() - 1
                selected_proxyindex = self.getproxyindex(fromproxyrowcol=(rowtoselect, 0))
            else:
                if current_sign is not None:
                    # this whole chunk is meant to identify the row of the proxy model that should be selected
                    # (ie, the one containing the indicated sign)
                    # there must be a less convoluted way to do this, but I'm not sure what it might be...?
                    proxymodelrow = 0
                    while rowtoselect == -1 and proxymodelrow in range(self.getrowcount()):
                        selected_proxyindex = self.getproxyindex(fromproxyrowcol=(proxymodelrow, 0))
                        sourcemodelindex = self.getsourceindex(fromproxyindex=selected_proxyindex)
                        corpusitem = self.getcorpusitem(fromsourceindex=sourcemodelindex)
                        sign = corpusitem.sign
                        if sign == current_sign:
                            rowtoselect = proxymodelrow
                        proxymodelrow += 1

            self.corpus_view.selectRow(rowtoselect)  # row -1 (ie, no selection) if current_sign is None
            self.handle_selection(selected_proxyindex)
        except ValueError:
            self.clear()

    def getproxyindex(self, fromproxyrowcol=None, fromsourceindex=None):
        if fromproxyrowcol:
            return self.corpus_view.model().index(fromproxyrowcol[0], fromproxyrowcol[1])
        elif fromsourceindex:
            return self.corpus_view.model().mapFromSource(fromsourceindex)
        return None

    def getsourceindex(self, fromproxyrowcol=None, fromproxyindex=None):
        if fromproxyrowcol:
            return self.corpus_view.model().mapToSource(self.getproxyindex(fromproxyrowcol=fromproxyrowcol))
        elif fromproxyindex:
            return self.corpus_view.model().mapToSource(fromproxyindex)
        return None

    def getcorpusitem(self, fromsourceindex):
        return self.corpus_view.model().sourceModel().itemFromIndex(fromsourceindex)

    def getrowcount(self):
        return self.corpus_view.model().rowCount()

    def clear(self):
        self.corpus_title.setText("")

        self.corpus_model.clear()
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()

    def filter_corpus_list(self):
        self.corpus_sortproxy.setFilterRegExp(self.sender().text())
        self.corpus_view.clearSelection()  # Deselects all signs in the corpus list
