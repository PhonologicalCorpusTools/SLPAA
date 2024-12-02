from copy import deepcopy

from lexicon.lexicon_classes import unserializemovementmodules, unserializelocationmodules, unserializerelationmodules, Sign, SignLevelInformation
from serialization_classes import MovementModuleSerializable, LocationModuleSerializable, RelationModuleSerializable
from constant import ModuleTypes, HAND, ARM, LEG, ARTICULATOR_ABBREVS, PREDEFINED_MAP
PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}

snums = [1, 2]

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


# TODO description
# return format - checked with Stanley 20241122: [(s1mod1,s2mod2),(s1mod2,s2mod1),(s1mod3,None)]
def alignmodules(sign1, sign2, moduletype):
    if moduletype == ModuleTypes.SIGNTYPE:
        return [(sign1.signtype, sign2.signtype)]
    else:
        modulesbysign = {
            1: list(sign1.getmoduledict(moduletype).values()),
            2: list(sign2.getmoduledict(moduletype).values())
        }
        signswiththismodule = whichsignshavemodulesoftype(modulesbysign)

        if signswiththismodule == [1]:
            # no need to try and align modules; this module type only exists in sign1
            return [(mod, None) for mod in modulesbysign[1]]
        elif signswiththismodule == [2]:
            # no need to try and align modules; this module type only exists in sign2
            return [(None, mod) for mod in modulesbysign[2]]
        elif signswiththismodule == []:
            # no need to try and align modules; this module type isn't used in sign1 or sign2
            return []
        # else signswiththismodule == [1, 2]
        # try to align them; continue below

        # now we are at the point where we know that the module type in questions exists in both sign1 and sign2;
        #   we have to decide how to align them
        if moduletype == ModuleTypes.MOVEMENT:
            # i. First 'align by hand.' That is, try to align hand1 modules from sign1 to hand1 modules from sign2.
            #   If sign1 and sign2 each have only hand1 modules, or each have only hand2 modules, then proceed to the next step of alignment.
            #   If sign1 has both hand1 and hand2 modules, while sign2 has only hand1 modules (or vice versa), then align the hand1 modules only,
            #   and leave all hand2 modules unmatched.
            #   If sign1 has only hand1 modules, and sign2 has only hand2 modules, then this is the only time that non-matching hand modules can be aligned.
            modsalignedbyhand, unmatched = alignbyhand(modulesbysign)
            # ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
            #   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
            #   while sign 2 has only joint-specific movement, align the two joint-specific movements,
            #   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
            #   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
            #   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
            #   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
            #   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
            modsalignedbymovtype, unmatched = alignbymovementtype(unmatched)
            #   If modules still can't be aligned, align by coding order.
            modsalignedbycodingorder, _ = alignbycodingorder(unmatched, matchwithnone=True)
        elif moduletype == ModuleTypes.LOCATION:
            # i. First ‘align by hand’ as for the movement module.
            modsalignedbyhand, unmatched = alignbyhand(modulesbysign)
            # ii. After aligning by hand, try to align by general location type (body-anchored or signing space)
            #   -- e.g., if sign1 has both body-anchored and signing space locations, and sign2 has only a body-anchored location,
            #   then align the body-anchored modules and leave the signing-space module unmatched.
            #   If there are multiple locations of the same type (e.g., multiple body-anchored locations),
            #   use the uppermost (in the tree) location specifications to align
            #   (e.g., align two head-locations rather than a head location with a torso location, if possible).
            modsalignedbyloctype, unmatched = alignbylocationtype(unmatched)
            #   If modules still can't be aligned, align by coding order.
            modsalignedbycodingorder, _ = alignbycodingorder(unmatched, matchwithnone=True)
            return modsalignedbyhand + modsalignedbyloctype + modsalignedbycodingorder
        elif moduletype == ModuleTypes.ORIENTATION:
            # i. First ‘align by hand’ as for the movement module.
            modsalignedbyhand, unmatched = alignbyhand(modulesbysign)
            # ii. After aligning by hand, align by palm orientation if possible (e.g. align two palm-up modules).
            modsalignedbypalm, unmatched = alignbypalmori(unmatched)
            #   If not possible, align by finger root direction.
            modsalignedbyfingerroot, unmatched = alignbyfingerrootdir(unmatched)
            #   If still not possible, align by coding order.
            modsalignedbycodingorder, _ = alignbycodingorder(unmatched, matchwithnone=True)
            return modsalignedbyhand + modsalignedbypalm + modsalignedbyfingerroot + modsalignedbycodingorder
        elif moduletype == ModuleTypes.HANDCONFIG:
            pass  # TODO
            # i. First ‘align by hand’ as for the movement module.
            modsalignedbyhand, unmatched = alignbyhand(modulesbysign)
            # ii. After aligning by hand, align by handshape name if possible (e.g. align two '5' handshapes).
            modsalignedbyhs, unmatched = alignbyhandshapename(unmatched)
            #   If not possible, align by coding order.
            modsalignedbycodingorder, _ = alignbycodingorder(unmatched, matchwithnone=True)
            return modsalignedbyhand + modsalignedbyhs + modsalignedbycodingorder
            #   [NB: this one might eventually need to get refined.]
        elif moduletype == ModuleTypes.RELATION:
            # TODO - waiting for further intructions from Kathleen
            modsalignedbycodingorder, _ = alignbycodingorder(modulesbysign, matchwithnone=True)
            return modsalignedbycodingorder
        elif moduletype == ModuleTypes.NONMANUAL:
            # TODO - waiting for further intructions from Kathleen
            modsalignedbycodingorder, _ = alignbycodingorder(modulesbysign, matchwithnone=True)
            return modsalignedbycodingorder


