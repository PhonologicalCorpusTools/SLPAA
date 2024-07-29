from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QMdiArea,
    QMdiSubWindow,
    QFormLayout,
    QFrame,
    QDialogButtonBox,
    QFileDialog,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QScrollArea,
    QButtonGroup,
    QLineEdit,
    QMessageBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QTableView,
    QHeaderView,
    QSizePolicy,
    QMainWindow,
    QItemDelegate,
    QStyledItemDelegate,
    QAction,
    QTabWidget
)

from PyQt5.QtCore import QModelIndex, Qt
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel, 
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QDialog
)
from gui.panel import SignLevelMenuPanel, SignSummaryPanel

import logging

class ResultHeaders:
    CORPUS = 0
    NAME = 1
    VALUES = 2
    TYPE = 3
    ID = 4
    GLOSS = 5
    LEMMA = 6
    IDGLOSS = 7

class ResultsView(QWidget):
    def __init__(self, resultsdict, mainwindow, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("Search Results")
        self.resultsdict = resultsdict
        self.mainwindow = mainwindow
        self.corpus = self.mainwindow.corpus

        # Create a tab widget
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        self.listdelegate = ListDelegate()

        self.summarytab = QWidget()
        self.summary_table_view = QTableView()
        self.summarymodel = ResultSummaryModel()
        self.summarymodel.populate(self.resultsdict)
        self.summary_table_view.setModel(self.summarymodel)
        self.summary_table_view.setItemDelegate(self.listdelegate)
        self.summary_table_view.setEditTriggers(QTableView.NoEditTriggers)
        summarylayout = QVBoxLayout()
        summarylayout.addWidget(self.summary_table_view)
        self.summarytab.setLayout(summarylayout)
        
        self.individualtab = QWidget()
        self.individual_table_view = QTableView()
        self.individualmodel = IndividualSummaryModel()
        self.individualmodel.populate(self.resultsdict)
        self.individual_table_view.setModel(self.individualmodel)
        self.individual_table_view.setItemDelegate(self.listdelegate)
        self.individual_table_view.doubleClicked.connect(self.handle_result_doubleclicked)
        self.individual_table_view.setEditTriggers(QTableView.NoEditTriggers) # disable edit via clicking table
 
        individuallayout = QVBoxLayout()
        individuallayout.addWidget(self.individual_table_view)
        self.individualtab.setLayout(individuallayout)

        self.tab_widget.addTab(self.summarytab, "Summary")
        self.tab_widget.addTab(self.individualtab, "Individual results")

        self.showMaximized()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def handle_result_doubleclicked(self, index):
        entryid = self.individualmodel.get_entry_id_from_row(index.row())
        # logging.warning(self.corpus.signs)
        # QMessageBox.critical(self, "double clicked", str(entryid))
        # for s in self.corpus.signs:
        #     thissign = s
        #     break
        # self.signsummary_panel = SignSummaryPanel(mainwindow=self.mainwindow, sign=thissign, parent=self)
        # self.signsummary_panel.refreshsign(thissign)
        # self.signsummary_panel.show()

class ListDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    def displayText(self, value, locale):
        if isinstance(value, list) or isinstance(value, tuple):
            display_text = '; '.join(value) # TODO prefer multiline...
            return display_text
        return super().displayText(value, locale)

class ResultSummaryModel(QStandardItemModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.headers = ["Corpus", "Target Name(s)", "Target Value(s)", "Result Type(s)", "Frequency"]
        self.setHorizontalHeaderLabels(self.headers)
    
    def populate(self, resultsdict):
        for targetname in resultsdict:
            resultrow = resultsdict[targetname]
            name = QStandardItem()
            name.setData(targetname, Qt.DisplayRole)
            values = QStandardItem()
            values.setData(resultrow["display"], Qt.DisplayRole)
            corpus = QStandardItem()
            corpus.setData(resultrow["corpus"], Qt.DisplayRole)
            resulttypes = QStandardItem()
            resulttypes.setData(resultrow["negative"], Qt.DisplayRole)
            frequency = QStandardItem()
            frequency.setData(len(resultrow["signs"]), Qt.DisplayRole)

            self.appendRow([corpus, name, values, resulttypes, frequency])

class IndividualSummaryModel(QStandardItemModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.headers = ["Corpus", "Target Name(s)",  "Target Value(s)", "Result Type(s)", "Entry ID", "Gloss", "Lemma", "ID Gloss"]
        self.setHorizontalHeaderLabels(self.headers)
    
    def get_entry_id_from_row(self, row):
        return self.index(row, ResultHeaders.ID).data(Qt.DisplayRole)

    def populate(self, resultsdict):
        for targetname in resultsdict:
            resultrow = resultsdict[targetname]
            for sli in resultrow["signs"]: # signlevelinformation objects
                name = QStandardItem()
                name.setData(targetname, Qt.DisplayRole)
                values = QStandardItem()
                values.setData(resultrow["display"], Qt.DisplayRole)
                corpus = QStandardItem()
                corpus.setData(resultrow["corpus"], Qt.DisplayRole)
                resulttypes = QStandardItem()
                resulttypes.setData(resultrow["negative"], Qt.DisplayRole)
                entryid = QStandardItem()
                entryid.setData(sli.entryid.display_string(), Qt.DisplayRole)
                gloss = QStandardItem()
                gloss.setData(sli.gloss, Qt.DisplayRole)
                lemma = QStandardItem()
                lemma.setData(sli.lemma, Qt.DisplayRole)
                idgloss = QStandardItem()
                idgloss.setData(sli.idgloss, Qt.DisplayRole)
                self.appendRow([corpus, name, values, resulttypes, entryid, gloss, lemma, idgloss])