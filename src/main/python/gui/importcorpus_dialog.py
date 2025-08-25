import io
import os
import json
from datetime import datetime
from fractions import Fraction

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QFormLayout,
    QFileDialog,
    QWizard,
    QWizardPage,
    QLineEdit
)

from PyQt5.QtCore import pyqtSignal, Qt

from gui.modulespecification_widgets import StatusDisplay
from gui.helper_widget import OptionSwitch
from lexicon.lexicon_classes import Corpus, Sign
from lexicon.module_classes import SignLevelInformation, Signtype, AddedInfo, XslotStructure, MovementModule, \
    LocationModule, RelationModule, OrientationModule, HandConfigurationModule, NonManualModule, \
    TimingInterval, TimingPoint, Direction, PhonLocations, RelationX, RelationY, ContactRelation, Distance, \
    BodypartInfo, ContactType, MannerRelation
from serialization_classes import MovementTreeSerializable
from models.movement_models import MovementTreeModel
from models.location_models import LocationTreeModel, BodypartTreeModel
from constant import HAND, ARM, LEG


# Throughout the methods of this class, there are lots of conditionals, default values, and the like, because we
#   don't know if we're importing a maximal or a minimal .json. Don't make any assumptions! (Well... except a few
#   keys that are absolutely guaranteed to exist.)
class ImportCorpusWizard(QWizard):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.setOption(QWizard.IndependentPages, True)
        self.app_settings = app_settings
        self.inputformat = "json"
        self.keeporigtimestamps = True

        sourceselection_page = ImportSourceSelectionWizardPage(self.app_settings)
        sourceselection_page.completeChanged.connect(self.clear_statusdisplay)
        self.sourceselection_pageid = self.addPage(sourceselection_page)

        destselection_page = ImportDestinationSelectionWizardPage(self.app_settings)
        destselection_page.completeChanged.connect(self.clear_statusdisplay)
        self.destselection_pageid = self.addPage(destselection_page)

        timestampselection_page = TimestampSelectionWizardPage()
        timestampselection_page.timestampselected.connect(self.handle_timestampselected)
        timestampselection_page.completeChanged.connect(self.clear_statusdisplay)
        self.timestampselection_pageid = self.addPage(timestampselection_page)

        self.importcorpus_page = ImportCorpusWizardPage()
        self.importcorpus_page.importcorpus.connect(self.handle_import_corpus)
        self.importcorpus_pageid = self.addPage(self.importcorpus_page)

        self.setWindowTitle("Import Corpus")

    def clear_statusdisplay(self):
        self.importcorpus_page.importattempted = False
        self.importcorpus_page.statusdisplay.clear()

    def handle_timestampselected(self, keeporigtimestamps):
        self.keeporigtimestamps = keeporigtimestamps

    def handle_import_corpus(self):
        self.importcorpus_page.statusdisplay.setText("importing...")
        self.importcorpus_page.statusdisplay.repaint()
        resultmessage = self.import_corpus()
        self.importcorpus_page.statusdisplay.setText(resultmessage)

    def import_corpus(self):
        returnmessage = ""
        with io.open(str(self.field("importsourcepath")), "r") as imfile:
            corpus = Corpus()
            glosses = []
            try:
                data = json.load(imfile)  # dict with keys: 'signs', 'path', 'minimum id', 'highest id'
            except json.JSONDecodeError:
                return "import failed - not a valid JSON document"
            except UnicodeDecodeError:
                return "import failed - JSON does not contain UTF-8, UTF-16 or UTF-32 encoded data"
            try:
                if 'signs' in data.keys():
                    for signdict in data['signs']:
                        sign = self.read_sign(signdict)
                        corpus.add_sign(sign)
                        glosses.append(str(sign))
                corpus.path = str(self.field("importdestpath"))
            except Exception:
                return "import failed - reading signs"
            try:
                if 'minimum id' in data.keys():
                    corpus.minimumID = data['minimum id']
                if 'highest id' in data.keys():
                    corpus.highestID = data['highest id']
                returnmessage = "imported " + str(len(glosses)) + " signs:\n" + "\n".join(glosses)
            except Exception:
                return "import failed - setting corpus metadata"
        self.parent().load_corpus_info(corpus.path, preloadedcorpus=corpus)
        return "import completed\n\n" + returnmessage

    def read_sign(self, signdict):
        sli = self.read_sli(signdict.pop('signlevel', {}))
        lastmodified_orig = sli.datelastmodified
        sign = Sign(signlevel_info=sli)
        sign.signtype = self.read_signtype(signdict.pop('type', None))
        sign.xslotstructure = self.read_xslotstructure(signdict.pop('xslot structure', None))
        sign.specifiedxslots = bool(signdict.pop('specified xslots', None))  # could be True, False, or None
        if 'cfg modules' in signdict.keys() and signdict['cfg modules'] is not None:
            for uid in signdict['cfg modules']:
                cfgmod = self.read_cfgmod(float(uid), signdict['cfg modules'][uid])
                sign.addmodule(cfgmod)
            if 'cfg module numbers' in signdict.keys() and signdict['cfg module numbers'] is not None:
                sign.handconfigmodulenumbers = {float(uid):num for uid, num in signdict['cfg module numbers'].items()}
        if 'mov modules' in signdict.keys() and signdict['mov modules'] is not None:
            for uid in signdict['mov modules']:
                movmod = self.read_movmod(float(uid), signdict['mov modules'][uid])
                sign.addmodule(movmod)
            if 'mov module numbers' in signdict.keys() and signdict['mov module numbers'] is not None:
                sign.movementmodulenumbers = {float(uid):num for uid, num in signdict['mov module numbers'].items()}
        # note that relation *must* come before location
        if 'rel modules' in signdict.keys() and signdict['rel modules'] is not None:
            for uid in signdict['rel modules']:
                relmod = self.read_relmod(float(uid), signdict['rel modules'][uid])
                sign.addmodule(relmod)
            if 'rel module numbers' in signdict.keys() and signdict['rel module numbers'] is not None:
                sign.relationmodulenumbers = {float(uid):num for uid, num in signdict['rel module numbers'].items()}
        if 'loc modules' in signdict.keys() and signdict['loc modules'] is not None:
            for uid in signdict['loc modules']:
                locmod = self.read_locmod(float(uid), signdict['loc modules'][uid])
                sign.addmodule(locmod)
            if 'loc module numbers' in signdict.keys() and signdict['loc module numbers'] is not None:
                sign.locationmodulenumbers = {float(uid):num for uid, num in signdict['loc module numbers'].items()}
        if 'ori modules' in signdict.keys() and signdict['ori modules'] is not None:
            for uid in signdict['ori modules']:
                orimod = self.read_orimod(float(uid), signdict['ori modules'][uid])
                sign.addmodule(orimod)
            if 'ori module numbers' in signdict.keys() and signdict['ori module numbers'] is not None:
                sign.orientationmodulenumbers = {float(uid):num for uid, num in signdict['ori module numbers'].items()}
        if 'nonman modules' in signdict.keys() and signdict['nonman modules'] is not None:
            for uid in signdict['nonman modules']:
                nonmanmod = self.read_nonmanmod(float(uid), signdict['nonman modules'][uid])
                sign.addmodule(nonmanmod)
            if 'nonman module numbers' in signdict.keys() and signdict['nonman module numbers'] is not None:
                sign.nonmanualmodulenumbers = {float(uid):num for uid, num in signdict['nonman module numbers'].items()}

        sign.signlevel_information.datelastmodified = lastmodified_orig if self.keeporigtimestamps else datetime.now()
        return sign

    def read_articulators(self, articulatorsentry):
        if articulatorsentry is None:
            return "", {1: False, 2: False}

        whicharticulator = articulatorsentry[0]
        whichnums = {1: False, 2: False}
        # when reading a minimum export, there may not be an artnums entry at all
        if len(articulatorsentry) > 1:
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
        # articulators may or may not be present
        articulators = self.read_articulators(paramdict.pop('_articulators', None))
        # timing intervals have to be specified in modules (even if xslots aren't on), so no need to check for existence
        timingintervals = self.read_timingintervals(paramdict['_timingintervals'])
        # phonological/phonetic locations may or may not be present
        phonlocs = self.read_phonlocs(paramdict.pop('_phonlocs', {}))
        # added info may or may not be present
        addedinfo = self.read_addedinfo(paramdict.pop('_addedinfo', {}))

        return articulators, timingintervals, phonlocs, addedinfo

    def read_handconfig(self, fields_list):
        for field_dict in fields_list:
            for slot_dict in field_dict['slots']:
                if 'symbol' not in slot_dict.keys():
                    slot_dict['symbol'] = ""
                slot_dict['addedinfo'] = self.read_addedinfo(slot_dict.pop('addedinfo', {}))
        return fields_list

    def read_overalloptions(self, overalloptionsdict):
        if overalloptionsdict is None:
            return {
                'forearm': False,
                'forearm_addedinfo': AddedInfo(),
                'overall_addedinfo': AddedInfo()
            }
        else:
            return {
                'forearm': bool(overalloptionsdict.pop('forearm', None)),  # could be True, False, or None
                'forearm_addedinfo': self.read_addedinfo(overalloptionsdict.pop('forearm_addedinfo', {})),
                'overall_addedinfo': self.read_addedinfo(overalloptionsdict.pop('overall_addedinfo', {}))
            }

    def read_cfgmod(self, uid, cfgdict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(cfgdict)

        # handconfig-specific attributes
        handconfig = self.read_handconfig(cfgdict['_handconfiguration'])
        overalloptions = self.read_overalloptions(cfgdict.pop('_overalloptions', None))

        cmod = HandConfigurationModule(handconfiguration=handconfig, overalloptions=overalloptions, articulators=articulators,
                                       timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)
        cmod.uniqueid = uid
        return cmod

    def read_nonmanmod(self, uid, nonmandict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(nonmandict)

        # nonmanual-specific attributes
        nonmanspecs = nonmandict['_nonmanual']
        nmod = NonManualModule(nonman_specs=nonmanspecs, articulators=articulators, timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)
        nmod.uniqueid = uid
        return nmod

    def read_orimod(self, uid, oridict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(oridict)

        # update palm directions and finger root directions
        palmdirs_list = []
        palmlist = oridict.pop('_palm', [])
        for dirdict in palmlist:
            dirn = Direction(axis=dirdict['_axis'])
            dirn.__dict__.update(dirdict)
            palmdirs_list.append(dirn)

        rootdirs_list = []
        rootlist = oridict.pop('_root', [])
        for dirdict in rootlist:
            dirn = Direction(axis=dirdict['_axis'])
            dirn.__dict__.update(dirdict)
            rootdirs_list.append(dirn)

        omod = OrientationModule(palmdirs_list=palmdirs_list, rootdirs_list=rootdirs_list, articulators=articulators,
                                 timingintervals=timingintervals, phonlocs=phonlocs, addedinfo=addedinfo)
        omod.uniqueid = uid
        return omod

    def read_relmod(self, uid, reldict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(reldict)

        # relation-specific attributes
        relx = RelationX()
        relx.__dict__.update(reldict.pop('relationx', {}))
        rely = RelationY()
        rely.__dict__.update(reldict.pop('relationy', {}))
        bodyparts = self.read_bodyparts(reldict.pop('bodyparts_dict', {}))
        contactrel = self.read_contactrel(reldict.pop('contactrel', {}))
        xycrossed = bool(reldict.pop('xy_crossed', None))  # could be True, False, or None
        xylinked = bool(reldict.pop('xy_linked', None))  # could be True, False, or None
        directions = self.read_directions(reldict.pop('directions', {}))

        rmod = RelationModule(relationx=relx, relationy=rely, bodyparts_dict=bodyparts, contactrel=contactrel,
                              xy_crossed=xycrossed, xy_linked=xylinked, directionslist=directions,
                              articulators=articulators, timingintervals=timingintervals,
                              phonlocs=phonlocs, addedinfo=addedinfo)
        rmod.uniqueid = uid
        return rmod

    def read_bodyparts(self, bodypartsdict):
        bodyparts = {}

        for articulator in [HAND, ARM, LEG]:
            bodyparts[articulator] = {}
            for artnum in [1, 2]:
                if articulator in bodypartsdict.keys() and str(artnum) in bodypartsdict[articulator].keys():
                    onebodypart = bodypartsdict[articulator][str(artnum)]
                    # for one bodypart...
                    addedinfo = self.read_addedinfo(onebodypart.pop('addedinfo', {}))
                    bodyparttreemodel = BodypartTreeModel(bodyparttype=articulator,
                                                          jsondict=onebodypart['bodyparttree'])
                    bodyparts[articulator][artnum] = BodypartInfo(bodyparttype=articulator,
                                                                  bodyparttreemodel=bodyparttreemodel,
                                                                  addedinfo=addedinfo)
                else:
                    bodyparts[articulator][artnum] = BodypartInfo(bodyparttype=articulator,
                                                                  bodyparttreemodel=BodypartTreeModel(
                                                                      bodyparttype=articulator),
                                                                  addedinfo=AddedInfo())
        return bodyparts

    def read_contactrel(self, contactdict):
        conrel = ContactRelation()

        if '_contact' in contactdict.keys():
            conrel.contact = contactdict['_contact']
        else:
            conrel.contact = False

        contacttype = ContactType()
        if '_contacttype' in contactdict.keys() and contactdict['_contacttype'] is not None:
            contacttype.__dict__.update(contactdict['_contacttype'])
            conrel.contacttype = contacttype

        manner = MannerRelation()
        if '_manner' in contactdict.keys() and contactdict['_manner'] is not None:
            manner.__dict__.update(contactdict['_manner'])
            conrel.manner = manner

        distances = [
            Distance(Direction.HORIZONTAL),
            Distance(Direction.VERTICAL),
            Distance(Direction.SAGITTAL),
            Distance(Direction.GENERIC)
        ]
        if '_distances' in contactdict.keys() and contactdict['_distances'] is not None:
            for dist in contactdict['_distances']:
                distances_idx = 0 if dist['_axis'] == Direction.HORIZONTAL \
                    else (1 if dist['_axis'] == Direction.VERTICAL
                          else (2 if dist['_axis'] == Direction.SAGITTAL else 3))
                distances[distances_idx].__dict__.update(dist)
        conrel.distances = distances

        return conrel

    def read_directions(self, dirlist):
        directions = [
            Direction(axis=Direction.HORIZONTAL),
            Direction(axis=Direction.VERTICAL),
            Direction(axis=Direction.SAGITTAL),
        ]
        for dirn in dirlist:
            directions_idx = 0 if dirn['_axis'] == Direction.HORIZONTAL else (1 if dirn['_axis'] == Direction.VERTICAL else 2)
            directions[directions_idx].__dict__.update(dirn)
        return directions

    def read_locmod(self, uid, locdict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(locdict)

        # location-specific attributes
        ltree = LocationTreeModel(jsondict=locdict['locationtree'])
        inphase = locdict.pop('inphase', 0)

        lmod = LocationModule(ltree, articulators, timingintervals=timingintervals,
                              phonlocs=phonlocs, addedinfo=addedinfo, inphase=inphase)
        lmod.uniqueid = uid
        return lmod

    def read_movmod(self, uid, movdict):
        # attributes common to all parameter modules
        articulators, timingintervals, phonlocs, addedinfo = self.read_parameter_module(movdict)

        # movement-specific attributes
        mtreeser = MovementTreeSerializable(infodicts=movdict['movementtree'])  # includes addedinfos for individual movement items
        mtree = MovementTreeModel(serializedmvmttree=mtreeser)
        inphase = movdict.pop('inphase', 0)

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
        specslist = []
        addedinfo = AddedInfo()

        if typedict is not None:
            if '_specslist' in typedict.keys() and typedict['_specslist'] is not None:
                specslist = [spec for spec in typedict['_specslist']]
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


# wizard page that asks the user to choose a source (exported) file to import
class ImportSourceSelectionWizardPage(QWizardPage):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Select the file to import: JSON (.txt) is currently the only importable format."))
        # TODO pagelayout.addWidget(QLabel("Select the file to import:\nJSON (.txt) is currently the only importable format."))

        selectionlayout = QHBoxLayout()
        self.importsourcedisplay = QLineEdit()
        self.importsourcedisplay.setReadOnly(True)
        self.registerField("importsourcepath", self.importsourcedisplay)
        choosefilebutton = QPushButton("Browse")
        choosefilebutton.clicked.connect(self.handle_select_source)
        selectionlayout.addWidget(self.importsourcedisplay)
        selectionlayout.addWidget(choosefilebutton)

        pagelayout.addLayout(selectionlayout)
        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.field("importsourcepath")) > 0

    # presents the user a standard file selection dialog to choose which file to import
    def handle_select_source(self):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           self.tr('Select file to import'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('JSON file (*.txt)'))
        if file_name:
            self.importsourcedisplay.setText(file_name)
            self.completeChanged.emit()


# wizard page that asks the user to choose a destination file to which to save the imported (source) file
class ImportDestinationSelectionWizardPage(QWizardPage):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        pagelayout = QVBoxLayout()

        pagelayout.addWidget(QLabel("Choose the name and location to save the corpus file generated from the import."))

        selectionlayout = QHBoxLayout()
        self.importdestdisplay = QLineEdit()
        self.importdestdisplay.setReadOnly(True)
        self.registerField("importdestpath", self.importdestdisplay)
        choosefilebutton = QPushButton("Browse")
        choosefilebutton.clicked.connect(self.handle_select_dest)
        selectionlayout.addWidget(self.importdestdisplay)
        selectionlayout.addWidget(choosefilebutton)

        pagelayout.addLayout(selectionlayout)
        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return len(self.field("importdestpath")) > 0

    # presents the user a standard file selection dialog to choose which file to import
    def handle_select_dest(self):
        importsourcefilename = os.path.split(str(self.field("importsourcepath")))[1]
        suggesteddestfilename = importsourcefilename.replace(".txt", "_imported.slpaa")
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select import destination'),
                                                           # complains if dest already exists
                                                           os.path.join(self.app_settings['storage']['recent_folder'], suggesteddestfilename),
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_name:
            self.importdestdisplay.setText(file_name)
            self.completeChanged.emit()


# wizard page that asks the user to decide whether they want the 'last modified' timestamps from the originally-exported signs,
# or if new ones should be generated now
class TimestampSelectionWizardPage(QWizardPage):
    timestampselected = pyqtSignal(bool)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.keeporigtimestamps = None

        pagelayout = QVBoxLayout()
        pagelayout.addWidget(QLabel("Select which option you prefer for the 'last modified' timestamp on each sign."))
        self.timestampswitch = OptionSwitch("Keep original values\nas per exported file", "Reset to now")
        self.timestampswitch.toggled.connect(self.handle_timestampswitch_toggled)
        pagelayout.addWidget(self.timestampswitch)

        self.setLayout(pagelayout)

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return self.keeporigtimestamps is not None

    def handle_timestampswitch_toggled(self, switchvalue):
        self.keeporigtimestamps = switchvalue[1]
        self.completeChanged.emit()
        self.timestampselected.emit(self.keeporigtimestamps)


# wizard page that allows the user to finally confirm importing the corpus
# it also shows a status display
class ImportCorpusWizardPage(QWizardPage):
    importcorpus = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.importattempted = False
        pagelayout = QVBoxLayout()

        importlayout = QHBoxLayout()
        importlayout.addWidget(QLabel("Import JSON to new .slpaa file."))
        importcorpusbutton = QPushButton("Import corpus")
        importcorpusbutton.clicked.connect(self.handle_import_corpus)
        importlayout.addWidget(importcorpusbutton)
        pagelayout.addLayout(importlayout)

        statuslayout = QHBoxLayout()
        statuslabel = QLabel("Status of import:")
        statuslayout.addWidget(statuslabel)
        statuslayout.setAlignment(statuslabel, Qt.AlignTop)
        self.statusdisplay = StatusDisplay("not yet attempted")
        statuslayout.addWidget(self.statusdisplay)
        pagelayout.addLayout(statuslayout)

        self.setLayout(pagelayout)

    # signals to the parent (wizard) to try importing the corpus
    def handle_import_corpus(self, checked):
        self.importcorpus.emit()
        self.importattempted = True
        self.completeChanged.emit()

    # determines whether the "next" (or "finish") button should be enabled on this page
    def isComplete(self):
        return self.importattempted
