import os
from collections import defaultdict

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QPushButton,
    QLabel,
    QFormLayout,
    QFrame,
    QDialogButtonBox,
    QFileDialog,
    QSpinBox,
    QMessageBox
)

from PyQt5.QtCore import pyqtSignal

from constant import filenamefrompath
from lexicon.lexicon_classes import Corpus
from gui.modulespecification_widgets import StatusDisplay


class MergeCorporaDialog(QDialog):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.corpusfilepaths = []
        self.corpuspaths_order = []
        self.mergedfilepath = ""

        self.results_lists = {
            "incorrect format": [],
            "failed to load": [],
            "failed to count": [],
            "successful results": [],
            "duplicated glosses": [],
            "duplicated lemmas": [],
            "duplicated ID-glosses": []
        }

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.choosefileslabel = QLabel("1. Choose the .slpaa corpus files to merge.")
        self.choosefilesbutton = QPushButton("Select corpus files")
        self.choosefilesbutton.clicked.connect(self.handle_select_corpusfiles)
        form_layout.addRow(self.choosefileslabel, self.choosefilesbutton)
        self.chooseorderlabel = QLabel("2. Choose the order in which the corpora should be combined (this affects EntryID numbering).")
        self.chooseorderbutton = QPushButton("Select order")
        self.chooseorderbutton.clicked.connect(self.handle_choose_order)
        form_layout.addRow(self.chooseorderlabel, self.chooseorderbutton)
        self.choosemergedfilelabel = QLabel("3. Choose the name and location for the merged file.")
        self.choosemergedfilebutton = QPushButton("Select merged file")
        self.choosemergedfilebutton.clicked.connect(self.handle_select_mergedfile)
        form_layout.addRow(self.choosemergedfilelabel, self.choosemergedfilebutton)
        self.mergecorporalabel = QLabel("4. Merge selected .slpaa files.")
        self.mergecorporabutton = QPushButton("Merge corpora")
        self.mergecorporabutton.clicked.connect(self.handle_merge_corpora)
        form_layout.addRow(self.mergecorporalabel, self.mergecorporabutton)
        self.statuslabel = QLabel("5. Status of merge:")
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

    def handle_select_corpusfiles(self):
        file_names, file_type = QFileDialog.getOpenFileNames(self,
                                                            self.tr('Select Corpora'),
                                                            self.app_settings['storage']['recent_folder'],
                                                            self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_names != self.corpusfilepaths:
            numfiles = len(file_names)
            self.statusdisplay.setText(str(numfiles) + " file" + ("" if numfiles == 1 else "s") + " selected")
        self.corpusfilepaths = file_names

    def handle_choose_order(self):
        existingorder = []
        if self.corpuspaths_order:
            # an order has been set at some point
            if sorted(self.corpuspaths_order) == sorted(self.corpusfilepaths):
                # the corpora in the ordered list correspond to the currently-selected corpora;
                # show this ordering in the spinboxes
                existingorder = self.corpuspaths_order

        chooseorderdialog = ChooseOrderDialog(self.corpusfilepaths, existingorder, parent=self)
        chooseorderdialog.setcorpusorder.connect(self.handle_setcorpusorder)
        chooseorderdialog.exec_()

    def handle_setcorpusorder(self, corpuspathslist):
        self.corpuspaths_order = corpuspathslist
        self.statusdisplay.setText("order selected")

    def handle_select_mergedfile(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select merged destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_name != self.mergedfilepath:
            self.statusdisplay.setText("destination selected")
        self.mergedfilepath = file_name

    def handle_merge_corpora(self):

        self.statusdisplay.setText("merging...")
        self.clear_results_lists()

        self.load_and_merge_corpora()

        statusstrings = []
        for listname in self.results_lists.keys():
            if len(self.results_lists[listname]) > 0:
                filenames = [filenamefrompath(fp) for fp in self.results_lists[listname]]
                statusstrings.append(listname + ":\n\t" + ",\n\t".join(filenames))
        self.statusdisplay.setText("\n".join(statusstrings))

    def clear_results_lists(self):
        for k in self.results_lists.keys():
            self.results_lists[k] = []

    def load_and_merge_corpora(self):
        mergedcorpus = Corpus()

        glosses_seen = defaultdict(list)
        lemmas_seen = defaultdict(list)
        # idglosses_seen = defaultdict(list)

        for corpusfilepath in self.corpuspaths_order if self.corpuspaths_order else self.corpusfilepaths:
            self.statusdisplay.appendText("\t" + filenamefrompath(corpusfilepath), afternewline=True)

            if not corpusfilepath.endswith(".slpaa"):
                self.results_lists["incorrect format"].append(corpusfilepath)
            else:
                corpustoadd = self.parent().load_corpus_binary(corpusfilepath)
                if corpustoadd is None:
                    self.results_lists["failed to load"].append(corpusfilepath)
                else:
                    corpustoadd.increaseminID(mergedcorpus.highestID + 1)
                    for sign in corpustoadd.signs:
                        mergedcorpus.add_sign(sign)
                        sli = sign.signlevel_information
                        gloss = sli.gloss.lower().strip()
                        if gloss != "":
                            glosses_seen[gloss].append(corpusfilepath)
                        # for gloss in [g.lower().strip() for g in sli.gloss if g != ""]:
                        #     glosses_seen[gloss].append(corpusfilepath)
                        lemma = sli.lemma.lower().strip()
                        if lemma != "":
                            lemmas_seen[lemma].append(corpusfilepath)
                        # idgloss = sli.idgloss.lower().strip()
                        # if idgloss != "":
                        #     idglosses_seen[idgloss].append(corpusfilepath)

                    mergedcorpus.highestID = corpustoadd.highestID
                    self.results_lists["successful results"].append(corpusfilepath)

                    # self.results_lists["failed to load"].append(corpusfilepath + " (" + result + ")")

        for (gloss, corpuslist) in glosses_seen.items():
            if len(corpuslist) > 1:
                self.results_lists["duplicated glosses"].append(gloss)
        for (lemma, corpuslist) in lemmas_seen.items():
            if len(corpuslist) > 1:
                self.results_lists["duplicated lemmas"].append(lemma)
        # for (idgloss, corpuslist) in idglosses_seen.items():
        #     if len(corpuslist) > 1:
        #         self.results_lists["duplicated ID-glosses"].append(idgloss)



        self.parent().save_corpus_binary(othercorpusandpath=(mergedcorpus, self.mergedfilepath))

    def handle_buttonbox_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Close:
            # close dialog
            self.accept()


class ChooseOrderDialog(QDialog):
    setcorpusorder = pyqtSignal(list)

    def __init__(self, corpusfilepaths, ordered, **kwargs):
        super().__init__(**kwargs)
        self.corpusfilepaths = corpusfilepaths

        main_layout = QVBoxLayout()

        instructionstring = "Choose the order in which the corpora should be combined, or leave them all the same if it doesn't matter."
        instructionstring += "\n\nThis affects which corpora will have their sequential Entry ID numbering incremented."
        instructionstring += "\n\nFor example, suppose CorpusA.slpaa and CorpusB.slpaa both have three signs, with counters 1, 2, and 3."
        instructionstring += "\nThen if A is added first and B is added next, the signs in A will still have their counter values 1, 2, 3"
        instructionstring += "\nbut the signs in B will have theirs adjusted to 4, 5, and 6."
        main_layout.addWidget(QLabel(instructionstring))

        chooseorder_layout = QFormLayout()
        self.spinboxes_dict = {}
        numcorpora = len(self.corpusfilepaths)
        for corpuspath in self.corpusfilepaths:
            spinlayout = QHBoxLayout()
            orderspin = QSpinBox(parent=self)
            orderspin.setMinimum(1)
            orderspin.setMaximum(numcorpora)
            if ordered:
                orderspin.setValue(ordered.index(corpuspath) + 1)
            spinlayout.addWidget(orderspin)
            spinlayout.addStretch()
            self.spinboxes_dict[corpuspath] = orderspin
            folders, filename = os.path.split(corpuspath)
            higherfolders, lastfolder = os.path.split(folders)
            chooseorder_layout.addRow(QLabel(os.path.join("...", lastfolder, filename)), spinlayout)
        main_layout.addLayout(chooseorder_layout)

        buttons = QDialogButtonBox.Cancel | QDialogButtonBox.Save
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.on_button_click)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def check_ordering(self):
        if not self.spinboxes_dict:
            return 0

        order_numbers = []
        for box in self.spinboxes_dict.values():
            order_numbers.append(box.value())
        allunique = len(set(order_numbers)) == len(order_numbers)
        allsame = len([num for num in order_numbers if num != order_numbers[0]]) == 0
        return 0 if allsame else (1 if allunique else 2)

    def on_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Save:
            orderingtype = self.check_ordering()
            if orderingtype == 0:
                # all values are the same; don't set a particular order
                self.setcorpusorder.emit([])
                self.accept()
            elif orderingtype == 1:
                # user set a unique ordering
                orders_corpuspaths = []
                for corpuspath, spinbox in self.spinboxes_dict.items():
                    orders_corpuspaths.append((spinbox.value(), corpuspath))
                orders_corpuspaths.sort()
                self.setcorpusorder.emit([corpuspath for (order, corpuspath) in orders_corpuspaths])
                self.accept()
            else:
                # user duplicates at least one of the ordering values
                QMessageBox.critical(self, "Warning", "Ordering values must either all be unique, or all be zero")

        elif standard == QDialogButtonBox.Cancel:
            self.reject()
