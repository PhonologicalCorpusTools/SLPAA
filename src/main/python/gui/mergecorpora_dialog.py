import os
from collections import defaultdict

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog,
    QCheckBox,
    QLineEdit,
    QWizard,
    QWizardPage,
    QSpacerItem,
    QSizePolicy,
    QRadioButton,
    QButtonGroup
)

from PyQt5.QtCore import pyqtSignal, Qt

from constant import filenamefrompath
from lexicon.lexicon_classes import Corpus
from gui.modulespecification_widgets import StatusDisplay
from gui.helper_widget import OptionSwitch


class MergeCorporaWizard(QWizard):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.mainwindow = self.parent()
        self.corpusfilepaths = []
        self.corpuspaths_order = []
        self.mergedfilepath = ""
        self.mergeintoexisting = False
        self.makenewIDs_ifnoconflict = None
        self.makenewIDs_ifconflict = None
        self.openmergedcorpus = False

        fileselection_page = FilesSelectionWizardPage(self.app_settings)
        fileselection_page.corpusfilesselected.connect(self.handle_corpusfilesselected)
        fileselection_page.mergeintoexisting.connect(self.handle_mergeintoexisting)
        self.fileselection_pageid = self.addPage(fileselection_page)

        entryIDstrategy_page = EntryIDStrategyWizardPage()
        entryIDstrategy_page.newIDs_ifnoconflict.connect(self.handle_newIDs_ifnoconflict)
        entryIDstrategy_page.newIDs_ifconflict.connect(self.handle_newIDs_ifconflict)
        self.entryIDstrategy_pageid = self.addPage(entryIDstrategy_page)

        namelocation_page = MergedNameLocationWizardPage(self.app_settings)
        namelocation_page.mergedfileselected.connect(self.handle_mergedfileselected)
        self.namelocation_pageid = self.addPage(namelocation_page)

        self.mergecorpora_page = MergeCorporaWizardPage()
        self.mergecorpora_page.mergecorpora.connect(self.handle_merge_corpora)
        self.mergecorpora_page.openmergedcorpus.connect(self.handle_open_mergedcorpus)
        self.mergecorpora_pageid = self.addPage(self.mergecorpora_page)

        self.setWindowTitle("Merge Corpora")

        self.button(QWizard.FinishButton).clicked.connect(self.onFinish)

    def onFinish(self, checked):
        # print("finish button clicked")
        if self.openmergedcorpus:
            self.mainwindow.load_corpus_info(self.mergedfilepath)

    def nextId(self):
        if self.currentId() == self.entryIDstrategy_pageid and self.mergeintoexisting:
            # skip asking for a merged filename/path if we're not merging into the existing corpus
            return self.mergecorpora_pageid
        else:
            return super().nextId()

    def handle_newIDs_ifnoconflict(self, makenewIDs):
        self.makenewIDs_ifnoconflict = makenewIDs

    def handle_newIDs_ifconflict(self, makenewIDs):
        self.makenewIDs_ifconflict = makenewIDs

    def handle_corpusfilesselected(self, fileslist):
        self.corpusfilepaths = fileslist

    def handle_mergeintoexisting(self, mergeintoexisting):
        self.mergeintoexisting = mergeintoexisting

    def handle_mergedfileselected(self, filepath):
        self.mergedfilepath = filepath

    def handle_open_mergedcorpus(self, openmergedfile):
        # make sure that
        #   (a) the user actually wanted to open the new corpus once it's merged, and
        #   (b) there even is a new corpus, because maybe it was canceled due to EntryID conflict
        self.openmergedcorpus = openmergedfile and os.path.exists(self.mergedfilepath)

    def handle_merge_corpora(self):

        if self.mergeintoexisting:
            # ensure that the current corpus is saved
            self.mainwindow.on_action_saveas(clicked=None)

            # ensure that the current corpus filepath is in the list
            thiscorpuspath = os.path.realpath(self.mainwindow.corpus.path)
            corpuspathstomerge = [os.path.realpath(path) for path in self.corpusfilepaths]
            if thiscorpuspath not in corpuspathstomerge:
                self.corpusfilepaths.append(thiscorpuspath)

            # when merging, "save as" the current corpus filepath
            self.mergedfilepath = thiscorpuspath

        self.mergecorpora_page.statusdisplay.setText("merging...")
        self.mergecorpora_page.statusdisplay.repaint()

        results_lists = self.load_and_merge_corpora()

        self.mergecorpora_page.statusdisplay.clear()
        for listname in results_lists.keys():
            if len(results_lists[listname]) > 0:
                filenames = [filenamefrompath(fp) for fp in results_lists[listname]]
                statusstring = listname + ":\n\t" + ",\n\t".join(filenames)
                self.mergecorpora_page.statusdisplay.appendText(statusstring, joinwithnewline=True)

    def load_and_merge_corpora(self):
        mergedcorpus = Corpus()
        results_lists = {
            "conflicting Entry IDs": [],
            "incorrect format": [],
            "failed to load": [],
            "failed to count": [],
            "successful results": [],
            "duplicated glosses": [],
            "duplicated lemmas": [],
            "duplicated ID-glosses": []
        }

        glosses_seen = defaultdict(list)
        lemmas_seen = defaultdict(list)
        idglosses_seen = defaultdict(list)

        # check file formats
        validfilenames = [fname for fname in self.corpusfilepaths if fname.endswith(".slpaa")]
        invalidfilenames = [fname for fname in self.corpusfilepaths if fname not in validfilenames]
        results_lists["incorrect format"] = invalidfilenames

        corporatomerge = [self.parent().load_corpus_binary(fname) for fname in validfilenames]

        # check if EntryIDs overlap at all
        entryIDs_overlap = self.checkforoverlap_entryIDs(corporatomerge)
        if entryIDs_overlap and not self.makenewIDs_ifconflict:
            # give up and cancel the merge
            results_lists["conflicting Entry IDs"].append("merge canceled")  # TODO KV it looks like the destination file (even if an existing corpus) is empty when merge is canceled-- in essence potentially deleting an existing corpus
        else:
            # go ahead with the merge, either making new EntryIDs or keeping the existing ones as per user specification
            for idx, corpustoadd in enumerate(corporatomerge):
                corpuspath = validfilenames[idx]
                if corpustoadd is None:
                    pass
                    results_lists["failed to load"].append(corpuspath)
                else:
                    if self.makenewIDs_ifnoconflict or self.makenewIDs_ifconflict:
                        next_entryID = mergedcorpus.highestID
                    for sign in corpustoadd.signs:
                        if self.makenewIDs_ifnoconflict or self.makenewIDs_ifconflict:
                            next_entryID += 1
                            sign.signlevel_information.entryid.counter = next_entryID
                        # else: use existing Entry ID (so, nothing to change)
                        mergedcorpus.add_sign(sign)
                        sli = sign.signlevel_information
                        for gloss in [g.lower().strip() for g in sli.gloss if g != ""]:
                            glosses_seen[gloss].append(corpuspath)
                        lemma = sli.lemma.lower().strip()
                        if lemma != "":
                            lemmas_seen[lemma].append(corpuspath)
                        idgloss = sli.idgloss.lower().strip()
                        if idgloss != "":
                            idglosses_seen[idgloss].append(corpuspath)

                    # if self.makenewIDs_ifconflict:
                    #     mergedcorpus.highestID = next_entryID
                    mergedcorpus.confirmhighestID("merge")
                    results_lists["successful results"].append(corpuspath)

                    # results_lists["failed to load"].append(corpusfilepath + " (" + result + ")")

        for (gloss, corpuslist) in glosses_seen.items():
            if len(corpuslist) > 1:
                results_lists["duplicated glosses"].append(gloss)
        for (lemma, corpuslist) in lemmas_seen.items():
            if len(corpuslist) > 1:
                results_lists["duplicated lemmas"].append(lemma)
        for (idgloss, corpuslist) in idglosses_seen.items():
            if len(corpuslist) > 1:
                results_lists["duplicated ID-glosses"].append(idgloss)

        self.parent().save_corpus_binary(othercorpusandpath=(mergedcorpus, self.mergedfilepath))
        return results_lists

    def checkforoverlap_entryIDs(self, corpora):
        entryIDintervals = [(corpus.minimumID, corpus.highestID) for corpus in corpora]
        runningrange = range(0)
        for entryIDinterval in entryIDintervals:
            rangetocompare = range(entryIDinterval[0], entryIDinterval[1]+1)
            if len(runningrange) == 0:  # we're on the first corpus
                runningrange = rangetocompare
            else:
                overlaprange = range(max(runningrange[0], rangetocompare[0]), min(runningrange[-1], rangetocompare[-1]) + 1)
                if len(overlaprange) == 0:
                    # there's no overlap; update the running range
                    runningrange = range(min(runningrange[0], rangetocompare[0]), max(runningrange[-1], rangetocompare[-1])+1)
                else:
                    # there is overlap; give up
                    return True
        return False



