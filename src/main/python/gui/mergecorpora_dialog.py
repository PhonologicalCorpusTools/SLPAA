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
        self.setOption(QWizard.IndependentPages, True)
        self.app_settings = app_settings
        self.mainwindow = self.parent()
        self.corpusfilepaths = []
        self.corporatomerge = []
        self.mergesuccessful = False

        fileselection_page = FilesSelectionWizardPage(self.app_settings)
        fileselection_page.corpusfilesselected.connect(self.handle_corpusfilesselected)
        fileselection_page.completeChanged.connect(self.clear_statusdisplay)
        self.fileselection_pageid = self.addPage(fileselection_page)

        entryIDstrategy_page = EntryIDStrategyWizardPage()
        entryIDstrategy_page.completeChanged.connect(self.clear_statusdisplay)
        self.entryIDstrategy_pageid = self.addPage(entryIDstrategy_page)

        namelocation_page = MergedNameLocationWizardPage(self.app_settings)
        namelocation_page.completeChanged.connect(self.clear_statusdisplay)
        self.namelocation_pageid = self.addPage(namelocation_page)

        self.mergecorpora_page = MergeCorporaWizardPage()
        self.mergecorpora_page.mergecorpora.connect(self.handle_merge_corpora)
        self.mergecorpora_pageid = self.addPage(self.mergecorpora_page)

        self.setWindowTitle("Merge Corpora")

        self.button(QWizard.FinishButton).clicked.connect(self.onFinish)

    def clear_statusdisplay(self):
        self.mergecorpora_page.mergeattempted = False
        self.mergecorpora_page.statusdisplay.clear()

    # when the user clicks the "Finish" button, open the newly-merged corpus if applicable
    def onFinish(self, checked):
        mergedfilepath_str = str(self.field("mergedfilepath"))
        if self.field("openmergedcorpus") and os.path.exists(mergedfilepath_str) and self.mergesuccessful:
            # if "Open new merged file ..." on MergeCorporaWizardPage is checked
            # and the merged path exists
            #   (but this might be because the user was going to overwrite a previously existing file)
            # and the merge was successful
            self.mainwindow.load_corpus_info(mergedfilepath_str)

    def handle_corpusfilesselected(self, fileslist):
        self.corpusfilepaths = fileslist

    # ensure the appropriate corpora to merge are selected
    #   (make sure current corpus is either not selected, or not selected twice, as applicable)
    # load and merge corpora
    # display results messages in status display
    def handle_merge_corpora(self):

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

        if entryIDs_overlap and self.field("conflict_cancel"):
            # there is overlap, and the user said to cancel the merge in the case of overlap
            # so, give up and cancel the merge
            results_lists["conflicting Entry IDs"].append("merge canceled due to conflicting EntryIDs")
            return results_lists
        else:
            # go ahead with the merge, whether with new IDs or not (as specified by user)
            makenewIDs = (entryIDs_overlap and self.field("conflict_newIDs")) or self.field("noconflict_newIDs")

            # check for duplicated IDglosses
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
                    if makenewIDs:
                        next_entryID = mergedcorpus.highestID
                    for sign in corpustoadd.signs:
                        sli = sign.signlevel_information
                        if makenewIDs:
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

                self.parent().save_corpus_binary(othercorpusandpath=(mergedcorpus, str(self.field("mergedfilepath"))))
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

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.corpusfilenames = []
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Choose the .slpaa corpus files to merge:"))

        selectionlayout = QHBoxLayout()
        self.selectedfilesdisplay = StatusDisplay()  # QLineEdit()
        self.selectedfilesdisplay.setMinimumWidth(500)
        choosefilesbutton = QPushButton("Browse")
        choosefilesbutton.clicked.connect(self.handle_select_corpusfiles)
        selectionlayout.addWidget(self.selectedfilesdisplay)
        selectionlayout.addWidget(choosefilesbutton)
        selectionlayout.setAlignment(choosefilesbutton, Qt.AlignTop)
        pagelayout.addLayout(selectionlayout)

        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.corpusfilenames) > 0  #  and self.mergetypeselected

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
        self.registerField("noconflict_keepIDs", self.noconflict_keepIDs_rb)
        self.registerField("noconflict_newIDs", self.noconflict_newIDs_rb)
        self.noconflict_group.addButton(self.noconflict_keepIDs_rb)
        self.noconflict_group.addButton(self.noconflict_newIDs_rb)
        self.noconflict_group.buttonToggled.connect(lambda a0, a1: self.completeChanged.emit())
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
        self.registerField("conflict_newIDs", self.conflict_newIDs_rb)
        self.registerField("conflict_cancel", self.conflict_cancel_rb)
        self.conflict_group.addButton(self.conflict_newIDs_rb)
        self.conflict_group.addButton(self.conflict_cancel_rb)
        self.conflict_group.buttonToggled.connect(lambda a0, a1: self.completeChanged.emit())
        conflict_sublayout.addWidget(self.conflict_newIDs_rb)
        conflict_sublayout.addWidget(self.conflict_cancel_rb)
        conflictlayout.addLayout(conflict_sublayout)
        pagelayout.addLayout(conflictlayout)

        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return self.noconflict_group.checkedButton() is not None and self.conflict_group.checkedButton() is not None


# wizard page that asks the user to choose a path/name for the merged file
# this page does not always show; if the user chose to merge into an existing corpus then it is not necessary
class MergedNameLocationWizardPage(QWizardPage):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Choose the name and location for the merged file:"))

        selectionlayout = QHBoxLayout()
        self.mergedfiledisplay = QLineEdit()
        self.registerField("mergedfilepath", self.mergedfiledisplay)
        choosefilebutton = QPushButton("Browse")
        choosefilebutton.clicked.connect(self.handle_select_mergedfile)
        selectionlayout.addWidget(self.mergedfiledisplay)
        selectionlayout.addWidget(choosefilebutton)

        pagelayout.addLayout(selectionlayout)

        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.field("mergedfilepath")) > 0

    # presents the user a standard file selection dialog to choose where to save the merged file
    def handle_select_mergedfile(self):
        mergedfilename, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select merged destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        self.mergedfiledisplay.setText(mergedfilename)
        self.completeChanged.emit()


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
