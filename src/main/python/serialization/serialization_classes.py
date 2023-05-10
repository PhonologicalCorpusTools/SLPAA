from copy import copy
import io
import pickle


from PyQt5.QtCore import (
    Qt
)

from lexicon.module_classes import userdefinedroles as udr

from models.movement_models import fx



# TODO KV implement this base class; refactor children (eg LocationModuleSerializable) to inherit as much as possible
# TODO KV this class definition should be somewhere more general (ie, it's not just for location-related stuff)
class ParameterModuleSerializable:

    def __init__(self, parammod):
        self.hands = parammod.hands
        self.timingintervals = parammod.timingintervals
        self.addedinfo = parammod.addedinfo


# This class is a serializable form of the class LocationTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class LocationModuleSerializable(ParameterModuleSerializable):

    def __init__(self, locnmodule):
        super().__init__(locnmodule)

        # creates a full serializable copy of the location module, eg for saving to disk
        self.inphase = locnmodule.inphase
        self.phonlocs = locnmodule.phonlocs
        self.locationtree = LocationTreeSerializable(locnmodule.locationtreemodel)


# This class is a serializable form of the class MovementModule, which is itself not pickleable
# due to its component MovementTreeModel.
class MovementModuleSerializable(ParameterModuleSerializable):

    def __init__(self, mvmtmodule):
        super().__init__(mvmtmodule)

        # creates a full serializable copy of the movement module, eg for saving to disk
        self.inphase = mvmtmodule.inphase
        self.movementtree = MovementTreeSerializable(mvmtmodule.movementtreemodel)
    #
    # def getMovementTreeModel(self):
    #     mvmttreemodel = MovementTreeModel()
    #     rootnode = mvmttreemodel.invisibleRootItem()
    #     mvmttreemodel.populate(rootnode)
    #     makelistmodel = mvmttreemodel.listmodel
    #     self.setvalues(rootnode)
    #     return mvmttreemodel


