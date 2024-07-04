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
    QButtonGroup,
    QMessageBox
)

from PyQt5.QtCore import pyqtSignal, Qt

from constant import filenamefrompath
from lexicon.lexicon_classes import Corpus
from gui.modulespecification_widgets import StatusDisplay
from gui.helper_widget import OptionSwitch


# wizard that walks the user through merging one or more corpora, whether into a new file or into the currently-open one
class MergeCorporaWizard(QWizard):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.mainwindow = self.parent()
        self.corpusfilepaths = []
        self.corporatomerge = []
        self.mergedfilepath = ""
        self.mergesuccessful = False
        self.mergeintoexisting = False
        self.makenewIDs_ifnoconflict = None
        self.makenewIDs_ifconflict = None

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
        self.mergecorpora_pageid = self.addPage(self.mergecorpora_page)

        self.setWindowTitle("Merge Corpora")

        self.button(QWizard.FinishButton).clicked.connect(self.onFinish)

    # when the user clicks the "Finish" button, open the newly-merged corpus if applicable
    def onFinish(self, checked):
        if self.field("openmergedcorpus") and os.path.exists(self.mergedfilepath) and self.mergesuccessful:
            # if "Open new merged file ..." on MergeCorporaWizardPage is checked
            # and the merged path exists
            #   (but this might be because the user was going to overwrite a previously existing file)
            # and the merge was successful
            self.mainwindow.load_corpus_info(self.mergedfilepath)

    # this logic allows all pages to be followed in the order in which they were added,
    #   but skips the one asking for a filename for the merged file if the user wants to merge into the current corpus
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

    # ensure the appropriate corpora to merge are selected
    #   (make sure current corpus is either not selected, or not selected twice, as applicable)
    # load and merge corpora
    # display results messages in status display
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

    # load corpora to be merged from their paths
    # merge if possible (but merge might be canceled if the user said to do so in the case of conflicting EntryIDs,
    #   or if there are duplicate IDglosses and the user decides to cancel out of the merge and address the duplicates
    #   before trying again
    # returns a dictionary of results messages
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

        # check file formats
        validfilenames = [fname for fname in self.corpusfilepaths if fname.endswith(".slpaa")]
        invalidfilenames = [fname for fname in self.corpusfilepaths if fname not in validfilenames]
        results_lists["incorrect format"] = invalidfilenames

        self.corporatomerge = [self.parent().load_corpus_binary(fname) for fname in validfilenames]

        # check if EntryIDs overlap at all
        entryIDs_overlap = self.checkforoverlap_entryIDs()
        if entryIDs_overlap and not self.makenewIDs_ifconflict:
            # give up and cancel the merge
            results_lists["conflicting Entry IDs"].append("merge canceled due to conflicting EntryIDs")
        else:
            duplicated_IDglosses = self.checkforoverlap_IDglosses()
            dupl_IDglosses_counters = {k:0 for k in duplicated_IDglosses}
            if len(duplicated_IDglosses) > 0:
                results_lists["duplicated ID-glosses"] = duplicated_IDglosses
                firstduplicate = duplicated_IDglosses[0]
                response = QMessageBox.question(self, "Duplicated ID-glosses",
                                                "The corpora you selected have one or more overlapping ID-glosses (" +
                                                ", ".join(duplicated_IDglosses) + "), which are not permitted. " +
                                                "Click 'OK' to proceed with the merge and append numerals to the " +
                                                "duplicated ID-glosses (e.g. " + firstduplicate + "1, " + firstduplicate + "2) " +
                                                "or 'Cancel' to exit this wizard and edit the ID-glosses yourself before trying again.",
                                                buttons=QMessageBox.Ok | QMessageBox.Cancel)
                if response == QMessageBox.Cancel:
                    # also cancel out of the whole merge wizard
                    self.button(QWizard.CancelButton).click()
                    return results_lists
                # else: continue on with the merge, but make sure to tag the duplicated ID-glosses

            # go ahead with the merge, either making new EntryIDs or keeping the existing ones as per user specification
            # and tagging any duplicated ID-glosses, if applicable
            for idx, corpustoadd in enumerate(self.corporatomerge):
                corpuspath = validfilenames[idx]
                if corpustoadd is None:
                    pass
                    results_lists["failed to load"].append(corpuspath)
                else:
                    if self.makenewIDs_ifnoconflict or self.makenewIDs_ifconflict:
                        next_entryID = mergedcorpus.highestID
                    for sign in corpustoadd.signs:
                        sli = sign.signlevel_information
                        if self.makenewIDs_ifnoconflict or self.makenewIDs_ifconflict:
                            next_entryID += 1
                            sli.entryid.counter = next_entryID
                        # else: use existing Entry ID (so, nothing to change)
                        # tag duplicatd ID-gloss with index, if applicable
                        if sli.idgloss in dupl_IDglosses_counters.keys():
                            dupl_IDglosses_counters[sli.idgloss] += 1
                            sli.idgloss += str(dupl_IDglosses_counters[sli.idgloss])

                        mergedcorpus.add_sign(sign)
                        for gloss in [g.lower().strip() for g in sli.gloss if g != ""]:
                            glosses_seen[gloss].append(corpuspath)
                        lemma = sli.lemma.lower().strip()
                        if lemma != "":
                            lemmas_seen[lemma].append(corpuspath)
                    mergedcorpus.confirmhighestID("merge")
                    results_lists["successful results"].append(corpuspath)

                for (gloss, corpuslist) in glosses_seen.items():
                    if len(corpuslist) > 1 and gloss not in results_lists["duplicated glosses"]:
                        results_lists["duplicated glosses"].append(gloss)
                for (lemma, corpuslist) in lemmas_seen.items():
                    if len(corpuslist) > 1 and lemma not in results_lists["duplicated lemmas"]:
                        results_lists["duplicated lemmas"].append(lemma)

                self.parent().save_corpus_binary(othercorpusandpath=(mergedcorpus, self.mergedfilepath))
                self.mergesuccessful = True
        return results_lists

    # return a list of IDglosses that are duplicated in the corpora to be merged
    # list is empty if there are no duplicated IDglosses
    def checkforoverlap_IDglosses(self):
        idglosses_in_merge = [sign.signlevel_information.idgloss.lower().strip() for corpus in self.corporatomerge for sign in corpus.signs]
        seen = set()
        dupes = []
        for idgloss in [idgloss for idgloss in idglosses_in_merge if idgloss != ""]:
            if idgloss in seen:
                dupes.append(idgloss)
            else:
                seen.add(idgloss)
        return dupes

    # return True iff the entryID ranges for any of the merging corpora overlap at all
    def checkforoverlap_entryIDs(self):
        entryIDintervals = [(corpus.minimumID, corpus.highestID) for corpus in self.corporatomerge]
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


