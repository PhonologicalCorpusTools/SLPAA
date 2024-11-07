from copy import deepcopy

from lexicon.lexicon_classes import unserializemovementmodules, unserializelocationmodules, unserializerelationmodules, Sign, SignLevelInformation
from constant import ModuleTypes
from serialization_classes import MovementModuleSerializable, LocationModuleSerializable, RelationModuleSerializable


def deepcopysignlevelinfo(sli_orig):
    return SignLevelInformation(serializedsignlevelinfo=sli_orig.serialize(), parentsign=sli_orig.parentsign)


def deepcopysign(sign_orig):
    sign_copy = Sign()
    sign_copy.signlevel_information = deepcopysignlevelinfo(sign_orig.signlevel_information)
    sign_copy.signtype = deepcopy(sign_orig.signtype)
    sign_copy.xslotstructure = deepcopy(sign_orig.xslotstructure)
    sign_copy.specifiedxslots = deepcopy(sign_orig.specifiedxslots)

    uid_updates = {}
    # mtypes = ModuleTypes.parametertypes_relationfirst
    for mtype in ModuleTypes.parametertypes_relationfirst:
        for muid in sign_orig.getmoduledict(mtype).keys():
            sign_copy.getmoduledict(mtype)[muid] = deepcopymodule(sign_orig.getmoduledict(mtype)[muid])
            sign_copy.getmodulenumbersdict(mtype)[muid] = sign_orig.getmodulenumbersdict(mtype)[muid]
        uid_updates[mtype] = sign_copy.reIDmodules(mtype)

    # make sure any rel modules with associated mov or loc modules have their linked module IDs updated to the new version
    for relmod in sign_copy.relationmodules.values():
        if relmod.relationy.existingmodule:
            linked_type = relmod.relationy.linkedmoduletype
            if linked_type is not None:
                orig_anchor_uids = relmod.relationy.linkedmoduleids
                relmod.relationy.linkedmoduleids = [uid_updates[linked_type][a_uid] for a_uid in orig_anchor_uids]

    return sign_copy


# module is either of type ParameterModule (or one of its children: MovementModule, OrientationModule, etc)
def deepcopymodule(module_orig):
    moduletype = module_orig.moduletype
    uid = module_orig.uniqueid
    module_copy = None

    if moduletype == ModuleTypes.MOVEMENT:
        serialdict = {uid: MovementModuleSerializable(module_orig)}
        module_copy = unserializemovementmodules(serialdict)[uid]
    elif moduletype == ModuleTypes.LOCATION:
        serialdict = {uid: LocationModuleSerializable(module_orig)}
        locmods_copied, _ = unserializelocationmodules(serialdict)
        module_copy = locmods_copied[uid]
    elif moduletype == ModuleTypes.RELATION:
        serialdict = {uid: RelationModuleSerializable(module_orig)}
        module_copy = unserializerelationmodules(serialdict)[uid]
    elif moduletype in [ModuleTypes.HANDCONFIG, ModuleTypes.ORIENTATION, ModuleTypes.NONMANUAL]:
        module_copy = deepcopy(module_orig)

    # create a new unique ID for the copied module
    module_copy.uniqueid_reset()
    return module_copy

