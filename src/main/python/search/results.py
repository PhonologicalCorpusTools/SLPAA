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
import logging, os, json, csv, sys
import xml.etree.ElementTree as ET


class ResultHeaders:
    CORPUS = 0
    NAME = 1
    VALUES = 2
    TYPE = 3
    ID = 4
    FREQUENCY = 4
    GLOSS = 5
    LEMMA = 6
    IDGLOSS = 7

class ResultsView(QWidget):
    def __init__(self, resultsdict, mainwindow, **kwargs):
        super().__init__(**kwargs)
        self.setWindowTitle("Search Results")
        self.resultsdict = resultsdict
        self.mainwindow = mainwindow
        self.appctxt = mainwindow.app_ctx
        self.corpus = self.mainwindow.corpus
        self.individualresultspath = None
        self.summaryresultspath = None

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
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        # actions

        # export
        action_export = QAction(QIcon(self.mainwindow.app_ctx.icons['saveas']), 'Export current results', parent=self)
        action_export.triggered.connect(lambda checked: self.on_action_export(checked, label))
        export_shortcut = QKeySequence(Qt.CTRL+Qt.SHIFT+Qt.Key_S)
        action_export.setShortcut(export_shortcut)
        action_export.setToolTip(QKeySequence.listToString(export_shortcut, QKeySequence.NativeText))
        action_export.setCheckable(False)
        toolbar.addAction(action_export)
        return toolbar
    
    def save_results_to_file(self, file_name, tab_label, selected_filter):
        # print(f"saving as {file_name}")
        # print(f"selected filter {selected_filter}")
        directory = os.path.join(file_name)
        if tab_label == "individual":
            model = self.individualmodel
            self.individualresultspath = directory
        elif tab_label == "summary":
            model = self.summarymodel
            self.summaryresultspath = directory
        if ".json" in selected_filter:
            formatted = model.format_results()
            with open(directory, 'w') as f:
                json.dump(formatted, f)
        elif ".xml" in selected_filter:
            xml = model.format_results_as_xml()
            xml.write(directory, encoding="utf-8")
        else:
            with open(directory, 'w', newline='') as tsvfile:
                writer = csv.writer(tsvfile, delimiter='\t', lineterminator='\n')
                writer.writerow(model.headers)
                for row in range(model.rowCount()):
                    writer.writerow([model.entry(row, col) for col in range(model.columnCount())])

        folder, _ = os.path.split(file_name)
        if folder:
            self.mainwindow.app_settings['storage']['recent_results'] = folder


    def on_action_export(self, clicked, tab_label): # tab_label is "summary" or "individual"
        searchfile_name = self.mainwindow.searchmodel.name if self.mainwindow.searchmodel.name else "SLPAA"
        name = f"{searchfile_name}_{tab_label}_results"
        results_dir = self.mainwindow.app_settings['storage']['recent_results'] 
        dialog = QFileDialog(self)
        dialog.setAcceptMode(QFileDialog.AcceptSave)
        dialog.setWindowTitle(self.tr(f"Save {tab_label} results"))
        dialog.setDirectory(os.path.join(results_dir))
        dialog.selectFile(f"{name}.tsv")
        dialog.setNameFilters(["JSON (*.json)", "TSV (*.tsv)", "XML (*.xml)", "text (*.txt)"])
        dialog.selectNameFilter("TSV (*.tsv)") # initial filter
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, "File format:")
        if dialog.exec_() == QFileDialog.Accepted:
            file_name = dialog.selectedFiles()[0]
            selected_filter = dialog.selectedNameFilter()
        else:
            file_name = None
            selected_filter = None
        # file_name, selected_filter = QFileDialog.getSaveFileName(
        #     self,
        #     caption=self.tr(f"Save {tab_label} results"),
        #     directory=os.path.join(results_dir, f"{name}.xml"), 
        #     filter="JSON (*.json);;TSV (*.tsv);;XML (*.xml);;text (*.txt)",
        #     initialFilter="TSV (*.tsv)"),
        if file_name:
            self.save_results_to_file(file_name, tab_label, selected_filter)

    def handle_result_doubleclicked(self, index):
        entryid = self.individualmodel.entry_id(index.row())
        previous_sign = self.appctxt.main_window.current_sign
        for s in self.corpus.signs:
            if s.signlevel_information.entryid == entryid:
                thissign = s
                idgloss = s.signlevel_information.idgloss
                entryid = s.signlevel_information.entryid
                break
        self.appctxt.main_window.current_sign  = thissign
        # self.mainwindow.current_sign = None
        signsummary_panel = SignSummaryPanel(mainwindow=self.appctxt.main_window, sign=thissign, parent=self)
        # signsummary_panel.mainwindow.current_sign = thissign  # refreshsign() checks for this
        # signsummary_panel.refreshsign(thissign)
        
        # TODO. subclass the sign summary panel. connect focus in and focus out events to switch the current sign.
        

        layout = QHBoxLayout()
        layout.addWidget(signsummary_panel)
        resultpopup = QWidget(parent=self)
        resultpopup.setLayout(layout)
        resultpopup.setWindowFlags(Qt.Window)
        resultpopup.setWindowTitle(f"Search Result: {entryid} {idgloss}")
        resultpopup.setAttribute(Qt.WA_DeleteOnClose) 
        resultpopup.destroyed.connect(lambda: self.reset_mainwindow_sign(previous_sign))
        resultpopup.show()
        
    def reset_mainwindow_sign(self, previous_sign):
        # when we doubleclick on a search result, it sets the current sign to that search result.
        # but if we then return to the mainwindow, the current sign will still be the double-clicked search result 
        # even if the active sign is different. So we reset it to the previous active sign.s
        self.appctxt.main_window.current_sign = previous_sign
        

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

    def format_results(self):
        """
        Format the results for converting to json or xml.

        Returns:
            formatted (list[dict]): Each element is a dictionary with keys:
            
            - "Targets" (list[dict]):
                Each dictionary has keys:
                - "Target Name": str
                - "Specifications": str
                - "Search Type": str
            
            - "Results" (list[dict]):
                Each dictionary has keys:
                - "Corpus": str
                - "Frequency": int
        """
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
                    "Frequency": self.entry(row, ResultHeaders.FREQUENCY)
                }
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
    
    def format_results_as_xml(self):
        formatted = self.format_results()
        root = ET.Element('ResultsSummary')
        for result_dict in formatted:
            result_elem = ET.SubElement(root, "SearchResult")
            targets_elem = ET.SubElement(result_elem, "Targets")
            results_elem = ET.SubElement(result_elem, "Results")
            for target in result_dict["Target(s)"]:
                target_elem = ET.SubElement(targets_elem, "Target")
                for target_attr, value in target.items():
                    attrib = target_attr.replace(" ", "")
                    attrib = attrib[0].lower() + attrib[1:] # convert to camelCase (originally keys had spaces and other symbols)
                    target_elem.set(attrib, value)
            for result in result_dict["Results"]:
                result_elem = ET.SubElement(results_elem, "CorpusResult")
                result_elem.set("corpus", result["Corpus"])
                result_elem.set("frequency", str(result["Frequency"]))
        return ET.ElementTree(root)
    
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
    
    def format_results(self):
        """
        Format the results for converting to json or xml.

        Returns:
            formatted (list[dict]): Each element is a dictionary with keys:
            
            - "Targets" (list[dict]):
                Each dictionary has keys:
                - "Target Name" (str)
                - "Specifications" (str)
                - "Search Type" (str)
            
            - "Results" (list[dict]):
                Each dictionary has keys:
                - "Corpus" (str)
                - "Matching Entries" (list[dict]):
                    Each matching entry has keys:
                    - "Entry ID" (str)
                    - "ID Gloss" (str)
                    - "Gloss(es)" (str)
                    - "Lemma" (str)
        """
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

    def format_results_as_xml(self):
        formatted = self.format_results()
        root = ET.Element('SearchResults')
        for result_dict in formatted:
            result_elem = ET.SubElement(root, "SearchResult")
            targets_elem = ET.SubElement(result_elem, "Targets")
            results_elem = ET.SubElement(result_elem, "Results")
            for target in result_dict["Target(s)"]:
                target_elem = ET.SubElement(targets_elem, "Target")
                for target_attr, value in target.items():
                    attrib = target_attr.replace(" ", "")
                    attrib = attrib[0].lower() + attrib[1:] # convert to camelCase (originally keys had spaces and other symbols)
                    target_elem.set(attrib, value)
            for result in result_dict["Results"]:
                result_elem = ET.SubElement(results_elem, "CorpusResult")
                result_elem.set("corpus", result["Corpus"])
                for match in result["Matching Entries"]:
                    match_elem = ET.SubElement(result_elem, "Match")
                    for v, attrib in zip(match.values(), ["entryID", "idGloss", "glosses", "lemma"]): # convert to camelCase (originally keys had spaces and other symbols)
                        match_elem.set(attrib, v)
        return ET.ElementTree(root)





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