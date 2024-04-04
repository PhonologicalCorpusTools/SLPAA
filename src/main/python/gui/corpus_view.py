from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QModelIndex
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


class CorpusDisplay(QWidget):
    selected_sign = pyqtSignal(Sign)
    selection_cleared = pyqtSignal()

    def __init__(self, corpusfilename="", **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        filename_layout = QHBoxLayout()
        corpusfile_label = QLabel("Corpus file:")
        self.corpusfile_edit = QLineEdit(corpusfilename or "not yet saved")
        self.corpusfile_edit.setEnabled(False)
        filename_layout.addWidget(corpusfile_label)
        filename_layout.addWidget(self.corpusfile_edit)
        main_layout.addLayout(filename_layout)

        self.corpus_model = CorpusModel(settings=self.mainwindow.app_settings, parent=self)
        self.corpus_view = CorpusTableView(parent=self)
        self.corpus_view.verticalHeader().hide()

        self.corpus_sortproxy = CorpusSortProxyModel(parent=self)
        self.corpus_sortproxy.setSourceModel(self.corpus_model)
        self.corpus_model.modelupdated.connect(lambda: self.corpus_sortproxy.sortnow())
        self.corpus_view.setModel(self.corpus_sortproxy)
        self.corpus_view.newcurrentindex.connect(self.handle_selection)
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

    def handle_selection(self, proxyindex=None):
        if proxyindex is not None and proxyindex.model() is not None:
            sourceindex = self.corpus_sortproxy.mapToSource(proxyindex)
            sign = self.corpus_model.itemFromIndex(sourceindex).sign
            self.selected_sign.emit(sign)
        else:
            self.selection_cleared.emit()

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
            if selected_proxyindex:
                # don't ask... there must be a delay or a sync-timing thing that I can't figure out,
                # but for now all I can say is that calling it twice works but calling it once doesn't. sigh.
                # possibly relevant: https://forum.qt.io/topic/81671/scrollto-not-working-properly
                self.corpus_view.scrollTo(selected_proxyindex, QTableView.EnsureVisible)
                self.corpus_view.scrollTo(selected_proxyindex, QTableView.EnsureVisible)
            else:
                self.corpus_view.scrollToTop()
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

    def selectfirstrow(self):
        if self.getrowcount() > 0:
            self.corpus_view.selectRow(0)

    def getrowcount(self):
        return self.corpus_view.model().rowCount()

    def clear(self):
        self.corpusfile_edit.setText("not yet saved")

        self.corpus_model.clear()
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()

    def filter_corpus_list(self):
        self.corpus_sortproxy.setFilterRegExp(self.sender().text())
        self.corpus_view.clearSelection()  # Deselects all signs in the corpus list


class CorpusTableView(QTableView):
    newcurrentindex = pyqtSignal(QModelIndex)

    # same signal no matter how the user selects a new row
    # (whether by clicking, using up/down arrows, or typing a character on the keyboard)
    def currentChanged(self, current, previous):
        self.newcurrentindex.emit(current)
