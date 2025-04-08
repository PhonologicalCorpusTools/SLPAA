from copy import copy
import io
import pickle

from PyQt5.QtCore import Qt

from lexicon.module_classes import PhonLocations, AddedInfo, LocationType
from models.movement_models import fx
from constant import HAND, userdefinedroles as udr
import logging

class ParameterModuleSerializable:

    def __init__(self, parammod):
        self._articulators = parammod.articulators
        self._timingintervals = parammod.timingintervals
        self._addedinfo = parammod.addedinfo
        self._phonlocs = parammod.phonlocs

    @property
    def phonlocs(self):
        if not hasattr(self, '_phonlocs'):
            # for backward compatibility with pre-20240723 parameter modules
            self._phonlocs = PhonLocations()
        return self._phonlocs

    @phonlocs.setter
    def phonlocs(self, phonlocs):
        self._phonlocs = phonlocs

    @property
    def addedinfo(self):
        if not hasattr(self, '_addedinfo'):
            # for backward compatibility with pre-20230208 parameter modules
            self._addedinfo = AddedInfo()
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo

    @property
    def timingintervals(self):
        if not hasattr(self, '_timingintervals'):
            # TODO remove? for backward compatibility with pre-20250325 parameter modules
            self._timingintervals = []
            if 'timingintervals' in self.__dict__.keys():
                self._timingintervals = self.__dict__.pop('timingintervals')
        return self._timingintervals

    @timingintervals.setter
    def timingintervals(self, timingintervals):
        self._timingintervals = timingintervals

    @property
    def articulators(self):
        if not hasattr(self, '_articulators'):
            # backward compatibility pre-20230804 addition of arms and legs as articulators (issues #175 and #176)
            articulator_dict = {1: False, 2: False}
            if hasattr(self, '_hands') or hasattr(self, 'hands'):
                articulator_dict[1] = self.hands['H1']
                articulator_dict[2] = self.hands['H2']
                # for backward compatibility with pre-20250325 parameter modules
                del self._hands
            self._articulators = (HAND, articulator_dict)
        return self._articulators

    @articulators.setter
    def articulators(self, articulators):
        self._articulators = articulators


# This class is a serializable form of the class LocationTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class LocationModuleSerializable(ParameterModuleSerializable):

    def __init__(self, locnmodule):
        super().__init__(locnmodule)

        # creates a full serializable copy of the location module, eg for saving to disk
        self._inphase = locnmodule.inphase
        self.locationtree = LocationTreeSerializable(locnmodule.locationtreemodel)

    @property
    def inphase(self):
        if not hasattr(self, '_inphase'):
            # for backward compatibility with pre-20230410 location modules
            self._inphase = 0
        return self._inphase

    @inphase.setter
    def inphase(self, inphase):
        self._inphase = inphase


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
        self._inphase = mvmtmodule.inphase
        self.movementtree = MovementTreeSerializable(mvmtmodule.movementtreemodel)

    @property
    def inphase(self):
        if (not hasattr(self, '_inphase')) or (self._inphase is None):
            # for backward compatibility with pre-20230410 movement modules
            self._inphase = 0
        return self._inphase

    @inphase.setter
    def inphase(self, inphase):
        self._inphase = inphase


# This class is a serializable form of the class MovementTreeModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class MovementTreeSerializable:

    def __init__(self, mvmttreemodel=None, infodicts=None):

        self.numvals = {}  # deprecated
        self.stringvals = {}  # deprecated
        self.checkstates = {}
        self.addedinfos = {}
        self.userspecifiedvalues = {}

        if mvmttreemodel is None and infodicts is not None:
            # just import the dicts directly-- not from an existing MovementTreeModel
            self.__dict__.update(infodicts)

        else:
            # creates a full serializable copy of the movement tree, eg for saving to disk
            treenode = mvmttreemodel.invisibleRootItem()
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

    def __init__(self, locntreemodel=None, infodicts=None):

        self.numvals = {}  # deprecated
        self.checkstates = {}
        self.detailstables = {}
        self.addedinfos = {}
        self.locationtype = None
        self.multiple_selection_allowed = False
        self.nodes_are_terminal = False
        self.defaultneutralselected = False
        self.defaultneutrallist = None

        if locntreemodel is None and infodicts is not None:
            # just import the dicts directly-- not from an existing LocationTreeModel
            loctypedict = infodicts.pop('locationtype', {})
            self.locationtype = LocationType()
            self.locationtype.__dict__.update(loctypedict)

            detailstables = infodicts.pop('detailstables', {})
            for k, v in detailstables.items():
                self.detailstables[k] = LocationTableSerializable(infodict=v)

            addedinfos = infodicts.pop('addedinfos', {})
            for k, v in addedinfos.items():
                addedinfo = AddedInfo()
                addedinfo.__dict__.update(v)
                self.addedinfos[k] = addedinfo

            self.__dict__.update(infodicts)  #  = deep_update_pydantic(self.__dict__, infodicts)

        else:
            # creates a full serializable copy of the location tree, eg for saving to disk
            treenode = locntreemodel.invisibleRootItem()
            self.collectdatafromLocationTreeModel(treenode)
            self.locationtype = copy(locntreemodel.locationtype)
            self.multiple_selection_allowed = locntreemodel.multiple_selection_allowed
            self.nodes_are_terminal = locntreemodel.nodes_are_terminal
            self.defaultneutralselected = locntreemodel.defaultneutralselected
            self.defaultneutrallist = locntreemodel.defaultneutrallist

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
                    iseditable = treechild.data(Qt.UserRole + udr.isuserspecifiablerole) != fx
                    userspecifiedvalue = treechild.data(Qt.UserRole + udr.userspecifiedvaluerole)
                    # if iseditable:
                    #     self.userspecifiedvalues[pathtext] = userspecifiedvalue

                self.collectdatafromLocationTreeModel(treechild)


# This class is a serializable form of the class LocationTableModel, which is itself not pickleable.
# Rather than being based on QAbstractTableModel, this one uses the underlying lists from the
# LocationTableModel to convert to and from saveable form.
class LocationTableSerializable:

    def __init__(self, locntablemodel=None, infodict=None):
        self.col_labels = ["", ""]
        self.col_contents = [[], []]

        if locntablemodel is None and infodict is not None:
            # just import the dicts directly-- not from an existing LocationTableModel
            if 'col_labels' in infodict.keys():
                self.col_labels = infodict['col_labels']
            if 'col_contents' in infodict.keys():
                self.col_contents = infodict['col_contents']
        else:
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


# copied instead of imported, to avoid yet another package requirement for RAs
# from https://github.com/pydantic/pydantic/blob/fd2991fe6a73819b48c906e3c3274e8e47d0f761/pydantic/utils.py#L200
# TODO consider actually importing the package once RAs have switched to using the executable
# from pydantic.utils import deep_update
def deep_update_pydantic(mapping, updating_mappings):
    updated_mapping = mapping.copy()
    # for updating_mapping in updating_mappings.items():  # I added .items()
    for k, v in updating_mappings.items():  # I added the s at the end of updated_mapping
        if k in updated_mapping and isinstance(updated_mapping[k], dict) and isinstance(v, dict):
            updated_mapping[k] = deep_update_pydantic(updated_mapping[k], v)
        else:
            updated_mapping[k] = v
    return updated_mapping
