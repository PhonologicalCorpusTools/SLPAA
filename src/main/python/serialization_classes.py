from copy import copy
import io
import pickle


from PyQt5.QtCore import (
    Qt
)

from lexicon.module_classes import userdefinedroles as udr
from models.movement_models import fx
from constant import HAND


class ParameterModuleSerializable:

    def __init__(self, parammod):
        self._articulators = parammod.articulators
        self.timingintervals = parammod.timingintervals
        self.addedinfo = parammod.addedinfo

    @property
    def articulators(self):
        if not hasattr(self, '_articulators'):
            # backward compatibility pre-20230804 addition of arms and legs as articulators (issues #175 and #176)
            articulator_dict = {1: False, 2: False}
            if hasattr(self, 'hands'):
                articulator_dict[1] = self.hands['H1']
                articulator_dict[2] = self.hands['H2']
            self._articulators = (HAND, articulator_dict)
        return self._articulators

    @articulators.setter
    def articulators(self, articulators):
        # TODO KV - validate?
        self._articulators = articulators


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


# This class is a serializable form of the class RelationModule, which is itself not pickleable.
# Rather than being based on ParameterModule, this one uses dictionary structures to convert to
# and from saveable form.
class RelationModuleSerializable(ParameterModuleSerializable):

    def __init__(self, relmodule):
        super().__init__(relmodule)

        # creates a full serializable copy of the relation module, eg for saving to disk
        self.relationx = relmodule.relationx
        self.relationy = relmodule.relationy
        self.bodyparts_dict = {}
        for bodypart in relmodule.bodyparts_dict.keys():
            if bodypart not in self.bodyparts_dict.keys():
                self.bodyparts_dict[bodypart] = {}
            for n in relmodule.bodyparts_dict[bodypart].keys():
                self.bodyparts_dict[bodypart][n] = BodypartInfoSerializable(relmodule.bodyparts_dict[bodypart][n])
        self.contactrel = relmodule.contactrel
        self.xy_crossed = relmodule.xy_crossed
        self.xy_linked = relmodule.xy_linked
        self.directions = relmodule.directions


# This class is a serializable form of the class MovementModule, which is itself not pickleable
# due to its component MovementTreeModel.
class MovementModuleSerializable(ParameterModuleSerializable):

    def __init__(self, mvmtmodule):
        super().__init__(mvmtmodule)

        # creates a full serializable copy of the movement module, eg for saving to disk
        self.inphase = mvmtmodule.inphase
        self.movementtree = MovementTreeSerializable(mvmtmodule.movementtreemodel)


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


# This class is a serializable form of the class BodypartInfo, which is itself not pickleable.
# Rather than being based on a QStandardItemModel tree, this one uses dictionary structures to
# convert to and from saveable form.
class BodypartInfoSerializable:

    def __init__(self, bodypartinfo):
        # creates a full serializable copy of the bodypartinfo, eg for saving to disk
        self.addedinfo = bodypartinfo.addedinfo
        if bodypartinfo.bodyparttreemodel is not None:
            self.bodyparttree = LocationTreeSerializable(bodypartinfo.bodyparttreemodel)
        else:
            self.bodyparttree = None


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
        elif class_orig in ["LocationTreeSerializable", "LocationModuleSerializable", "LocationTableSerializable"] and module_orig in ["gui.location_view", "serialization.serialization_classes"]:
            module_updated = "serialization_classes"
        elif class_orig in ["ParameterModuleSerializable"] and module_orig in ["gui.location_view", "serialization.serialization_classes"]:
            module_updated = "serialization_classes"
        elif class_orig in ["MovementTreeSerializable", "MovementModuleSerializable"] and module_orig in ["gui.movement_view", "serialization.serialization_classes"]:
            module_updated = "serialization_classes"
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
        elif class_orig in ["ParameterModule", "OrientationModule", "LocationModule", "MovementModule", "HandConfigurationModule", "PhonLocations", "LocationType"] and module_orig == "lexicon.module_classes":
            # no change as of 20230510
            pass
        elif class_orig in ["TimingPoint", "TimingInterval", "AddedInfo"] and module_orig == "lexicon.module_classes2":
            module_updated = "lexicon.module_classes"
        # elif class_orig in ["BodypartSpecificationPanel", "BodypartSelectorDialog"] and module_orig == "gui.handpartspecification_dialog":
        #     module_updated = "gui.bodypartspecification_dialog"

        return super(RenameUnpickler, self).find_class(module_updated, class_updated)


def renamed_load(file_obj):
    return RenameUnpickler(file_obj).load()


def renamed_loads(pickled_bytes):
    file_obj = io.BytesIO(pickled_bytes)
    return renamed_load(file_obj)