# This class is a serializable form of the class MovementTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class MovementTreeSerializable:

    def __init__(self, mvmttreemodel):

        # creates a full serializable copy of the movement tree, eg for saving to disk
        treenode = mvmttreemodel.invisibleRootItem()

        self.numvals = {}  # deprecated
        self.stringvals = {}  # deprecated
        self.checkstates = {}
        self.addedinfos = {}
        self.userspecifiedvalues = {}

        self.collectdatafromMovementTreeModel(treenode)

    def collectdatafromMovementTreeModel(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    checkstate = treechild.checkState()
                    addedinfo = treechild.addedinfo
                    self.addedinfos[pathtext] = copy(addedinfo)
                    iseditable = treechild.data(Qt.UserRole + udr.isuserspecifiablerole) != fx
                    userspecifiedvalue = treechild.data(Qt.UserRole + udr.userspecifiedvaluerole)
                    if iseditable:
                        self.userspecifiedvalues[pathtext] = userspecifiedvalue

                    self.checkstates[pathtext] = checkstate
                self.collectdatafromMovementTreeModel(treechild)

    # def getMovementTreeModel(self):
    #     mvmttreemodel = MovementTreeModel()
    #     rootnode = mvmttreemodel.invisibleRootItem()
    #     mvmttreemodel.populate(rootnode)
    #     makelistmodel = mvmttreemodel.listmodel  # TODO KV   what is this? necessary?
    #     self.backwardcompatibility()
    #     self.setvaluesinMovementTreeModel(rootnode)
    #     return mvmttreemodel
    #
    # def backwardcompatibility(self):
    #     hadtoaddusv = False
    #     if not hasattr(self, 'userspecifiedvalues'):
    #         self.userspecifiedvalues = {}
    #         hadtoaddusv = True
    #     for stored_dict in [self.checkstates, self.addedinfos]:  # self.numvals, self.stringvals,
    #         pairstoadd = {}
    #         keystoremove = []
    #         for k in stored_dict.keys():
    #
    #             # 1. "H1 and H2 move in different directions" (under either axis driectin or plane, in perceptual shape)
    #             #   --> "H1 and H2 move in opposite directions"
    #             # 2. Then later... "H1 and H2 move in opposite directions" (under axis direction only)
    #             #   --> "H1 and H2 move toward each other" (along with an independent addition of "... away ...")
    #             if "H1 and H2 move in different directions" in k:
    #                 if "Axis direction" in k:
    #                     pairstoadd[k.replace("in different directions", "toward each other")] = stored_dict[k]
    #                     keystoremove.append(k)
    #                 elif "Place" in k:
    #                     pairstoadd[k.replace("different", "opposite")] = stored_dict[k]
    #                     keystoremove.append(k)
    #             elif "H1 and H2 move in opposite directions" in k and "Axis direction" in k:
    #                 pairstoadd[k.replace("in opposite directions", "toward each other")] = stored_dict[k]
    #                 keystoremove.append(k)
    #
    #             if hadtoaddusv:
    #
    #                 if k.endswith(specifytotalcycles_str) or k.endswith(numberofreps_str):
    #                     pairstoadd[k.replace(numberofreps_str, specifytotalcycles_str)] = stored_dict[k]
    #                     keystoremove.append(k)
    #
    #                 elif "This number is a minimum" in k:
    #                     pairstoadd[k.replace(delimiter + "#" + delimiter, delimiter)] = stored_dict[k]
    #                     keystoremove.append(k)
    #
    #                 elif (specifytotalcycles_str + delimiter in k or numberofreps_str + delimiter in k):
    #                     # then we're looking at the item that stores info about the specified number of repetitions
    #                     newkey = k.replace(numberofreps_str, specifytotalcycles_str)
    #                     newkey = newkey[:newkey.index(specifytotalcycles_str+delimiter) + len(specifytotalcycles_str)]
    #                     remainingtext = ""
    #                     if specifytotalcycles_str in k:
    #                         remainingtext = k[k.index(specifytotalcycles_str + delimiter) + len(specifytotalcycles_str + delimiter):]
    #                     elif numberofreps_str in k:
    #                         remainingtext = k[k.index(specifytotalcycles_str + delimiter) + len(numberofreps_str + delimiter):]
    #
    #                     if len(remainingtext) > 0 and delimiter not in remainingtext and remainingtext != "#":
    #                         numcycles = remainingtext
    #                         self.userspecifiedvalues[newkey] = numcycles
    #
    #         for oldkey in keystoremove:
    #             stored_dict.pop(oldkey)
    #
    #         for newkey in pairstoadd.keys():
    #             stored_dict[newkey] = pairstoadd[newkey]
    #
    # def setvaluesinMovementTreeModel(self, treenode):
    #     if treenode is not None:
    #         for r in range(treenode.rowCount()):
    #             treechild = treenode.child(r, 0)
    #             if treechild is not None:
    #                 pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
    #                 if pathtext in self.checkstates.keys():
    #                     treechild.setCheckState(self.checkstates[pathtext])
    #
    #                 if pathtext in self.addedinfos.keys():
    #                     treechild.addedinfo = copy(self.addedinfos[pathtext])
    #
    #                 if pathtext in self.userspecifiedvalues.keys():
    #                     # this also updates the associated list item as well as its display
    #                     treechild.setData(self.userspecifiedvalues[pathtext], Qt.UserRole + udr.userspecifiedvaluerole)
    #                     treechild.editablepart().setText(self.userspecifiedvalues[pathtext])
    #
    #                 self.setvaluesinMovementTreeModel(treechild)



# This class is a serializable form of the class LocationTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class LocationTreeSerializable:

    def __init__(self, locntreemodel):

        # creates a full serializable copy of the location tree, eg for saving to disk
        treenode = locntreemodel.invisibleRootItem()

        self.numvals = {}  # deprecated
        self.checkstates = {}
        self.detailstables = {}
        self.addedinfos = {}

        self.collectdatafromLocationTreeModel(treenode)

        self.locationtype = copy(locntreemodel.locationtype)

    # collect data from the LocationTreeModel to store in this LocationTreeSerializable
    def collectdatafromLocationTreeModel(self, treenode):
        if treenode is not None:
            for r in range(treenode.rowCount()):
                treechild = treenode.child(r, 0)
                if treechild is not None:
                    pathtext = treechild.data(Qt.UserRole + udr.pathdisplayrole)
                    checkstate = treechild.checkState()
                    locntable = treechild.detailstable
                    addedinfo = treechild.addedinfo
                    self.addedinfos[pathtext] = copy(addedinfo)
                    self.detailstables[pathtext] = LocationTableSerializable(locntable)
                    self.checkstates[pathtext] = checkstate
                    # editable = treechild.isEditable()  # TODO KV do this the same way as movement tree
                    # if editable:
                    #     pathsteps = pathtext.split(delimiter)
                    #     parentpathtext = delimiter.join(pathsteps[:-1])
                    #     numericstring = pathsteps[-1]  # pathtext[lastdelimindex + 1:]
                    #     self.numvals[parentpathtext] = numericstring
                    iseditable = treechild.data(Qt.UserRole + udr.isuserspecifiablerole) != fx
                    userspecifiedvalue = treechild.data(Qt.UserRole + udr.userspecifiedvaluerole)
                    # if iseditable:
                    #     self.userspecifiedvalues[pathtext] = userspecifiedvalue

                self.collectdatafromLocationTreeModel(treechild)
    #
    # # create, populate, and return a LocationTreeModel based on the values stored in this LocationTreeSerializable
    # def getLocationTreeModel(self):
    #     locntreemodel = LocationTreeModel()
    #     locntreemodel.locationtype = self.locationtype
    #     rootnode = locntreemodel.invisibleRootItem()
    #     locntreemodel.populate(rootnode)
    #     makelistmodel = locntreemodel.listmodel  # TODO KV   what is this? necessary?
    #     self.backwardcompatibility()
    #     self.setvaluesinLocationTreeModel(rootnode)
    #     return locntreemodel
    #
    # # ensure that any info stored in this LocationTreeSerializable under older keys (paths),
    # # is updated to reflect the newer text for those outdated keys
    # def backwardcompatibility(self):
    #     # hadtoaddusv = False
    #     # if not hasattr(self, 'userspecifiedvalues'):
    #     #     self.userspecifiedvalues = {}
    #     #     hadtoaddusv = True
    #     for stored_dict in [self.checkstates, self.addedinfos, self.detailstables]:  # self.numvals, self.stringvals,
    #         pairstoadd = {}
    #         keystoremove = []
    #         for k in stored_dict.keys():
    #             if "H1 is in front of H2" in k:
    #                 pairstoadd[k.replace("H1 is in front of H2", "H1 is more distal than H2")] = stored_dict[k]
    #                 keystoremove.append(k)
    #             if "H1 is behind H2" in k:
    #                 pairstoadd[k.replace("H1 is behind H2", "H1 is more proximal than H2")] = stored_dict[k]
    #                 keystoremove.append(k)
    #
    #         for oldkey in keystoremove:
    #             stored_dict.pop(oldkey)
    #
    #         for newkey in pairstoadd.keys():
    #             stored_dict[newkey] = pairstoadd[newkey]
    #
    # # take info stored in this LocationTreeSerializable and ensure it's reflected in the associated LocationTreeModel
    # def setvaluesinLocationTreeModel(self, treenode):
    #     if treenode is not None:
    #         for r in range(treenode.rowCount()):
    #             treechild = treenode.child(r, 0)
    #             if treechild is not None:
    #                 pathtext = treechild.data(Qt.UserRole+udr.pathdisplayrole)
    #                 # parentpathtext = treenode.data(Qt.UserRole+udr.pathdisplayrole)
    #                 # if parentpathtext in self.numvals.keys():
    #                 #     treechild.setText(self.numvals[parentpathtext])
    #                 #     treechild.setEditable(True)
    #                 #     pathtext = parentpathtext + delimiter + self.numvals[parentpathtext]
    #                 if pathtext in self.checkstates.keys():
    #                     treechild.setCheckState(self.checkstates[pathtext])
    #
    #                 if pathtext in self.addedinfos.keys():
    #                     treechild.addedinfo = copy(self.addedinfos[pathtext])
    #
    #                 if pathtext in self.detailstables.keys():
    #                     treechild.detailstable.updatefromserialtable(self.detailstables[pathtext])
    #
    #                 self.setvaluesinLocationTreeModel(treechild)


# This class is a serializable form of the class LocationTableModel, which is itself not pickleable.
# Rather than being based on QAbstractTableModel, this one uses the underlying lists from the
# LocationTableModel to convert to and from saveable form.
class LocationTableSerializable:

    def __init__(self, locntablemodel):
        # creates a full serializable copy of the location table, eg for saving to disk
        self.col_labels = locntablemodel.col_labels
        self.col_contents = locntablemodel.col_contents

    def isempty(self):
        labelsempty = self.col_labels == ["", ""]
        contentsempty = self.col_contents == [[], []]
        return labelsempty and contentsempty

    def __repr__(self):
        return '<LocationTableSerializable: ' + repr(self.col_labels) + ' / ' + repr(self.col_contents) + '>'


# for backward compatibility with package structure from pre- issue #69 (20230510)
class RenameUnpickler(pickle.Unpickler):
    def find_class(self, module_orig, class_orig):
        class_updated = class_orig
        module_updated = module_orig

        if class_orig in ["CorpusItem", "CorpusModel"] and module_orig == "gui.corpus_view":
            module_updated = "models.corpus_models"
        elif class_orig in ["HandConfigurationHand", "HandConfigurationField", "HandConfigurationSlot"] and module_orig == "gui.hand_configuration":
            module_updated = "lexicon.module_classes"
        elif class_orig in ["LocationTreeItem", "LocationTreeModel", "LocationTableModel", "LocationListItem", "LocationListModel"] and module_orig == "gui.location_view":
            module_updated = "models.location_models"
        elif class_orig in ["LocationTreeSerializable", "LocationModuleSerializable", "LocationTableSerializable"] and module_orig == "gui.location_view":
            module_updated = "serialization.serialization_classes"
        elif class_orig in ["ParameterModuleSerializable"] and module_orig == "gui.location_view":
            module_updated = "serialization.serialization_classes"
        elif class_orig in ["MovementTreeSerializable", "MovementModuleSerializable"] and module_orig == "gui.movement_view":
            module_updated = "serialization.serialization_classes"
        elif class_orig in ["MovementTreeItem", "MovementTreeModel", "MovementListItem", "MovementListModel"] and module_orig == "gui.movement_view":
            module_updated = "models.movement_models"
        elif class_orig in ["Signtype"] and module_orig == "gui.signtype_selector":
            module_updated = "lexicon.module_classes"
        elif class_orig in ["XslotStructure"] and module_orig == "gui.xslots_selector":
            module_updated = "lexicon.module_classes"
        elif class_orig in ["SignLevelInformation"] and module_orig == "lexicon.lexicon_classes":
            module_updated = "lexicon.module_classes"
        elif class_orig in ["LocationPoint", "LocationHand", "LocationTranscription"] and module_orig == "lexicon.lexicon_classes":
            # no change as of 20230510
            pass
        elif class_orig in ["Sign", "Corpus"] and module_orig == "lexicon.lexicon_classes":
            # no change as of 20230510
            pass
        elif class_orig in ["LocationParameter", "Locations"] and module_orig == "lexicon.location":
            # no change as of 20230510
            pass
        elif class_orig in ["ParameterModule", "TargetModule", "OrientationModule", "LocationModule", "MovementModule", "HandConfigurationModule", "PhonLocations", "LocationType"] and module_orig == "lexicon.module_classes":
            # no change as of 20230510
            pass
        elif class_orig in ["TimingPoint", "TimingInterval", "AddedInfo"] and module_orig == "lexicon.module_classes2":
            module_updated = "lexicon.module_classes"

        # if class_orig in ["SigntypeSpecificationWidget", "SigntypeButtonGroup", "SigntypeRadioButton", "SigntypeCheckBox", "SigntypeSelectorDialog"]:
        #     module_updated = "gui.signtypespecification_view"
        # elif class_orig in ["XslotsSpecificationWidget", "XslotSelectorDialog"]:
        #     module_updated = "gui.xslotspecification_view"
        # elif class_orig in ["XslotPointLabel", "XslotRect", "XslotRectButton", "XslotRectLinkingButton", "XslotEllipseModuleButton", "XslotRectModuleButton", "SignSummaryScene", "XSlotCheckbox", "XslotLinkScene"]:
        #     module_updated = "gui.xslot_graphics"
        # elif class_orig in ["SignLevelDateDisplay", "SignLevelInfoWidget", "SignlevelinfoSelectorDialog"]:
        #     module_updated = "gui.signlevelinfospecification_view"
        # elif class_orig in ["MovementTreeView", "MvmtTreeListView", "MvmtTreeItemDelegate", "MovementSpecificationWidget"]:
        #     module_updated = "gui.movementspecification_view"
        # elif class_orig in ["TreeSearchComboBox"] and module_orig == "gui.movement_view":
        #     module_updated = "gui.movementspecification_view"
        #     class_updated = "MvmtTreeSearchComboBox"
        # elif class_orig in ["TreeSearchComboBox"] and module_orig == "gui.location_view":
        #     module_updated = "gui.locationspecification_view"
        #     class_updated = "LocnTreeSearchComboBox"
        # elif class_orig in ["AddedInfoPushButton", "AddedInfoContextMenu", "AbstractLocationAction", "CheckNoteAction"]:
        #     module_updated = "gui.modulespecification_widgets"
        # elif class_orig in ["ModuleSelectorDialogNEW", "XslotLinkingWidget", "HandSelectionWidget"]:
        #     module_updated = "gui.modulespecification_dialog"
        # elif class_orig in ["LocationTreeView", "LocnTreeListView", "LocationGraphicsView", "LocationSvgView", "LocationTableView", "LocationSpecificationWidget", "LocationSelectionWidget", "ImageDisplayTab", "AxisTreeWidget", "LocationTreeItemDelegate"]:
        #     module_updated = "gui.locationspecification_view"
        # elif class_orig in ["SvgDisplayTab", "LocationGraphicsTestDialog"]:
        #     module_updated = "gui.locationgraphicstest_dialog"
        # elif class_orig in ["ConfigSlot", "ConfigField", "ConfigHand", "Config", "ForearmCheckBox", "HandConfigSpecificationWidget", "HandTranscriptionPanel", "HandIllustrationPanel"]:
        #     module_updated = "gui.handconfigspecification_view"
        # # elif class_orig in ["CorpusTitleEdit", "CorpusDisplay"]:
        # #     module_updated = "gui.corpus_view"
        # elif class_orig in ["CorpusItem", "CorpusModel", "CorpusSortProxyModel"]:
        #     module_updated = "models.corpus_models"
        # elif class_orig in ["CorpusItem", "CorpusModel", "CorpusSortProxyModel"]:
        #     module_updated = "models.corpus_models"
        # elif class_orig in ["LocationTreeModel", "LocationListModel", "LocationTableModel", "LocationListItem", "LocationPathsProxyModel", "LocationTreeItem"]:
        #     module_updated = "models.location_models"
        # elif class_orig in ["UserDefinedRoles", "ParameterModule", "SignLevelInformation", "MovementModule", "PhonLocations", "LocationType", "TimingPoint", "TimingInterval", "AddedInfo", "Signtype", "LocationModule", "HandConfigurationModule", "TargetModule", "OrientationModule", "HandConfigurationHand", "HandConfigurationField", "HandConfigurationSlot", "XslotStructure"]:
        #     module_updated = "lexicon.module_classes"
        # elif class_orig in ["mvmtOptionsDict", "MovementTreeItem", "MovementListItem", "MovementPathsProxyModel", "MovementListModel", "MovementTreeModel"]:
        #     module_updated = "models.movement_models"
        # elif class_orig in ["MovementTreeSerializable", "MovementModuleSerializable", "LocationTreeSerializable", "LocationTableSerializable", "LocationModuleSerializable", "ParameterModuleSerializable"]:
        #     module_updated = "serialization.serialization_classes"
        # elif class_orig in ["TreeListView"] and module_orig == "gui.movement_view":
        #     class_updated = "MvmtTreeListView"
        #     module_updated = "gui.movementspecification_view"
        # elif class_orig in ["TreeListView"] and module_orig == "gui.location_view":
        #     class_updated = "LocnTreeListView"
        #     module_updated = "gui.locationspecification_view"

        return super(RenameUnpickler, self).find_class(module_updated, class_updated)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)