from copy import deepcopy

from lexicon.lexicon_classes import unserializemovementmodules, unserializelocationmodules, unserializerelationmodules
from constant import ModuleTypes
from serialization_classes import MovementModuleSerializable, LocationModuleSerializable, RelationModuleSerializable


# module is either of type ParameterModule (or one of its children: MovementModule, OrientationModule, etc)
#   OR of type SignType
def deepcopymodule(module_orig):
    moduletype = module_orig.moduletype
    uid = module_orig.uniqueid
    module_copy = None

    if moduletype == ModuleTypes.MOVEMENT:
        serialdict = {uid:MovementModuleSerializable(module_orig)}
        module_copy = unserializemovementmodules(serialdict)[uid]
    elif moduletype == ModuleTypes.LOCATION:
        serialdict = {uid:LocationModuleSerializable(module_orig)}
        locmods_copied, _ = unserializelocationmodules(serialdict)
        module_copy = locmods_copied[uid]
    elif moduletype == ModuleTypes.RELATION:
        serialdict = {uid:RelationModuleSerializable(module_orig)}
        module_copy = unserializerelationmodules(serialdict)[uid]
    elif moduletype in [ModuleTypes.HANDCONFIG, ModuleTypes.ORIENTATION, ModuleTypes.NONMANUAL]:
        module_copy = deepcopy(module_orig)

    # create a new unique ID for the copied module
    module_copy.uniqueid_reset()
    return module_copy