def alignbypalmori(orimodsbysign):
    return alignbyori_helper(orimodsbysign, focus='palm', level='specific')


def alignbyfingerrootdir(orimodsbysign):
    return alignbyori_helper(orimodsbysign, focus='root', level='specific')


# try to match as specifically as possible (eg vertical/up with vertical/up)
# any leftovers, try to match at least to the general direction (eg vertical/up with vertical/down or just vertical)
# any leftovers, punt back up to next step
def alignbyori_helper(orimodsbysign, focus, level='specific'):
    sign1mods = [mod for mod in orimodsbysign[1]]
    sign2mods = [mod for mod in orimodsbysign[2]]

    matchedmods = []

    index1 = 0
    while index1 < len(sign1mods):
        mod1 = sign1mods[index1]
        mod1focus = mod1.palm if focus == 'palm' else mod1.root

        index2 = 0
        while index2 < len(sign2mods):
            mod2 = sign2mods[index2]
            mod2focus = mod2.palm if focus == 'palm' else mod2.root

            if directionsmatch(mod1focus, mod2focus, level=level):
                    matchedmods.append((mod1, mod2))
                    sign1mods.remove(mod1)
                    sign2mods.remove(mod2)

            index2 += 1
        index1 += 1

    unmatchedmods = {1: sign1mods, 2: sign2mods}
    if level == 'specific':
        morematchedmods, unmatchedmods = alignbyori_helper(unmatchedmods, focus, level='general')
        matchedmods.extend(morematchedmods)

    return matchedmods, unmatchedmods


def directionsmatch(sign1dirs, sign2dirs, level='specific'):
    if level == 'specific':
        return set(sign1dirs) == set(sign2dirs)
    elif level == 'general':
        for dir1 in sign1dirs:
            if len([dir2 for dir2 in sign2dirs if dir2.sameaxisselection(dir1)]) == 0:
                return False
        return True



