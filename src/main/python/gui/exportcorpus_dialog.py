import io
import json

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFormLayout,
    QFileDialog,
    QWizard,
    QWizardPage,
    QComboBox,
    QLineEdit,
)

from PyQt5.QtCore import pyqtSignal, Qt

from gui.modulespecification_widgets import StatusDisplay
from gui.helper_widget import OptionSwitch


# wizard that walks the user through exporting the current corpus as a .json file (currently only one format available)
class ExportCorpusWizard(QWizard):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.setOption(QWizard.IndependentPages, True)
        self.setOption(QWizard.NoDefaultButton, False)
        self.setOption(QWizard.NoCancelButton, False)
        self.app_settings = app_settings
        self.outputformat = ""
        self.detaillevel = ""

        formatselection_page = ExportFormatSelectionWizardPage()
        formatselection_page.exportformatselected.connect(self.handle_exportformatselected)
        formatselection_page.completeChanged.connect(self.clear_statusdisplay)
        self.formatselection_pageid = self.addPage(formatselection_page)

        fileselection_page = ExportFileSelectionWizardPage(self.app_settings)
        fileselection_page.completeChanged.connect(self.clear_statusdisplay)
        self.fileselection_pageid = self.addPage(fileselection_page)

        self.exportcorpus_page = ExportCorpusWizardPage()
        self.exportcorpus_page.exportcorpus.connect(self.handle_export_corpus)
        self.exportcorpus_pageid = self.addPage(self.exportcorpus_page)

        self.setWindowTitle("Export Corpus")
        # self.updateGeometry()
        # self.repaint()

    def clear_statusdisplay(self):
        self.exportcorpus_page.exportattempted = False
        self.exportcorpus_page.statusdisplay.clear()

    def handle_exportformatselected(self, outputformat, detaillevel):
        self.outputformat = outputformat
        self.detaillevel = detaillevel

    def handle_export_corpus(self):
        self.exportcorpus_page.statusdisplay.setText("exporting...")
        self.exportcorpus_page.statusdisplay.repaint()
        resultmessage = self.export_corpus()
        self.exportcorpus_page.statusdisplay.setText(resultmessage)

    def export_corpus(self):
        # corpus = self.parent().corpus
        if self.parent().corpus is None:
            return "export failed - corpus does not exist"

        serialized_corpus = self.parent().corpus.serialize()
        with io.open(str(self.field("exportedfilepath")), 'w') as exfile:
            # OK, this is a bit convoluted, but it seems like the most general way to be able to omit values
            # that are empty/zero/false/null, is to convert everything to json format and read it back in so
            # all of the data is in either dicts or lists (rather than objects).
            # If we end up wanting to do something prettier or more customized in the future,
            # this kind of cleaning might have to be done in the data classes themselves.

            try:
                # for json.dumps, can also specify separators=(item_separator, key_separator)
                # default is (', ', ': ') if indent is None and (',', ': ') otherwise
                thestring = json.dumps(serialized_corpus, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
            except Exception:
                return "export failed - writing original json"
            try:
                reloaded = json.loads(thestring)
            except json.JSONDecodeError:
                return "export failed - not a valid JSON document"
            except UnicodeDecodeError:
                return "export failed - JSON does not contain UTF-8, UTF-16 or UTF-32 encoded data"
            try:
                cleaned = cleandictsforexport(reloaded, self.detaillevel)
            except Exception:
                return "export failed - cleaning JSON"
            try:
                json.dump(cleaned, exfile, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
            except Exception:
                return "export failed - writing cleaned JSON"

        return "export completed"


# wizard page that asks the user to select the file format for the export,
# and whether it should contain minimal or maximal data
class ExportFormatSelectionWizardPage(QWizardPage):
    exportformatselected = pyqtSignal(str, str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.outputformat = ""
        self.detaillevel = ""

        formlayout = QFormLayout()
        # pagelayout = QVBoxLayout()

        selectformatlabel = QLabel("Choose which format you'd like for the exported data: JSON (.txt) is currently the only option.")
        # selectformatlabel = QLabel("Choose which format you'd like for the exported data:\nJSON (.txt) is currently the only option.")
        # selectformatlabel.setWordWrap(True)
        self.selectformatcombo = QComboBox()
        self.selectformatcombo.currentTextChanged.connect(self.formatcombo_changed)
        self.selectformatcombo.addItems(["JSON (.txt)"])
        formlayout.addRow(selectformatlabel, self.selectformatcombo)
        # pagelayout.addWidget(QLabel("Choose which format you'd like for the exported data:\nJSON (.txt) is currently the only option."))
        # pagelayout.addWidget(self.selectformatcombo)


        formlayout.addRow(QLabel("decoy button for testing macos highlighting"), QPushButton("TODO"))
        selectdetaillabel = QLabel("Choose whether you'd like maximal information (all attribute values, even if they're empty/false/0) or minimal (only specified values).")
        # selectdetaillabel = QLabel("Choose whether you'd like maximal information (all attribute values,\neven if they're empty/false/0) or minimal (only specified values).")
        # selectdetaillabel.setWordWrap(True)
        self.selectdetailswitch = OptionSwitch("Maximal", "Minimal", deselectable=False)
        self.selectdetailswitch.toggled.connect(self.handle_detailswitch_toggled)
        formlayout.addRow(selectdetaillabel, self.selectdetailswitch)
        # pagelayout.addWidget(QLabel("Choose whether you'd like maximal information (all attribute values,\neven if they're empty/false/0) or minimal (only specified values)."))
        # pagelayout.addWidget(self.selectdetailswitch)

        self.setLayout(formlayout)
        # self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.outputformat) > 0 and len(self.detaillevel)

    def handle_detailswitch_toggled(self, selection_dict):
        if selection_dict[1]:
            self.detaillevel = "max"
        elif selection_dict[2]:
            self.detaillevel = "min"
        else:
            self.detaillevel = ""
        self.check_emitsignals()

    def formatcombo_changed(self, txt):
        if "json" in txt.lower():
            self.outputformat = "json"
        else:
            self.outputformat = "something else"
        self.check_emitsignals()

    def check_emitsignals(self):
        if self.isComplete():
            self.completeChanged.emit()
            self.exportformatselected.emit(self.outputformat, self.detaillevel)


# wizard page that asks the user to choose a path/name for the export file
class ExportFileSelectionWizardPage(QWizardPage):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Choose the name and location for the exported file."))

        selectionlayout = QHBoxLayout()
        self.exportedfiledisplay = QLineEdit()
        self.exportedfiledisplay.setReadOnly(True)
        self.registerField("exportedfilepath", self.exportedfiledisplay)
        choosefilebutton = QPushButton("Browse")
        choosefilebutton.clicked.connect(self.handle_select_exportedfile)
        selectionlayout.addWidget(self.exportedfiledisplay)
        selectionlayout.addWidget(choosefilebutton)

        pagelayout.addLayout(selectionlayout)
        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.field("exportedfilepath")) > 0

    # presents the user a standard file selection dialog to choose where to save the exported file
    def handle_select_exportedfile(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select export destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('JSON file (*.txt)'))
        if file_name:
            self.exportedfiledisplay.setText(file_name)
            self.completeChanged.emit()


# wizard page that allows the user to finally confirm exporting the corpus
# it also shows a status display
class ExportCorpusWizardPage(QWizardPage):
    exportcorpus = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.exportattempted = False
        pagelayout = QVBoxLayout()

        exportlayout = QHBoxLayout()
        exportlayout.addWidget(QLabel("Export current .slpaa file:"))
        exportcorpusbutton = QPushButton("Export corpus")
        exportcorpusbutton.clicked.connect(self.handle_export_corpus)
        exportlayout.addWidget(exportcorpusbutton)
        pagelayout.addLayout(exportlayout)

        statuslayout = QHBoxLayout()
        statuslabel = QLabel("Status of export:")
        statuslayout.addWidget(statuslabel)
        statuslayout.setAlignment(statuslabel, Qt.AlignTop)
        self.statusdisplay = StatusDisplay("not yet attempted")
        statuslayout.addWidget(self.statusdisplay)
        pagelayout.addLayout(statuslayout)

        self.setLayout(pagelayout)

    # signals to the parent (wizard) to try exporting the corpus
    def handle_export_corpus(self, checked):
        self.exportcorpus.emit()
        self.exportattempted = True
        self.completeChanged.emit()

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return self.exportattempted


def cleandictsforexport(serialstructure, detaillevel):
    if detaillevel == "max":
        return serialstructure
    elif detaillevel == "min":
        if isinstance(serialstructure, dict):
            cleaned_dict = {}
            for k, v in serialstructure.items():
                if k in ['timingintervals', '_timingintervals']:
                    # do not omit any info from these items; it makes them hard to read
                    cleaned_dict[k] = v
                elif k == 'col_labels' and 'col_contents' in serialstructure.keys():
                    # Originally I didn't include the column labels for the location details, because it would be clear
                    # to the user what they're looking at based on the contents. However, it is necessary to include
                    # the column labels after all (assuming that the contents have any, well... content), for the
                    # purpose of re-importing from a minimal export.
                    col_contents_cleaned = cleandictsforexport(serialstructure['col_contents'], ("mid" if detaillevel == "min" else detaillevel))
                    if col_contents_cleaned != [[], []]:
                        cleaned_dict['col_labels'] = v
                        cleaned_dict['col_contents'] = col_contents_cleaned
                elif k == 'col_contents':
                    # dealt with above
                    pass
                elif k == 'action_state':
                    # do not omit any info from non-manual "action/state" subtrees; even when populated the values are empty dictionaries
                    cleaned_dict[k] = v
                elif k == 'defaultneutrallist' and v is not None:
                    # if default neutral is selected, then even when populated the values of defaultneutrallist are empty dictionaries
                    cleaned_dict[k] = v
                else:
                    cleaned_item = cleandictsforexport(v, detaillevel)
                    if cleaned_item:
                        cleaned_dict[k] = cleaned_item
            return cleaned_dict
        elif isinstance(serialstructure, list):
            cleaned_list = []
            if len(serialstructure) == 2 and isinstance(serialstructure[0], str) and isinstance(serialstructure[1], bool) and not serialstructure[1]:
                # it's a key-value pair of some sort; if the second element is false we don't want the first one either
                pass
            else:
                for v in serialstructure:
                    cleaned_item = cleandictsforexport(v, detaillevel)
                    if cleaned_item:
                        cleaned_list.append(cleaned_item)
            return cleaned_list
        elif isinstance(serialstructure, str) or isinstance(serialstructure, float) or isinstance(serialstructure, int) or isinstance(serialstructure, bool) or serialstructure is None:
            if serialstructure and serialstructure != 0:
                # if it's a pseudo-primitive data type (even though yes, I know, that's not a thing for Python)
                # then just return it as is, as long as it's not empty/zero/false
                return serialstructure
            return None
    elif detaillevel == "mid" and isinstance(serialstructure, list):
        # The only way we should have gotten here is if we're doing a minimal export and we've got an entry in a
        # location details (surfaces/subareas/etc) table. The column labels will be exported as a list of length 2,
        # even though one might be the empty string. Which means that, in order to be imported again properly later,
        # we need the column contents to also be a list of length 2, even though the default cleaning strategy for
        # minimal detail would get rid of the first (empty) entry. So what we want is to have a list of length 2, but
        # the only contents to be those with True appearing in their key-value pairs.

        # assume it's col_contents
        return [cleandictsforexport(cc, "min") for cc in serialstructure]


def nestedlisthascontent(nestedlist):
    thislevelhascontent = False
    for listitem in nestedlist:
        if isinstance(listitem, list):
            if len(listitem) > 0:
                thislevelhascontent = nestedlisthascontent(listitem)
        else:
            thislevelhascontent = True
    return thislevelhascontent