class FilesSelectionWizardPage(QWizardPage):
    corpusfilesselected = pyqtSignal(list)
    mergeintoexisting = pyqtSignal(bool)

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.corpusfilenames = []
        self.mergetypeselected = False
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Choose the .slpaa corpus files to merge:"))

        selectionlayout = QHBoxLayout()
        self.selectedfilesdisplay = StatusDisplay()  # QLineEdit()
        choosefilesbutton = QPushButton("Browse")
        choosefilesbutton.clicked.connect(self.handle_select_corpusfiles)
        selectionlayout.addWidget(self.selectedfilesdisplay)
        selectionlayout.addWidget(choosefilesbutton)
        selectionlayout.setAlignment(choosefilesbutton, Qt.AlignTop)
        pagelayout.addLayout(selectionlayout)

        pagelayout.addSpacerItem(QSpacerItem(0, 30, QSizePolicy.Maximum, QSizePolicy.Minimum))

        mergeintoexistinglabel = QLabel("Would you like to merge the selected corpora into the current one, or create a new one?")
        pagelayout.addWidget(mergeintoexistinglabel)
        mergeintoexistingswitch = OptionSwitch("Save current corpus and merge into this one", "Create and save new merged corpus")
        mergeintoexistingswitch.toggled.connect(self.handle_mergeintoexistingswitch_toggled)
        pagelayout.addWidget(mergeintoexistingswitch)

        self.setLayout(pagelayout)

    def isComplete(self):
        return len(self.corpusfilenames) > 0 and self.mergetypeselected

    def handle_mergeintoexistingswitch_toggled(self, valuesdict):
        self.mergeintoexisting.emit(valuesdict[1])
        self.mergetypeselected = True in valuesdict.values()
        self.completeChanged.emit()

    def handle_select_corpusfiles(self):
        self.corpusfilenames, file_type = QFileDialog.getOpenFileNames(self,
                                                             self.tr('Select Corpora'),
                                                             self.app_settings['storage']['recent_folder'],
                                                             self.tr('SLP-AA Corpus (*.slpaa)'))
        self.completeChanged.emit()
        self.corpusfilesselected.emit(self.corpusfilenames)
        self.selectedfilesdisplay.clear()
        for filepath in self.corpusfilenames:
            folders, filename = os.path.split(filepath)
            higherfolders, lowestfolder = os.path.split(folders)
            self.selectedfilesdisplay.appendText(os.path.join("...", lowestfolder, filename), joinwithnewline=True)


