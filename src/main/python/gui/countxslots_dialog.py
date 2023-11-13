import io

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


class CountXslotsDialog(QDialog):

    def __init__(self, app_settings, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.filenames = []
        self.outputformat = "csv"

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.choosefileslabel = QLabel("1. Choose the .slpaa corpus file(s) whose signs to analyze.")
        self.choosefilesbutton = QPushButton("Select file(s)")
        self.choosefilesbutton.clicked.connect(self.handle_select_files)
        form_layout.addRow(self.choosefileslabel, self.choosefilesbutton)
        self.selectformatlabel = QLabel("2. Choose whether you'd like the results in comma-separated (.csv) or tab-delimited (.txt) format.")
        self.selectformatcombo = QComboBox()
        self.selectformatcombo.addItems(["Comma (.csv)", "Tab (.txt)"])
        self.selectformatcombo.currentTextChanged.connect(self.combotext_changed)
        form_layout.addRow(self.selectformatlabel, self.selectformatcombo)
        self.countxslotslabel = QLabel("3. Count x-slots for each sign in selected file(s).\nResults for each corpus will be saved in the same location as the original .slpaa file.")
        self.countxslotsbutton = QPushButton("Count x-slots")
        self.countxslotsbutton.clicked.connect(self.handle_count_xslots)
        form_layout.addRow(self.countxslotslabel, self.countxslotsbutton)
        self.statuslabel = QLabel("4. Status of x-slot counter:")
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

    def combotext_changed(self, txt):
        if "comma" in txt:
            newoutputformat = "csv"
        else:  # "tab"
            newoutputformat = "txt"

        if newoutputformat != self.outputformat:
            self.statusdisplay.setText(newoutputformat + " format selected")
        self.outputformat = newoutputformat

    def handle_select_files(self):
        file_names, file_type = QFileDialog.getOpenFileNames(self,
                                                            self.tr('Select Corpus'),
                                                            self.app_settings['storage']['recent_folder'],
                                                            self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_names != self.filenames:
            numfiles = len(file_names)
            self.statusdisplay.setText(str(numfiles) + " file" + ("" if numfiles == 1 else "s") + " selected")
        self.filenames = file_names

    def handle_count_xslots(self):

        self.statusdisplay.setText("counting...")
        self.count_all_xslots()

    def count_all_xslots(self):

        badformatlist = []
        failedtoloadlist = []
        successlist = []
        failurelist = []
        for corpusfilepath in self.filenames:
            if not corpusfilepath.endswith(".slpaa"):
                badformatlist.append(corpusfilepath)
            else:
                corpus = self.parent().load_corpus_binary(corpusfilepath)
                if corpus is None:
                    failedtoloadlist.append(corpusfilepath)
                else:
                    resultsfilepath = corpusfilepath.replace(".slpaa", "_xslotcounts." + self.outputformat)
                    result = self.count_record_corpus_xslots(corpus, resultsfilepath)
                    if result == "success":
                        successlist.append(resultsfilepath)
                    else:
                        failurelist.append(corpusfilepath + " (permission error)")

        statusstrings = []
        if len(badformatlist) > 0:
            badformatnames = [self.getfilenamefrompath(fp) for fp in badformatlist]
            statusstrings.append("incorrect format: " + ",\n\t".join(badformatnames))
        if len(failedtoloadlist) > 0:
            failedtoloadnames = [self.getfilenamefrompath(fp) for fp in failedtoloadlist]
            statusstrings.append("failed to load: " + ",\n\t".join(failedtoloadnames))
        if len(failurelist) > 0:
            failurenames = [self.getfilenamefrompath(fp) for fp in failurelist]
            statusstrings.append("failed to count: " + ",\n\t".join(failurenames))
        if len(successlist) > 0:
            successnames = [self.getfilenamefrompath(fp) for fp in successlist]
            statusstrings.append("successful results: " + ",\n\t".join(successnames))

        self.statusdisplay.setText("\n".join(statusstrings))

    def getfilenamefrompath(self, filepath):
        afterlastslash = filepath.rfind("/") + 1
        return filepath[afterlastslash:]

    def count_record_corpus_xslots(self, corpus, resultsfilepath):
        d = "," if self.outputformat == "csv" else "\t"
        try:
            with io.open(resultsfilepath, "w") as rfile:
                rfile.write(d.join(["gloss", "whole_xslots", "partial_xslots", "fingerspelled"]) + "\n")
                for sign in corpus.signs:
                    gloss = sign.signlevel_information.gloss
                    whole_xslots = sign.xslotstructure.number
                    frac_xslots = sign.xslotstructure.additionalfraction
                    fingerspelled = sign.signlevel_information.fingerspelled
                    rfile.write(d.join([gloss, str(whole_xslots), str(frac_xslots), str(fingerspelled)]) + "\n")
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


class StatusDisplay(QLabel):
    def __init__(self, initialtext="", **kwargs):
        super().__init__(**kwargs)
        self.setText(initialtext)
        self.setStyleSheet("border: 1px solid black;")