# ii. After aligning by hand, align by handshape name if possible (e.g. align two '5' handshapes).
def alignbyhandshapename(configmodsbysign):
    sign1mods = [mod for mod in configmodsbysign[1]]
    sign2mods = [mod for mod in configmodsbysign[2]]

    matchedmods = []

    index1 = 0
    while index1 < len(sign1mods):
        mod1 = sign1mods[index1]
        mod1hs = PREDEFINED_MAP.get(tuple(mod1.handconfiguration.get_hand_transcription_list()))
        if mod1hs is not None:
            mod1hsname = mod1hs.name

            index2 = 0
            while index2 < len(sign2mods):
                mod2 = sign2mods[index2]
                mod2hs = PREDEFINED_MAP.get(tuple(mod2.handconfiguration.get_hand_transcription_list()))
                if mod2hs is not None:
                    mod2hsname = mod2hs.name

                    if mod1hsname == mod2hsname:
                        matchedmods.append((mod1, mod2))
                        sign1mods.remove(mod1)
                        sign2mods.remove(mod2)

                index2 += 1
        index1 += 1

    return matchedmods, {1: sign1mods, 2: sign2mods}


# ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
#   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
#   while sign 2 has only joint-specific movement, align the two joint-specific movements,
#   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
#   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
#   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
#   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
#   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
def alignbymovementtype(movmodsbysign):
    pass  # TODO