class EntryIDStrategyWizardPage(QWizardPage):
    newIDs_ifnoconflict = pyqtSignal(bool)
    newIDs_ifconflict = pyqtSignal(bool)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("If Entry IDs do not conflict:"))

        noconflictlayout = QHBoxLayout()
        noconflictlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        noconflict_sublayout = QVBoxLayout()
        self.noconflict_group = QButtonGroup()
        self.noconflict_keepIDs_rb = QRadioButton("Keep existing EntryIDs")
        self.noconflict_newIDs_rb = QRadioButton("Assign new unique EntryIDs")
        self.noconflict_group.addButton(self.noconflict_keepIDs_rb)
        self.noconflict_group.addButton(self.noconflict_newIDs_rb)
        # self.noconflict_group.buttonToggled.connect(lambda a0, a1: self.handle_buttongroup_toggled(self.noconflict_group))
        self.noconflict_group.buttonToggled.connect(self.handle_buttongroup_toggled)
        noconflict_sublayout.addWidget(self.noconflict_keepIDs_rb)
        noconflict_sublayout.addWidget(self.noconflict_newIDs_rb)
        noconflictlayout.addLayout(noconflict_sublayout)
        pagelayout.addLayout(noconflictlayout)

        pagelayout.addWidget(QLabel("If Entry IDs conflict:"))

        conflictlayout = QHBoxLayout()
        conflictlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        conflict_sublayout = QVBoxLayout()
        self.conflict_group = QButtonGroup()
        self.conflict_newIDs_rb = QRadioButton("Assign new unique EntryIDs")
        self.conflict_cancel_rb = QRadioButton("Cancel merge")
        self.conflict_group.addButton(self.conflict_newIDs_rb)
        self.conflict_group.addButton(self.conflict_cancel_rb)
        # self.conflict_group.buttonToggled.connect(lambda a0, a1: self.handle_buttongroup_toggled(self.conflict_group))
        self.conflict_group.buttonToggled.connect(self.handle_buttongroup_toggled)
        conflict_sublayout.addWidget(self.conflict_newIDs_rb)
        conflict_sublayout.addWidget(self.conflict_cancel_rb)
        conflictlayout.addLayout(conflict_sublayout)
        pagelayout.addLayout(conflictlayout)

        self.setLayout(pagelayout)

    # def handle_buttongroup_toggled(self, btngroup):
    #     if btngroup == self.noconflict_group:
    #         self.newIDs_ifnoconflict.emit(self.noconflict_newIDs_rb.isChecked())
    #     elif btngroup == self.conflict_group:
    #         self.newIDs_ifconflict.emit(self.conflict_newIDs_rb.isChecked())
    #     self.completeChanged.emit()

    def handle_buttongroup_toggled(self, a0, a1):
        btngroup = a0.group()
        if btngroup == self.noconflict_group:
            self.newIDs_ifnoconflict.emit(self.noconflict_newIDs_rb.isChecked())
        elif btngroup == self.conflict_group:
            self.newIDs_ifconflict.emit(self.conflict_newIDs_rb.isChecked())
        self.completeChanged.emit()

    def isComplete(self):
        return self.noconflict_group.checkedButton() is not None and self.conflict_group.checkedButton() is not None


