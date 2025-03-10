import io
import json
from datetime import datetime

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QPushButton,
    QLabel,
    QFormLayout,
    QFrame,
    QDialogButtonBox,
    QFileDialog,
    QComboBox
)

from gui.modulespecification_widgets import StatusDisplay
from lexicon.lexicon_classes import Corpus, Sign, SignLevelInformation
from gui.helper_widget import OptionSwitch


class ImportCorpusDialog(QDialog):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.importfilepath = ""
        self.inputformat = "json"
        # self.detaillevel = "max"

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # self.selectformatlabel = QLabel("1a. Choose which format you'd like for the exported data: JSON (.txt) is currently the only option.")
        # self.selectformatcombo = QComboBox()
        # self.selectformatcombo.addItems(["JSON (.txt)"])
        # self.selectformatcombo.currentTextChanged.connect(self.formatcombo_changed)
        # form_layout.addRow(self.selectformatlabel, self.selectformatcombo)
        self.chooseimportfilelabel = QLabel("1. Select the file to import: JSON (.txt) is currently the only importable format.")
        self.chooseimportfilebutton = QPushButton("Select import file")
        self.chooseimportfilebutton.setEnabled(True)
        self.chooseimportfilebutton.clicked.connect(self.handle_select_importfile)
        form_layout.addRow(self.chooseimportfilelabel, self.chooseimportfilebutton)
        self.importcorpuslabel = QLabel("2. Import JSON to new .slpaa file.")
        self.importcorpusbutton = QPushButton("Import corpus")
        self.importcorpusbutton.setEnabled(False)
        self.importcorpusbutton.clicked.connect(self.handle_import_corpus)
        form_layout.addRow(self.importcorpuslabel, self.importcorpusbutton)
        self.statuslabel = QLabel("3. Status of import:")
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

    # def handle_detailswitch_toggled(self, selection_dict):
    #     if selection_dict[1]:
    #         self.detaillevel = "max"
    #     else:
    #         self.detaillevel = "min"
    #     self.statusdisplay.setText(self.detaillevel + "imal detail selected")
    #     self.chooseexportedfilebutton.setEnabled(True)
    #
    # def formatcombo_changed(self, txt):
    #     if "json" in txt.lower():
    #         newoutputformat = "json"
    #     else:
    #         newoutputformat = "something else"
    #
    #     if newoutputformat != self.outputformat:
    #         self.statusdisplay.setText(newoutputformat + " format selected")
    #     self.outputformat = newoutputformat

    def handle_select_importfile(self):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           caption=self.tr('Select import file'),
                                                           directory=self.app_settings['storage']['recent_folder'],
                                                           filter=self.tr('JSON file (*.txt)'))
        if file_name != self.importfilepath:
            self.statusdisplay.setText("source selected")
        self.importfilepath = file_name
        if len(self.importfilepath) > 0:  #  and self.parent().corpus is not None:
            self.importcorpusbutton.setEnabled(True)

    def handle_import_corpus(self):
        self.statusdisplay.setText("importing...")
        self.statusdisplay.repaint()
        resultmessage = self.import_corpus()
        self.statusdisplay.setText(resultmessage)

    def import_corpus(self):
        # TODO
        returnmessage = ""
        with io.open(self.importfilepath, "r") as imfile:
            # try:
            corpus = Corpus()
            data = json.load(imfile)  # dict with keys: 'signs', 'path', 'minimum id', 'highest id'
            glosses = []
            if 'signs' in data:
                for signdict in data['signs']:
                    sign = self.read_sign(signdict)
                    corpus.add_sign(sign)
                    glosses.append(str(sign))
            returnmessage = "read " + str(len(glosses)) + " signs:\n" + "\n".join(glosses)  # TODO imported
            temp = ""
            # may need to reset or re-confirm corpus path
            # except Exception:
            #     return "import failed"
        # serialized_corpus = self.parent().corpus.serialize()
        # with io.open(self.exportfilepath, "w") as exfile:
        #     try:
        #         # OK, this is a bit convoluted, but it seems like the most general way to be able to omit values
        #         # that are empty/zero/false/null, is to convert everything to json format and read it back in so
        #         # all of the data is in either dicts or lists (rather than objects).
        #         # If we end up wanting to do something prettier or more customized in the future,
        #         # this kind of cleaning might have to be done in the data classes themselves.
        #
        #         # for json.dumps, can also specify separators=(item_separator, key_separator)
        #         # default is (', ', ': ') if indent is None and (',', ': ') otherwise
        #         thestring = json.dumps(serialized_corpus, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
        #         reloaded = json.loads(thestring)
        #         cleaned = cleandictsforexport(reloaded, self.detaillevel)
        #         json.dump(cleaned, exfile, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
        #     except Exception:
        #         return "export failed"
        #
        return "import completed\n\n" + returnmessage

    def read_sign(self, signdict):
        sli = self.read_sli(signdict['signlevel'])
        sign = Sign(signlevel_info=sli)
        # TODO add rest of info
        return sign

    def read_sli(self, slidict):
        # set up defaults for all attributes, just in case they don't all have values to import
        sli = {
            'entryid': 0,
            'gloss': [],
            'lemma': "",
            'idgloss': "",
            'source': "",
            'signer': "",
            'frequency': 0.0,
            'coder': "",
            'date created': datetime.now(),
            'date last modified': datetime.now(),
            'note': "",
            'fingerspelled': False,
            'compoundsign': False,
            'handdominance': 'R'
        }
        for k, v in slidict.items():
            if k.startswith('date '):  # date last created, date last modified
                v = datetime.fromtimestamp(slidict[k])
            sli[k] = v
        return SignLevelInformation(signlevel_info=sli)

    def handle_buttonbox_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Close:
            # close dialog
            self.accept()


def cleandictsforexport(serialstructure, detaillevel):
    if detaillevel == "max":
        return serialstructure
    elif detaillevel == "min":
        if isinstance(serialstructure, dict):
            cleaned_dict = {}
            for k, v in serialstructure.items():
                if k in ["timingintervals", "_timingintervals"]:
                    # do not omit any info from these items; it makes them hard to read
                    cleaned_dict[k] = v
                elif k == "col_labels":
                    # don't worry about including the column labels for the location details;
                    # it should be clear from the contents what we're looking at
                    pass
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
                # if it's a pseudo-primite data type (even though yes, I know, that's not a thing for Python)
                # then just return it as is, as long as it's not empty/zero/false
                return serialstructure
            return None