# ii. After aligning by hand, try to align by general location type (body-anchored or signing space)
#   -- e.g., if sign1 has both body-anchored and signing space locations, and sign2 has only a body-anchored location,
#   then align the body-anchored modules and leave the signing-space module unmatched.
#   If there are multiple locations of the same type (e.g., multiple body-anchored locations),
#   use the uppermost (in the tree) location specifications to align
#   (e.g., align two head-locations rather than a head location with a torso location, if possible).
def alignbylocationtype(locmodsbysign):

    bodymods = {1: [], 2: []}
    bodyanchoredmods = {1: [], 2: []}
    purelyspatialmods = {1: [], 2: []}
    signingspaceonlymods = {1: [], 2: []}
    noloctypemods = {1: [], 2: []}

    rematchbodymods = {1: [], 2: []}
    rematchallmods = {1: [], 2: []}

    for snum in snums:
        for locmod in locmodsbysign[snum]:
            loctype = locmod.locationtreemodel.locationtype
            if loctype.body:
                bodymods[snum].append(locmod)
            elif loctype.signingspace:
                if loctype.bodyanchored:
                    bodyanchoredmods[snum].append(locmod)
                elif loctype.purelyspatial:
                    purelyspatialmods[snum].append(locmod)
                else:  # just general "signing space" with no further detail
                    signingspaceonlymods[snum].append(locmod)
            else:  # no location type selected
                noloctypemods[snum].append(locmod)

    toreturn = []
    if bodymods[1] and bodymods[2]:
        # match up body modules
        matchedpairs, unmatchedmodsbysign = alignbybodybasedlocation(bodymods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched body module(s) in both signs at this point
            print("error: why are there unmatched body module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchbodymods[snum].extend(unmatchedmodsbysign[snum])

    if bodyanchoredmods[1] and bodyanchoredmods[2]:
        # match up body-anchored modules
        matchedpairs, unmatchedmodsbysign = alignbybodybasedlocation(bodyanchoredmods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched body-anchored module(s) in both signs at this point
            print("error: why are there unmatched body-anchored module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchbodymods[snum].extend(unmatchedmodsbysign[snum])

    if purelyspatialmods[1] and purelyspatialmods[2]:
        # match up purely spatial modules
        matchedpairs, unmatchedmodsbysign = alignbypurelyspatiallocation(purelyspatialmods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched purely-spatial module(s) in both signs at this point
            print("error: why are there unmatched purely-spatial module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])

    if signingspaceonlymods[1] and signingspaceonlymods[2]:
        # match up general signing space modules
        matchedpairs, unmatchedmodsbysign = alignbysigningspaceonlylocation(signingspaceonlymods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched signing-space-only module(s) in both signs at this point
            print("error: why are there unmatched signing-space-only module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])

    if noloctypemods[1] and noloctypemods[2]:
        # match up modules with no specified location type
        matchedpairs, unmatchedmodsbysign = alignbycodingorder(noloctypemods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched no-location module(s) in both signs at this point
            print("error: why are there unmatched no-location module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])

    if rematchbodymods[1] and rematchbodymods[2]:
        # there is at least one pair of potentially-matchable body-based location modules,
        #   where some are body type and some are body-anchored type
        matchedpairs, unmatchedmodsbysign = alignbybodybasedlocation(rematchbodymods)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched body-based module(s) in both signs at this point
            print("error: why are there unmatched body-based module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])

    # if rematchallmods[1] and rematchallmods[2]:
    #     # there is at least one pair of potentially-matchable location modules of various location types
    #     matchedpairs, unmatchedmodsbysign = alignbycodingorder(rematchallmods, matchwithnone=True)
    #     toreturn.extend(matchedpairs)
    #
    #     if unmatchedmodsbysign[1] or unmatchedmodsbysign[2]:
    #         # there should not be unmatched location module(s) in both signs at this point
    #         print("error: why are there unmatched location module(s) in both signs?", unmatchedmodsbysign)
    #
    # return toreturn

    return toreturn, rematchallmods

def alignbybodybasedlocation(bodybasedlocmodsbysign):
    return [], bodybasedlocmodsbysign  # TODO


# # TODO can this be combined with alignbybodylocation? We're just checking for parallel locations, right?
# def alignbybodyanchoredlocation(bodyanchoredlocmodsbysign):
#     return alignbybodylocation(bodyanchoredlocmodsbysign)


def alignbysigningspaceonlylocation(ssonlylocmodsbysign):
    return [], ssonlylocmodsbysign  # TODO


def alignbypurelyspatiallocation(purelyspatiallocmodsbysign):
    return [], purelyspatiallocmodsbysign  # TODO


def alignbynolocation(nolocmodsbysign):
    return [], nolocmodsbysign  # TODO


# TODO this currently uses *solely* uniqueid (which is a timestamp) to determine coding order within the list of
# modules for each sign. If for some reason we need it to refer to the module numbers themselves (eg Loc1, Loc2) more
# explicitly, then this function will also need moduletype & sign1 & sign2 (or sign1 & 2 modulenumberdicts) as input too
def alignbycodingorder(modulesbysign, matchwithnone=False):
    unmatchedmods = {1: [], 2: []}

    # sort both lists of modules based on creation timestamp
    for snum in snums:
        modulesbysign[snum].sort(key=lambda mod: mod.uniqueid)

    # extend whichever list is shorter, if applicable
    lendiff = len(modulesbysign[1]) - len(modulesbysign[2])
    if matchwithnone:
        if lendiff > 0:  # there are more sign1 than sign2 modules
            modulesbysign[2].extend([None] * lendiff)
        elif lendiff < 0:  # there are more sign2 than sign1 modules
            modulesbysign[1].extend([None] * -lendiff)
        # else they're equal so no adjustments necessary
    else:
        if lendiff > 0:  # there are more sign1 than sign2 modules
            unmatchedmods[1] = modulesbysign[1][-lendiff:]
        elif lendiff < 0:  # there are more sign2 than sign1 modules
            unmatchedmods[2] = modulesbysign[2][-lendiff:]
        # else they're equal so there are no unmatched modules

    # pair up the modules in the sign1 & sign2 lists
    matchedmods = [modpair for modpair in zip(modulesbysign[1], modulesbysign[2])]
    return matchedmods, unmatchedmods

def alignbyhand(modulesbysign):
    return [], modulesbysign

    # sign1mods_artnames = set([s1mod.articulators[0] for s1mod in sign1modules])
    # sign2mods_artnames = set([s2mod.articulators[0] for s2mod in sign2modules])
    #
    # if sign1mods_artnames == sign2mods_artnames:
    #     # all modules in both signs use the exact same articulators (but we haven't checked yet which number, ie H1 vs H2
    #     pass  # TODO
    # else:
    #     #
    #     # proceed to next step
    # elif sign1mods_artnames.issubset(sign2mods_artnames) or sign2mods_artnames.issubset(sign1mods_artnames):
    #     # modules in sign1 use a proper subset of the articulators of modules in sign2, or vice versa
    #     pass  # TODO
    #     # align the modules that have matching articulators

    # organize modules by articular and articular number (eg hand/arm/leg, 1/2)
    articulators = {
        1: [],
        2: []
    }
    for snum in snums:
        for mod in modulesbysign[snum]:
            for artnum in [1, 2]:
                if mod.articulators[1][artnum]:
                    articulators[snum].append(ARTICULATOR_ABBREVS[mod.articulators[0]] + str(artnum))

    articulators = {snum: set(articulatorslist) for snum, articulatorslist in articulators.items()}
    sign1articulators = set(sign1articulators)
    sign2articulators = set(sign2articulators)

    # organize modules by articular and articular number (eg hand/arm/leg, 1/2)
    sign1articulators = {
        HAND: {
            1: [],
            2: []
        },
        ARM: {
            1: [],
            2: []
        },
        LEG: {
            1: [],
            2: []
        }
    }
    sign2articulators = {
        HAND: {
            1: [],
            2: []
        },
        ARM: {
            1: [],
            2: []
        },
        LEG: {
            1: [],
            2: []
        }
    }

    for snum in snums:
        for mod in modulesbysign[snum]:
            for artnum in [1, 2]:
                if mod.articulators[1][artnum]:
                    # if this articulatornumber is used, add the module to the list for articulatorname --> artnum
                    sign1articulators[mod.articulators[0]][artnum].append(mod)

    for s1mod in sign1modules:
        if s1mod.articulators[1][1]:
            # if art1 is used, add the module to the list for articulatorname --> 1
            sign1articulators[s1mod.articulators[0]][1].append(s1mod)
        if s1mod.articulators[1][2]:
            # if art2 is used, add the module to the list for articulatorname --> 2
            sign1articulators[s1mod.articulators[0]][2].append(s1mod)
    for s2mod in sign2modules:
        if s2mod.articulators[1][1]:
            # if art1 is used, add the module to the list for articulatorname --> 1
            sign2articulators[s2mod.articulators[0]][1].append(s2mod)
        if s2mod.articulators[1][2]:
            # if art2 is used, add the module to the list for articulatorname --> 2
            sign2articulators[s2mod.articulators[0]][2].append(s2mod)

    # at this point for each sign (sign 1 vs sign 2), we have a dictionary of
    #   articulatorname --> articulatornum --> [list of modules that use that articulator name/number]

    for artname in [HAND, ARM, LEG]:
        if sign1articulators[artname][1] or sign1articulators[artname][2]:
            # there is at least one module in sign1 that uses this articulatorname
            pass  # TODO
        if sign2articulators[artname][1] or sign2articulators[artname][2]:
            # there is at least one module in sign2 that uses this articulatorname
            pass  # TODO



        for artnum in [1, 2]:
            if sign1articulators[artname][artnum] and sign2articulators[artname][artnum]:
                pass  # TODO
                # articulators and numbers both match



    trytoalign = ([], [])
    leaveunmatched = ([], [])





    return trytoalign, leaveunmatched


    # i. First 'align by hand.' That is, try to align hand1 modules from sign1 to hand1 modules from sign2.
    #   If sign1 and sign2 each have only hand1 modules, or each have only hand2 modules, then proceed to the next step of alignment.
    #   If sign1 has both hand1 and hand2 modules, while sign2 has only hand1 modules (or vice versa), then align the hand1 modules only,
    #   and leave all hand2 modules unmatched.
    #   If sign1 has only hand1 modules, and sign2 has only hand2 modules, then this is the only time that non-matching hand modules can be aligned.


    # @property
    # def articulators(self):
    #     if not hasattr(self, '_articulators'):
    #         # backward compatibility pre-20230804 addition of arms and legs as articulators (issues #175 and #176)
    #         articulator_dict = {1: False, 2: False}
    #         if hasattr(self, '_hands'):
    #             articulator_dict[1] = self._hands['H1']
    #             articulator_dict[2] = self._hands['H2']
    #         self._articulators = (HAND, articulator_dict)
    #     return self._articulators


def whichsignshavemodulesoftype(modulesbysign):
    signswithmodules = []
    for snum in snums:
        if modulesbysign[snum]:
            signswithmodules.append(snum)
    return signswithmodules


