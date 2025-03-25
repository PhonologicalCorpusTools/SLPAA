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
    TimingInterval, TimingPoint, Direction, PhonLocations
from serialization_classes import MovementTreeSerializable, LocationTreeSerializable
from models.movement_models import MovementTreeModel
from models.location_models import LocationTreeModel
from gui.helper_widget import OptionSwitch


class ImportCorpusDialog(QDialog):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.importsourcepath = ""
        self.inputformat = "json"
        self.destpath = ""

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

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
            try:
                corpus = Corpus()
                data = json.load(imfile)  # dict with keys: 'signs', 'path', 'minimum id', 'highest id'
                glosses = []
                if 'signs' in data.keys():
                    for signdict in data['signs']:
                        sign = self.read_sign(signdict)
                        corpus.add_sign(sign)
                        glosses.append(str(sign))
                corpus.path = self.destpath
                if 'minimum id' in data.keys():
                    corpus.minimumID = data['minimum id']
                if 'highest id' in data.keys():
                    corpus.highestID = data['highest id']
                returnmessage = "imported " + str(len(glosses)) + " signs:\n" + "\n".join(glosses)
            except Exception:
                return "import failed"
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
            for uid in signdict['ori modules']:
                orimod = self.read_orimod(float(uid), signdict['ori modules'][uid])
                sign.addmodule(orimod)
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

    def read_addedinfo(self, addedinfodict):
        addedinfo = AddedInfo()
        addedinfo.__dict__.update(addedinfodict)
        return addedinfo

    def read_phonlocs(self, phonlocsdict):
        phonlocs = PhonLocations()
        phonlocs.__dict__.update(phonlocsdict)
        return phonlocs

    def read_parameter_module(self, paramdict):
        # articulators have to be specified in movement modules, so no need to check for existence
        articulators = self.read_articulators(paramdict['_articulators'])
        # timing intervals have to be specified in modules (even if xslots aren't on), so no need to check for existence
        timingintervals = self.read_timingintervals(paramdict['_timingintervals'])
        # phonological/phonetic locations may or may not be present
        phonlocs = self.read_phonlocs(paramdict['_phonlocs']) if '_phonlocs' in paramdict.keys() else PhonLocations()
        # added info may or may not be present
        addedinfo = self.read_addedinfo(paramdict['_addedinfo']) if '_addedinfo' in paramdict.keys() else AddedInfo()

        return articulators, timingintervals, phonlocs, addedinfo
    def read_overalloptions(self, overalloptionsdict):
        options = {
            'forearm': False,
            'forearm_addedinfo': AddedInfo(),
            'overall_addedinfo': AddedInfo()
        }
        if overalloptionsdict is not None:
            if 'forearm' in overalloptionsdict:
                options['forearm'] = overalloptionsdict['forearm']
            if 'forearm_addedinfo' in overalloptionsdict:
                options['forearm_addedinfo'] = self.read_addedinfo(overalloptionsdict['forearm_addedinfo'])
            if 'overall_addedinfo' in overalloptionsdict:
                options['overall_addedinfo'] = self.read_addedinfo(overalloptionsdict['overall_addedinfo'])
        return options

    def read_orimod(self, uid, oridict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(oridict)

        # update palm directions and finger root directions
        palmlist = oridict['_palm']
        palmdirs_list = []
        for dirdict in palmlist:
            dir = Direction(axis=dirdict['_axis'])
            dir.__dict__.update(dirdict)
            palmdirs_list.append(dir)
        rootlist = oridict['_root']
        rootdirs_list = []
        for dirdict in rootlist:
            dir = Direction(axis=dirdict['_axis'])
            dir.__dict__.update(dirdict)
            rootdirs_list.append(dir)

        omod = OrientationModule(palmdirs_list=palmdirs_list, rootdirs_list=rootdirs_list, articulators=articulators,
                                 timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)
        omod.uniqueid = uid
        return omod


    def read_movmod(self, uid, movdict):
        # attributes common to all parameter modules
        # added info TODO
        articulators, timingintervals = self.read_parameter_module(movdict)
        # movement tree
        mtreeser = MovementTreeSerializable(infodicts=movdict['movementtree'])
        mtree = MovementTreeModel(serializedmvmttree=mtreeser)
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(movdict)

        # phonlocs TODO
        # inphase TODO
        # movement-specific attributes
        mtreeser = MovementTreeSerializable(infodicts=movdict['movementtree'])  # includes addedinfos for individual movement items
        mtree = MovementTreeModel(serializedmvmttree=mtreeser)
        inphase = movdict['inphase'] if 'inphase' in movdict.keys() else 0

        mmod = MovementModule(mtree, articulators, timingintervals=timingintervals, phonlocs=None, addedinfo=None, inphase=0)
        mmod = MovementModule(mtree, articulators, timingintervals=timingintervals,
                              phonlocs=phonlocs, addedinfo=addedinfo, inphase=inphase)
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

