import io
import json

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
from gui.helper_widget import OptionSwitch


class ExportCorpusDialog(QDialog):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.exportfilepath = ''
        self.outputformat = "json"
        self.detaillevel = "max"

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.selectformatlabel = QLabel("1a. Choose which format you'd like for the exported data: JSON (.txt) is currently the only option.")
        self.selectformatcombo = QComboBox()
        self.selectformatcombo.addItems(["JSON (.txt)"])
        self.selectformatcombo.currentTextChanged.connect(self.formatcombo_changed)
        form_layout.addRow(self.selectformatlabel, self.selectformatcombo)
        self.selectdetaillabel = QLabel("1b. Choose whether you'd like maximal information (all attribute values, even if they're empty/false/0) or minimal (only specified values).")
        self.selectdetailswitch = OptionSwitch("Maximal", "Minimal")
        self.selectdetailswitch.toggled.connect(self.handle_detailswitch_toggled)
        form_layout.addRow(self.selectdetaillabel, self.selectdetailswitch)
        self.chooseexportedfilelabel = QLabel("2. Choose the name and location for the exported file.")
        self.chooseexportedfilebutton = QPushButton("Select exported file")
        self.chooseexportedfilebutton.setEnabled(False)
        self.chooseexportedfilebutton.clicked.connect(self.handle_select_exportedfile)
        form_layout.addRow(self.chooseexportedfilelabel, self.chooseexportedfilebutton)
        self.exportcorpuslabel = QLabel("3. Export current .slpaa file.")
        self.exportcorpusbutton = QPushButton("Export corpus")
        self.exportcorpusbutton.setEnabled(False)
        self.exportcorpusbutton.clicked.connect(self.handle_export_corpus)
        form_layout.addRow(self.exportcorpuslabel, self.exportcorpusbutton)
        self.statuslabel = QLabel("4. Status of export:")
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

    def handle_detailswitch_toggled(self, selection_dict):
        if selection_dict[1]:
            self.detaillevel = "max"
        else:
            self.detaillevel = "min"
        self.statusdisplay.setText(self.detaillevel + "imal detail selected")
        self.chooseexportedfilebutton.setEnabled(True)

    def formatcombo_changed(self, txt):
        if "json" in txt.lower():
            newoutputformat = "json"
        else:
            newoutputformat = "unrecognized"

        if newoutputformat != self.outputformat:
            self.statusdisplay.setText(newoutputformat + " format selected")
        self.outputformat = newoutputformat

    def handle_select_exportedfile(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr("Select export destination"),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr("JSON file (*.txt)"))
        if file_name != self.exportfilepath:
            self.statusdisplay.setText("destination selected")
        self.exportfilepath = file_name
        if len(self.exportfilepath) > 0 and self.parent().corpus is not None:
            self.exportcorpusbutton.setEnabled(True)

    def handle_export_corpus(self):
        self.statusdisplay.setText("exporting...")
        self.statusdisplay.repaint()
        resultmessage = self.export_corpus()
        self.statusdisplay.setText(resultmessage)

    def export_corpus(self):
        # corpus = self.parent().corpus
        serialized_corpus = self.parent().corpus.serialize()
        with io.open(self.exportfilepath, 'w') as exfile:
            try:
                # OK, this is a bit convoluted, but it seems like the most general way to be able to omit values
                # that are empty/zero/false/null, is to convert everything to json format and read it back in so
                # all of the data is in either dicts or lists (rather than objects).
                # If we end up wanting to do something prettier or more customized in the future,
                # this kind of cleaning might have to be done in the data classes themselves.

                # for json.dumps, can also specify separators=(item_separator, key_separator)
                # default is (', ', ': ') if indent is None and (',', ': ') otherwise
                thestring = json.dumps(serialized_corpus, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
                reloaded = json.loads(thestring)
                cleaned = cleandictsforexport(reloaded, self.detaillevel)  # TODO this is where we lose everything but 'mouth' for TRY's nonmanuals
                json.dump(cleaned, exfile, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
            except Exception:
                return "export failed"

        return "export completed"

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
                # elif "body" in k:
                #     cleaned_item = cleandictsforexport(v, detaillevel)
                #     if cleaned_item:
                #         cleaned_dict[k] = cleaned_item
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
        toreturn = [cleandictsforexport(cc, "min") for cc in serialstructure]
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