# wizard page that asks the user to select which files should be merged, and whether they should be saved as an entirely
# new corpus or folded into the one that's currently open
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

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.corpusfilenames) > 0 and self.mergetypeselected

    # track in this page, and signal to parent wizard, that the merge should be done into the currently-open corpus
    def handle_mergeintoexistingswitch_toggled(self, valuesdict):
        self.mergeintoexisting.emit(valuesdict[1])
        self.mergetypeselected = True in valuesdict.values()
        self.completeChanged.emit()

    # presents the user with a standard file selection dialog to choose which corpora to merge
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


# wizard page that asks the user to decide what to do with Entry IDs in case the ones from the various merging corpora
# (a) don't conflict or (b) do conflict
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

    # updates the parent wizard with information about what to do in case of conflicting/non-conflicting Entry IDs
    def handle_buttongroup_toggled(self, a0, a1):
        btngroup = a0.group()
        if btngroup == self.noconflict_group:
            self.newIDs_ifnoconflict.emit(self.noconflict_newIDs_rb.isChecked())
        elif btngroup == self.conflict_group:
            self.newIDs_ifconflict.emit(self.conflict_newIDs_rb.isChecked())
        self.completeChanged.emit()

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return self.noconflict_group.checkedButton() is not None and self.conflict_group.checkedButton() is not None


# wizard page that asks the user to choose a path/name for the merged file
# this page does not always show; if the user chose to merge into an existing corpus then it is not necessary
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

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.mergedfilename) > 0

    # presents the user a standard file selection dialog to choose where to save the merged file
    def handle_select_mergedfile(self):
        self.mergedfilename, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select merged destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        self.completeChanged.emit()
        self.mergedfileselected.emit(self.mergedfilename)
        self.mergedfiledisplay.setText(self.mergedfilename)


# wizard page that allows the user to finally confirm merging the corpora
# it also shows a status display and offers the user an option to open the newly-merged corpus upon exiting the wizard
class MergeCorporaWizardPage(QWizardPage):
    mergecorpora = pyqtSignal()

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

        self.openmergedfilecb = QCheckBox("Open new merged file when this dialog box is closed")
        self.registerField("openmergedcorpus", self.openmergedfilecb)
        pagelayout.addWidget(self.openmergedfilecb)

        self.setLayout(pagelayout)

    # signals to the parent (wizard) to try merging the corpora
    def handle_merge_corpora(self, checked):
        self.mergecorpora.emit()
        self.mergeattempted = True
        self.completeChanged.emit()

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return self.mergeattempted
