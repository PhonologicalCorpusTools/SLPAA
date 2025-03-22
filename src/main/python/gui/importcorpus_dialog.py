import io
import json
from datetime import datetime
from fractions import Fraction

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
from lexicon.lexicon_classes import Corpus, Sign
from lexicon.module_classes import SignLevelInformation, Signtype, AddedInfo, XslotStructure, MovementModule, \
    LocationModule, RelationModule, OrientationModule, HandConfigurationModule, NonManualModule, \
    TimingInterval, TimingPoint
from serialization_classes import MovementTreeSerializable
from models.movement_models import MovementTreeModel
from gui.helper_widget import OptionSwitch


class ImportCorpusDialog(QDialog):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.importsourcepath = ""
        self.inputformat = "json"
        self.destpath = ""
        # self.detaillevel = "max"

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        # self.selectformatlabel = QLabel("1a. Choose which format you'd like for the exported data: JSON (.txt) is currently the only option.")
        # self.selectformatcombo = QComboBox()
        # self.selectformatcombo.addItems(["JSON (.txt)"])
        # self.selectformatcombo.currentTextChanged.connect(self.formatcombo_changed)
        # form_layout.addRow(self.selectformatlabel, self.selectformatcombo)
        self.chooseimportsourcelabel = QLabel("1. Select the file to import: JSON (.txt) is currently the only importable format.")
        self.chooseimportsourcebutton = QPushButton("Select import source")
        self.chooseimportsourcebutton.setEnabled(True)
        self.chooseimportsourcebutton.clicked.connect(self.handle_select_importsource)
        form_layout.addRow(self.chooseimportsourcelabel, self.chooseimportsourcebutton)
        self.choosedestlabel = QLabel("2. Choose the name and location to save the corpus file generated from the import.")
        self.choosedestbutton = QPushButton("Select import destination")
        self.choosedestbutton.setEnabled(False)
        self.choosedestbutton.clicked.connect(self.handle_select_dest)
        form_layout.addRow(self.choosedestlabel, self.choosedestbutton)
        self.importcorpuslabel = QLabel("3. Import JSON to new .slpaa file.")
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

    def handle_select_dest(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select import destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_name != self.destpath:
            self.statusdisplay.setText("destination selected")
        self.destpath = file_name
        if len(self.destpath) > 0 and len(self.importsourcepath) > 0:  #
            self.importcorpusbutton.setEnabled(True)

    def handle_select_importsource(self):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           caption=self.tr('Select import file'),
                                                           directory=self.app_settings['storage']['recent_folder'],
                                                           filter=self.tr('JSON file (*.txt)'))
        if file_name != self.importsourcepath:
            self.statusdisplay.setText("source selected")
        self.importsourcepath = file_name
        if len(self.importsourcepath) > 0:
            self.choosedestbutton.setEnabled(True)
            if len(self.destpath) > 0:
                self.importcorpusbutton.setEnabled(True)

    def handle_import_corpus(self):
        self.statusdisplay.setText("importing...")
        self.statusdisplay.repaint()
        resultmessage = self.import_corpus()
        self.statusdisplay.setText(resultmessage)

    def import_corpus(self):
        # TODO
        returnmessage = ""
        with io.open(self.importsourcepath, "r") as imfile:
            # try:
            corpus = Corpus()
            data = json.load(imfile)  # dict with keys: 'signs', 'path', 'minimum id', 'highest id'
            glosses = []
            if 'signs' in data.keys():
                for signdict in data['signs']:
                    sign = self.read_sign(signdict)
                    corpus.add_sign(sign)
                    glosses.append(str(sign))
            # if 'path' in data.keys():
            #     corpus.path = data['path']
            corpus.path = self.destpath
            if 'minimum id' in data.keys():
                corpus.minimumID = data['minimum id']
            if 'highest id' in data.keys():
                corpus.highestID = data['highest id']
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
        self.parent().load_corpus_info(corpus.path, preloadedcorpus=corpus)
        return "import completed\n\n" + returnmessage

    def read_sign(self, signdict):
        sli = self.read_sli(signdict['signlevel'])
        sign = Sign(signlevel_info=sli)
        if 'type' in signdict.keys():
            stype = self.read_signtype(signdict['type'])
            sign.signtype = stype
        if 'xslot structure' in signdict.keys():
            xslotstruct = self.read_xslotstructure(signdict['xslot structure'])
            sign.xslotstructure = xslotstruct
        if 'specified xslots' in signdict.keys():
            sign.specifiedxslots = bool(signdict['specified xslots'])  # could be True, False, or None
        if 'mov modules' in signdict.keys() and signdict['mov modules'] is not None:
            for uid in signdict['mov modules']:
                movmod = self.read_movmod(float(uid), signdict['mov modules'][uid])
                sign.addmodule(movmod)
            if 'mov module numbers' in signdict.keys() and signdict['mov module numbers'] is not None:
                sign.movementmodulenumbers = {float(uid):num for uid, num in signdict['mov module numbers'].items()}
        if 'loc modules' in signdict.keys() and signdict['loc modules'] is not None:
            # TODO

            if 'loc module numbers' in signdict.keys() and signdict['loc module numbers'] is not None:
                sign.locationmodulenumbers = {float(uid):num for uid, num in signdict['loc module numbers'].items()}
        if 'rel modules' in signdict.keys() and signdict['rel modules'] is not None:
            # TODO
            # TODO double check order from unserialization code, for whether rel or loc goes first

            if 'rel module numbers' in signdict.keys() and signdict['rel module numbers'] is not None:
                sign.relationmodulenumbers = {float(uid):num for uid, num in signdict['rel module numbers'].items()}
        if 'ori modules' in signdict.keys() and signdict['ori modules'] is not None:
            # TODO

            if 'ori module numbers' in signdict.keys() and signdict['ori module numbers'] is not None:
                sign.orientationmodulenumbers = {float(uid):num for uid, num in signdict['ori module numbers'].items()}
        if 'nonman modules' in signdict.keys() and signdict['nonman modules'] is not None:
            # TODO

            if 'nonman module numbers' in signdict.keys() and signdict['nonman module numbers'] is not None:
                sign.nonmanualmodulenumbers = {float(uid):num for uid, num in signdict['nonman module numbers'].items()}
        if 'cfg modules' in signdict.keys() and signdict['cfg modules'] is not None:
            # TODO

            if 'cfg module numbers' in signdict.keys() and signdict['cfg module numbers'] is not None:
                sign.handconfigmodulenumbers = {float(uid):num for uid, num in signdict['cfg module numbers'].items()}

        return sign

    def read_articulators(self, articulatorsentry):
        whicharticulator = articulatorsentry[0]
        whichnums = {1: False, 2: False}
        for k, v in articulatorsentry[1].items():
            whichnums[int(k)] = v
        return whicharticulator, whichnums

    def read_timingintervals(self, timingintervalsentry):
        timingintervals = []
        for intervaldict in timingintervalsentry:
            timinginterval = TimingInterval(TimingPoint(intervaldict['_startpoint']['_wholepart'],
                                                        Fraction(intervaldict['_startpoint']['_fractionalpart'])),
                                            TimingPoint(intervaldict['_endpoint']['_wholepart'],
                                                        Fraction(intervaldict['_endpoint']['_fractionalpart'])))
            timingintervals.append(timinginterval)
        return timingintervals

    def read_parameter_module(self, paramdict):
        # articulators have to be specified in movement modules, so no need to check for existence
        articulators = self.read_articulators(paramdict['_articulators'])
        # timing intervals have to be specified in modules (even if xslots aren't on), so no need to check for existence
        timingintervals = self.read_timingintervals(paramdict['timingintervals'])
        return articulators, timingintervals

    def read_movmod(self, uid, movdict):
        # attributes common to all parameter modules
        # added info TODO
        articulators, timingintervals = self.read_parameter_module(movdict)
        # movement tree
        mtreeser = MovementTreeSerializable(infodicts=movdict['movementtree'])
        mtree = MovementTreeModel(serializedmvmttree=mtreeser)

        # phonlocs TODO
        # inphase TODO

        mmod = MovementModule(mtree, articulators, timingintervals=timingintervals, phonlocs=None, addedinfo=None, inphase=0)
        mmod.uniqueid = uid
        return mmod

    def read_xslotstructure(self, xssdict):
        xss = XslotStructure()
        if xssdict is not None:
            if '_number' in xssdict.keys() and xssdict['_number'] is not None:
                xss.number = xssdict['_number']
            if '_fractionalpoints' in xssdict.keys() and xssdict['_fractionalpoints'] is not None:
                xss.fractionalpoints = [Fraction(f) for f in xssdict['_fractionalpoints']]
            if '_additionalfraction' in xssdict.keys() and xssdict['_additionalfraction'] is not None:
                xss.additionalfraction = Fraction(xssdict['_additionalfraction'])
        return xss

    def read_signtype(self, typedict):
        if typedict is None:
            return typedict

        specslist = []
        if '_specslist' in typedict.keys() and typedict['_specslist'] is not None:
            specslist = [tuple(specpair) for specpair in typedict['_specslist']]

        addedinfo = AddedInfo()
        if '_addedinfo' in typedict.keys() and typedict['_addedinfo'] is not None:
            addedinfo.__dict__.update(typedict['_addedinfo'])

        return Signtype(specslist, addedinfo)

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
