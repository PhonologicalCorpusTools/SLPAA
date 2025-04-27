from PyQt5.QtWidgets import (
    QVBoxLayout, QToolBar, QFileDialog,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableView,
    QStyledItemDelegate,
    QAction,
    QTabWidget
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
from PyQt5.QtCore import QModelIndex, Qt, QSize
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel, 
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QDialog
)
from gui.panel import SignLevelMenuPanel, SignSummaryPanel
from collections import defaultdict
import logging, os, json

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
        summarylayout.addWidget(self.create_toolbar("summary"))
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
        individuallayout.addWidget(self.create_toolbar("individual"))
        individuallayout.addWidget(self.individual_table_view)
        self.individualtab.setLayout(individuallayout)

         # for both summary and individual tabs
        self.tab_widget.addTab(self.summarytab, "Summary")
        self.tab_widget.addTab(self.individualtab, "Individual results")

        self.showMaximized()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)    

    def create_toolbar(self, label):
        toolbar = QToolBar(f'{label} toolbar', parent=self)
        toolbar.setIconSize(QSize(16, 16))
        # actions
        # save
        action_save = QAction(QIcon(self.mainwindow.app_ctx.icons['save']), 'Save', parent=self)
        action_save.setStatusTip('Save')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        action_save.triggered.connect(lambda checked: self.on_action_save(checked, label))
        action_save.setCheckable(False)

        # save as
        action_saveas = QAction(QIcon(self.mainwindow.app_ctx.icons['saveas']), 'Save As...', parent=self)
        action_saveas.setStatusTip('Save As...')
        action_saveas.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_A))
        action_saveas.triggered.connect(lambda checked: self.on_action_save_as(checked, label))
        action_saveas.setCheckable(False)

        toolbar.addAction(action_save)
        toolbar.addAction(action_saveas)
        return toolbar

    def on_action_save_as(self, clicked, tab_label): # tab_label is "summary" or "individual"
        name = f"{self.mainwindow.searchmodel.name}_{tab_label}_results"
        results_dir = self.mainwindow.app_settings['storage']['recent_results'] # TODO
        file_name, selected_filter = QFileDialog.getSaveFileName(
            self,
            caption=self.tr(f"Save {tab_label} results"),
            directory=os.path.join(results_dir, f"{name}.json"), 
            filter="JSON (*.json);;TSV (*.tsv);;XML (*.xml);;text (*.txt)",
            initialFilter="JSON (*.json)")
        if file_name:
            print(f"saving as {file_name}")
            print(f"selected filter {selected_filter}")
            model = self.individualmodel if tab_label == "individual" else self.summarymodel
            if "json" in selected_filter:
                results_dict = model.create_dict()
                directory = os.path.join(file_name)
                with open(directory, 'w') as f:
                    json.dump(results_dict, f)
            elif "xml" in selected_filter:
                pass
            folder, _ = os.path.split(file_name)
            if folder:
                self.mainwindow.app_settings['storage']['recent_results'] = folder
        
    # TODO
    #  @check_unsaved_search_targets decorator
    def on_action_save(self, clicked, tab_label): # tab is "summary" or "individual"
        print(f"saving {tab_label}")

    def handle_result_doubleclicked(self, index):
        entryid = self.individualmodel.entry_id(index.row())
        for s in self.corpus.signs:
            if s.signlevel_information.entryid == entryid:
                thissign = s
                idgloss = s.signlevel_information.idgloss
                entryid = s.signlevel_information.entryid
                break

        self.mainwindow.current_sign = None
        signsummary_panel = SignSummaryPanel(mainwindow=self.mainwindow, sign=thissign, parent=self)
        signsummary_panel.mainwindow.current_sign = thissign  # refreshsign() checks for this
        signsummary_panel.refreshsign(thissign)

        layout = QHBoxLayout()
        layout.addWidget(signsummary_panel)
        resultpopup = QWidget(parent=self)
        resultpopup.setLayout(layout)
        resultpopup.setWindowFlags(Qt.Window)
        resultpopup.setWindowTitle("Search Result: " + str(entryid) +"idgloss")
        resultpopup.setAttribute(Qt.WA_DeleteOnClose) 
        resultpopup.show()
        
        

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
    
    def entry(self, row, col):
        return self.index(row, col).data(Qt.DisplayRole)

    def create_dict(self):
        pass

    
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

        self.headers = ["Corpus", "Target Name(s)",  "Target Value(s)", "Result Type(s)", "Entry ID", "Gloss(es)", "Lemma", "ID Gloss"]
        self.setHorizontalHeaderLabels(self.headers)
    
    def entry_id(self, row):
        return self.index(row, ResultHeaders.ID).data(Qt.UserRole)
    
    def entry(self, row, col):
        return self.index(row, col).data(Qt.DisplayRole)
    
    def create_dict(self):
        # first make an intermediate dict where keys are target names.
        # TODO: what format should be used when searches span multiple corpora?
        # {target_name: {corpus_name: [rows]}}
        target_dict = defaultdict(lambda: defaultdict(list))
        for row in range(self.rowCount()):
            name, corpus = self.entry(row, ResultHeaders.NAME), self.entry(row, ResultHeaders.CORPUS)
            target_dict[name][corpus].append(row)
        # now, create an xml/json-friendly structure
        formatted_results = [] 
        for name in target_dict:
            reference_row = target_dict[name][corpus][0] # just grab the first row under this target name so that we can get the target values and result types later
            results = []
            for corpus in target_dict[name]:
                this_result = {
                    self.headers[ResultHeaders.CORPUS]: corpus,
                    "Matching Entries": []
                }
                matching_rows = target_dict[name][corpus]
                for row in matching_rows:
                    this_match = {}
                    for ind in [ResultHeaders.ID, ResultHeaders.IDGLOSS, ResultHeaders.GLOSS, ResultHeaders.LEMMA]:
                        this_match[self.headers[ind]] = self.entry(row, ind)
                    this_result["Matching Entries"].append(this_match)
                results.append(this_result)

            values_arr = []
            targetnames = (name,) if isinstance(name, str) else name
            targetvalues =  self.entry(reference_row, ResultHeaders.VALUES)
            if isinstance(targetvalues, str):
                targetvalues = (targetvalues,)
            searchtypes = self.entry(reference_row, ResultHeaders.TYPE)
            if isinstance(searchtypes, str):
                searchtypes = (searchtypes,)           
            for targetname, targetvalue, searchtype in zip(targetnames, targetvalues, searchtypes):
                values_arr.append({
                    "Target Name": targetname,
                    "Specifications": targetvalue,
                    "Search Type": searchtype
                })

            formatted_results.append({
                "Target(s)": values_arr,
                "Results": results
            })
        # print(formatted_results)
        return formatted_results




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
                entryid.setData(sli.entryid, Qt.UserRole)
                entryid.setData(sli.entryid.display_string(), Qt.DisplayRole)
                gloss = QStandardItem()
                gloss.setData(sli.gloss, Qt.DisplayRole)
                lemma = QStandardItem()
                lemma.setData(sli.lemma, Qt.DisplayRole)
                idgloss = QStandardItem()
                idgloss.setData(sli.idgloss, Qt.DisplayRole)
                self.appendRow([corpus, name, values, resulttypes, entryid, gloss, lemma, idgloss])