import io
import os

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QPushButton,
    QLabel,
    QComboBox,
    QFormLayout,
    QFrame,
    QDialogButtonBox,
    QFileDialog
)

from constant import filenamefrompath
from gui.modulespecification_widgets import StatusDisplay


class CountXslotsDialog(QDialog):
    headers = ["source_file", "entryid", "gloss_es", "whole_xslots", "partial_xslots", "fingerspelled"]

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.corpusfilepaths = []
        self.combinedresultsfilepath = ""
        self.outputformat = "csv"
        self.combined = False

        self.results_lists = {
            "incorrect format": [],
            "failed to load": [],
            "failed to count": [],
            "successful results": []
        }

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.choosefileslabel = QLabel("1. Choose the .slpaa corpus file(s) whose signs to analyze.")
        self.choosefilesbutton = QPushButton("Select corpus file(s)")
        self.choosefilesbutton.clicked.connect(self.handle_select_corpusfiles)
        form_layout.addRow(self.choosefileslabel, self.choosefilesbutton)
        self.selectformatlabel = QLabel("2. Choose whether you'd like the results in comma-separated (.csv) or tab-delimited (.txt) format.")
        self.selectformatcombo = QComboBox()
        self.selectformatcombo.addItems(["Comma (.csv)", "Tab (.txt)"])
        self.selectformatcombo.currentTextChanged.connect(self.formatcombo_changed)
        form_layout.addRow(self.selectformatlabel, self.selectformatcombo)
        self.selectcombinedlabel = QLabel("3a. Choose whether you'd like each .slpaa file to have its own separate results file, or combine them all in one.")
        self.selectcombinedcombo = QComboBox()
        self.selectcombinedcombo.addItems(["Separate", "Combined"])
        self.selectcombinedcombo.currentTextChanged.connect(self.combinedcombo_changed)
        form_layout.addRow(self.selectcombinedlabel, self.selectcombinedcombo)
        self.choosecombinedfilelabel = QLabel("3b. If combined, choose the name and location for the results file.")
        self.choosecombinedfilebutton = QPushButton("Select results file")
        self.choosecombinedfilebutton.clicked.connect(self.handle_select_resultsfile)
        form_layout.addRow(self.choosecombinedfilelabel, self.choosecombinedfilebutton)
        self.countxslotslabel = QLabel("4. Count x-slots for each sign in selected file(s).\nIf reporting separately, results for each corpus will be saved in the same location as the original .slpaa file.")
        self.countxslotsbutton = QPushButton("Count x-slots")
        self.countxslotsbutton.clicked.connect(self.handle_count_xslots)
        form_layout.addRow(self.countxslotslabel, self.countxslotsbutton)
        self.statuslabel = QLabel("5. Status of x-slot counter:")
        self.statusdisplay = StatusDisplay("not yet attempted")
        form_layout.addRow(self.statuslabel, self.statusdisplay)

        main_layout.addLayout(form_layout)

        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.HLine)
        horizontal_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(horizontal_line)

        buttons = QDialogButtonBox.Close
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.handle_buttonbox_click)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def delim(self):
        if self.outputformat == "csv":
            return ","
        else:
            return "\t"

    def formatcombo_changed(self, txt):
        if "comma" in txt.lower():
            newoutputformat = "csv"
        else:  # "tab"
            newoutputformat = "txt"

        if newoutputformat != self.outputformat:
            self.statusdisplay.setText(newoutputformat + " format selected")
        self.outputformat = newoutputformat

    def combinedcombo_changed(self, txt):
        if "combined" in txt.lower():
            newcombined = True
        else:  # "separate"
            newcombined = False

        if newcombined != self.combined:
            self.statusdisplay.setText(txt + " selected")
        self.combined = newcombined

    def handle_select_corpusfiles(self):
        file_names, file_type = QFileDialog.getOpenFileNames(self,
                                                            self.tr('Select Corpus'),
                                                            self.app_settings['storage']['recent_folder'],
                                                            self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_names != self.corpusfilepaths:
            numfiles = len(file_names)
            self.statusdisplay.setText(str(numfiles) + " file" + ("" if numfiles == 1 else "s") + " selected")
        self.corpusfilepaths = file_names

    def handle_select_resultsfile(self):
        description = "Comma-separated" if self.outputformat == "csv" else "Tab-separated"
        extension = self.outputformat
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select results destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr(description + "(*." + extension + ")"))
        if file_name != self.combinedresultsfilepath:
            self.statusdisplay.setText("destination selected")
        self.combinedresultsfilepath = file_name

    def handle_count_xslots(self):

        self.statusdisplay.setText("counting...")
        self.clear_results_lists()

        self.count_xslots()

        statusstrings = []
        for listname in self.results_lists.keys():
            if len(self.results_lists[listname]) > 0:
                filenames = [filenamefrompath(fp) for fp in self.results_lists[listname]]
                statusstrings.append(listname + ":\n\t" + ",\n\t".join(filenames))
        self.statusdisplay.setText("\n".join(statusstrings))

    def clear_results_lists(self):
        for k in self.results_lists.keys():
            self.results_lists[k] = []

    def count_xslots(self):
        if self.combined:
            resultsfilepath = self.combinedresultsfilepath
            try:
                with io.open(resultsfilepath, "w") as outfile:
                    outfile.write(self.delim().join(self.headers) + "\n")
            except PermissionError:
                return "permission error"
            except:
                return "unspecified error"
            w_or_a = "a"
        else:
            w_or_a = "w"

        for corpusfilepath in self.corpusfilepaths:
            self.statusdisplay.appendText("\t" + filenamefrompath(corpusfilepath), joinwithnewline=True)
            if not corpusfilepath.endswith(".slpaa"):
                self.results_lists["incorrect format"].append(corpusfilepath)
            else:
                corpus = self.parent().load_corpus_binary(corpusfilepath)
                if corpus is None:
                    self.results_lists["failed to load"].append(corpusfilepath)
                else:
                    if not self.combined:
                        resultsfilepath = corpusfilepath.replace(".slpaa", "_xslotcounts." + self.outputformat)
                    result = self.count_record_corpus_xslots(corpus, filenamefrompath(corpusfilepath), resultsfilepath, w_or_a)
                    if result == "success":
                        self.results_lists["successful results"].append(corpusfilepath)
                    else:
                        self.results_lists["failed to load"].append(corpusfilepath + " (" + result + ")")

    def count_record_corpus_xslots(self, corpus, corpusfilename, resultsfilepath, write_or_append):
        try:
            with io.open(resultsfilepath, write_or_append) as outfile:
                if not self.combined:
                    outfile.write(self.delim().join(self.headers) + "\n")
                for sign in corpus.signs:
                    entryidstring = sign.signlevel_information.entryid.display_string()
                    glosses = "/".join(sign.signlevel_information.gloss)
                    whole_xslots = sign.xslotstructure.number
                    frac_xslots = sign.xslotstructure.additionalfraction
                    fingerspelled = sign.signlevel_information.fingerspelled
                    outfile.write(self.delim().join([corpusfilename, entryidstring, glosses, str(whole_xslots), str(frac_xslots), str(fingerspelled)]) + "\n")
            return "success"
        except PermissionError:
            return "permission error"
        except:
            return "unspecified error"

    def handle_buttonbox_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Close:
            # close dialog
            self.accept()