class MergedNameLocationWizardPage(QWizardPage):
    mergedfileselected = pyqtSignal(str)

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.mergedfilename = ""
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Choose the name and location for the merged file:"))

        selectionlayout = QHBoxLayout()
        self.mergedfiledisplay = QLineEdit()
        choosefilebutton = QPushButton("Browse")
        choosefilebutton.clicked.connect(self.handle_select_mergedfile)
        selectionlayout.addWidget(self.mergedfiledisplay)
        selectionlayout.addWidget(choosefilebutton)

        pagelayout.addLayout(selectionlayout)

        self.setLayout(pagelayout)

    def isComplete(self):
        return len(self.mergedfilename) > 0

    def handle_select_mergedfile(self):
        self.mergedfilename, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select merged destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        self.completeChanged.emit()
        self.mergedfileselected.emit(self.mergedfilename)
        self.mergedfiledisplay.setText(self.mergedfilename)


class MergeCorporaWizardPage(QWizardPage):
    mergecorpora = pyqtSignal()
    openmergedcorpus = pyqtSignal(bool)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.mergeattempted = False
        pagelayout = QVBoxLayout()

        mergelayout = QHBoxLayout()
        mergelayout.addWidget(QLabel("Merge selected .slpaa files:"))
        mergecorporabutton = QPushButton("Merge corpora")
        mergecorporabutton.clicked.connect(self.handle_merge_corpora)
        mergelayout.addWidget(mergecorporabutton)
        pagelayout.addLayout(mergelayout)

        statuslayout = QHBoxLayout()
        statuslabel = QLabel("Status of merge:")
        statuslayout.addWidget(statuslabel)
        statuslayout.setAlignment(statuslabel, Qt.AlignTop)
        self.statusdisplay = StatusDisplay("not yet attempted")
        statuslayout.addWidget(self.statusdisplay)
        pagelayout.addLayout(statuslayout)

        self.openmergedfilecb = QCheckBox("Open new merged file")
        self.openmergedfilecb.toggled.connect(self.openmergedcorpus.emit)
        pagelayout.addWidget(self.openmergedfilecb)

        self.setLayout(pagelayout)

    def handle_merge_corpora(self, checked):
        self.mergecorpora.emit()
        self.mergeattempted = True
        self.completeChanged.emit()

    def isComplete(self):
        return self.mergeattempted
