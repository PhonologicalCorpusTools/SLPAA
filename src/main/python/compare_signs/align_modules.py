from collections import defaultdict

from PyQt5.QtCore import Qt

from lexicon.module_classes import HandConfigurationHand
from compare_signs.compare_helpers import parse_predefined_names
from constant import ModuleTypes, HAND, ARM, LEG, userdefinedroles as udr, PREDEFINED_MAP
PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}

snums = [1, 2]


# given two signs, this function aligns the s1 modules of the specified type with their s2 counterparts,
#   based first on their articulators, then on the module contents, and finally (as a fallback) the relative order
#   in which the modules were coded
# inputs:
#   sign1 = an object of type Sign
#   sign2 = an object of type Sign
#   moduletype = a string (from class ModuleTypes) indicating the module type to be aligned
# returns a list of pairs of aligned modules of this type, the first element from sign1 and the second from sign2
#   if there are unaligned modules then the other member of the pair will be None
#   return format example: [(s1mod1,s2mod2),(s1mod2,s2mod1),(s1mod3,None)]
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
        if moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.ORIENTATION, ModuleTypes.HANDCONFIG]:
            # i. First 'align by hand.' That is, try to align hand1 modules from sign1 to hand1 modules from sign2.
            #   If sign1 and sign2 each have only hand1 modules, or each have only hand2 modules, then proceed to the next step of alignment.
            #   If sign1 has both hand1 and hand2 modules, while sign2 has only hand1 modules (or vice versa), then align the hand1 modules only,
            #   and leave all hand2 modules unmatched.
            #   If sign1 has only hand1 modules, and sign2 has only hand2 modules, then this is the only time that non-matching hand modules can be aligned.
            return alignbyarticulator(modulesbysign, moduletype)
        elif moduletype in [ModuleTypes.RELATION, ModuleTypes.NONMANUAL]:
            # TODO - waiting for further intructions from Kathleen
            matched1, unmatched = alignmodules_helper(modulesbysign, moduletype)
            matched2, unmatched = alignbycodingorder(unmatched, matchwithnone=True)
            return matched1 + matched2


def alignmodules_helper(modulesbysign, moduletype):
    if moduletype == ModuleTypes.MOVEMENT:
        # ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
        #   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
        #   while sign 2 has only joint-specific movement, align the two joint-specific movements,
        #   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
        #   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
        #   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
        #   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
        #   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
        modsalignedbymovtype, unmatched = alignbymovement(modulesbysign)
        #   If modules still can't be aligned, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbymovtype + modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.LOCATION:
        # ii. After aligning by hand, try to align by general location type (body-anchored or signing space)
        #   -- e.g., if sign1 has both body-anchored and signing space locations, and sign2 has only a body-anchored location,
        #   then align the body-anchored modules and leave the signing-space module unmatched.
        #   If there are multiple locations of the same type (e.g., multiple body-anchored locations),
        #   use the uppermost (in the tree) location specifications to align
        #   (e.g., align two head-locations rather than a head location with a torso location, if possible).
        modsalignedbyloctype, unmatched = alignbylocation(modulesbysign)
        #   If modules still can't be aligned, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbyloctype + modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.ORIENTATION:
        # ii. After aligning by hand, align by palm orientation if possible (e.g. align two palm-up modules).
        # modsalignedbypalm, unmatched = alignbypalmori(modulesbysign)
        modsalignedbypalm, unmatched = alignbyorientation(modulesbysign, focus='palm', level='specific')
        #   If not possible, align by finger root direction.
        # modsalignedbyfingerroot, unmatched = alignbyfingerrootdir(unmatched)
        modsalignedbyfingerroot, unmatched = alignbyorientation(unmatched, focus='root', level='specific')
        #   If still not possible, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbypalm + modsalignedbyfingerroot + modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.HANDCONFIG:
        # ii. After aligning by hand, align by full handshape name if possible (e.g. align two '5' handshapes, or 2 'extended A' handshapes, etc.).
        modsalignedbyhsname, unmatched = alignbyhandshape(modulesbysign, 'name')
        # iii. If aligning by full handshape name isn’t possible, align by ‘base’ handshape.
        #   That is, align any variant of an “A” handshape with another variant of an “A” handshape (e.g. "A" and "extended A"),
        #   or any variant of a “B” handshape with another variant of a “B” handshape, etc.
        #   The base handshapes appear in the first column of the predefined handshape chart,
        #   so basically this is aligning by rows in that chart.
        #   If there are multiple handshapes with the same base, they can just be aligned by coding order.
        modsalignedbyhsbase, unmatched = alignbyhandshape(unmatched, 'base')
        # iv. If aligning by ‘base’ handshape isn’t possible, align by ‘variant type.’
        #   That is, align any ‘bent’ handshape with another ‘bent’ handshape, or any ‘clawed’ handshape with another
        #   ‘clawed’ handshape, etc. The variant types are listed in the first row of the predefined handshape chart,
        #   so basically this is aligning by columns in that chart.
        modsalignedbyhsvariant, unmatched = alignbyhandshape(unmatched, 'variant')
        # from 20250908 meeting: align by forearm after variant and before coding order
        modsalignedbyhsforearm, unmatched = alignbyhandshape(unmatched, 'forearm')
        # v. If there are still unaligned handshapes, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbyhsname + modsalignedbyhsbase + modsalignedbyhsvariant + modsalignedbyhsforearm + modsalignedbycodingorder, unmatched
        #   [NB: this one might eventually need to get refined.]
    elif moduletype == ModuleTypes.RELATION:
        # TODO - waiting for further intructions from Kathleen
        modsalignedbycodingorder, unmatched = alignbycodingorder(modulesbysign, matchwithnone=False)
        return modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.NONMANUAL:
        # TODO - waiting for further intructions from Kathleen
        modsalignedbycodingorder, unmatched = alignbycodingorder(modulesbysign, matchwithnone=False)
        return modsalignedbycodingorder, unmatched


# try to match as specifically as possible (eg vertical/up with vertical/up)
# any leftovers, try to match at least to the general direction (eg vertical/up with vertical/down or just vertical)
# any leftovers, punt back up to next step
def alignbyorientation(orimodsbysign, focus, level='specific'):
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
        morematchedmods, unmatchedmods = alignbyorientation(unmatchedmods, focus, level='general')
        matchedmods.extend(morematchedmods)

    return matchedmods, unmatchedmods


# both lists of directions must be in this order: horizontal, vertical, sagittal
def directionsmatch(sign1dirs, sign2dirs, level='specific'):
    if level == 'specific':
        return sign1dirs == sign2dirs
    elif level == 'general':
        for dir1 in sign1dirs:
            if len([dir2 for dir2 in sign2dirs if dir2.sameaxisselection(dir1)]) == 0:
                return False
        return True


# ii. After aligning by hand, align by full handshape name if possible (e.g. align two '5' handshapes, or 2 'extended A' handshapes, etc.).
# iii. If aligning by full handshape name isn’t possible, align by ‘base’ handshape.
#   That is, align any variant of an “A” handshape with another variant of an “A” handshape (e.g. "A" and "extended A"),
#   or any variant of a “B” handshape with another variant of a “B” handshape, etc.
#   The base handshapes appear in the first column of the predefined handshape chart,
#   so basically this is aligning by rows in that chart.
#   If there are multiple handshapes with the same base, they can just be aligned by coding order.
# iv. If aligning by ‘base’ handshape isn’t possible, align by ‘variant type.’
#   That is, align any ‘bent’ handshape with another ‘bent’ handshape, or any ‘clawed’ handshape with another
#   ‘clawed’ handshape, etc. The variant types are listed in the first row of the predefined handshape chart,
#   so basically this is aligning by columns in that chart.
# from 20250908 meeting: align by forearm after variant and before coding order
def alignbyhandshape(configmodsbysign, elementtoalignby):
    # elementtoalignby: str. one of 'name', 'base', 'variant', or 'forearm'
    sign1mods = [mod for mod in configmodsbysign[1]]
    sign2mods = [mod for mod in configmodsbysign[2]]

    matchedmods = []

    index1 = 0
    while index1 < len(sign1mods):
        mod1 = sign1mods[index1]
        mod1hs = PREDEFINED_MAP.get(tuple(HandConfigurationHand(mod1.handconfiguration).get_hand_transcription_list()))
        # tuple(HandConfigurationHand(self.handconfiguration).get_hand_transcription_list())
        if mod1hs is not None:
            mod1hsname = mod1hs.name

            index2 = 0
            while index2 < len(sign2mods):
                mod2 = sign2mods[index2]
                mod2hs = PREDEFINED_MAP.get(tuple(HandConfigurationHand(mod2.handconfiguration).get_hand_transcription_list()))
                if mod2hs is not None:
                    mod2hsname = mod2hs.name

                    mod1bases, mod1variants = parse_predefined_names(mod1hsname, None, mod2hsname, return_path_form=False)
                    mod2bases, mod2variants = parse_predefined_names(mod2hsname, None, mod1hsname, return_path_form=False)

                    mod1bases = set(mod1bases)
                    mod2bases = set(mod2bases)
                    mod1variants = [v for v in mod1variants if v not in mod1bases]
                    mod2variants = [v for v in mod2variants if v not in mod2bases]

                    if (elementtoalignby == 'name' and mod1hsname == mod2hsname) or \
                            (elementtoalignby == 'base' and (mod1bases.issubset(mod2bases) or mod2bases.issubset(mod1bases))) or \
                            (elementtoalignby == 'variant' and mod1variants == mod2variants) or \
                            (elementtoalignby == 'forearm' and mod1.overalloptions['forearm'] == mod2.overalloptions['forearm']):
                        matchedmods.append((mod1, mod2))
                        sign1mods.remove(mod1)
                        sign2mods.remove(mod2)

                index2 += 1
        index1 += 1

    return matchedmods, {1: sign1mods, 2: sign2mods}


# def alignbylocation_helper(locmodsbysign, locnodename=""):
#     matchedmods = []
#     unmatched = {1: [], 2: []}
#
#     if len(locmodsbysign[1]) == len(locmodsbysign[2]) == 1:
#         matchedmods.append((locmodsbysign[1][0], locmodsbysign[2][0]))
#         return matchedmods, unmatched
#
#     # do I need this stage or is this already taken care of above? ... or maybe I do need it because recursion? TODO
#     elif len(locmodsbysign[1]) == 0 or len(locmodsbysign[2]) == 0:
#         return matchedmods, locmodsbysign
#
#     else:  # both signs have locmods, and at least one sign has more than one
#         modsbysubnodesbysign = {1: defaultdict(list), 2: defaultdict(list)}
#
#         for snum in snums:
#             locmods = locmodsbysign[snum]
#             for lmod in locmods:
#                 treemodel = lmod.locationtreemodel
#                 checkedsubnodes = get_tree_subnodes(ModuleTypes.LOCATION, treemodel, locnodename, toplevel=(locnodename == ""))  # not locnodename
#                 checkedsubnodes_tuple = tuple(sorted(checkedsubnodes))
#                 modsbysubnodesbysign[snum][checkedsubnodes_tuple].append(lmod)
#
#         # now run through all the subnode groupings and see if we can match any
#         s1subnodegroups = set(modsbysubnodesbysign[1].keys())
#         s2subnodegroups = set(modsbysubnodesbysign[2].keys())
#         subnodegroups_inbothsigns = s1subnodegroups.intersection(s2subnodegroups)
#         for sharedsubnodegroup in subnodegroups_inbothsigns:
#             if len(sharedsubnodegroup) == 1:
#                 matches, unmatches = alignbylocation_helper({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, sharedsubnodegroup[0])
#             else:
#                 matches, unmatches = alignbycodingorder({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, matchwithnone=False)
#             matchedmods.extend(matches)
#             unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)
#         for s1onlysubnodegroup in s1subnodegroups.difference(subnodegroups_inbothsigns):
#             unmatched[1].extend(modsbysubnodesbysign[1][s1onlysubnodegroup])
#         for s2onlysubnodegroup in s2subnodegroups.difference(subnodegroups_inbothsigns):
#             unmatched[2].extend(modsbysubnodesbysign[2][s2onlysubnodegroup])
#
#         matches, unmatches = alignbycodingorder(unmatches, matchwithnone=False)
#         matchedmods.extend(matches)
#         unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)
#
#         return matchedmods, unmatched


# assume that both dicts have the same set of keys, and that each key has a list as its value
def concatenate_dictlists(d1, d2, allowduplicates=False):
    newdict = {k: [] for k in d1.keys()}
    for k in d1.keys():
        for listitem in d1[k] + d2[k]:
            if allowduplicates or listitem not in newdict[k]:
                newdict[k].append(listitem)
    # newdict = {k: d1[k] + d2[k] for k in d1.keys()}
    return newdict


def alignbymovement_helper_old(movmodsbysign, typename):
    sign1mods = [mod for mod in movmodsbysign[1]]
    sign2mods = [mod for mod in movmodsbysign[2]]

    matchedmods = []
    unmatched = {1: [], 2: []}

    index1 = 0
    while index1 < len(sign1mods):
        mod1 = sign1mods[index1]
        # mod1smeetingcriteria = mvmttree_checked_subnodes(mod1.movementtreemodel, typename)
        mod1smeetingcriteria = get_tree_subnodes(ModuleTypes.MOVEMENT, mod1.movementtreemodel, typename, toplevel=False)
        if mod1smeetingcriteria is not None:
            index2 = 0
            while index2 < len(sign2mods):
                mod2 = sign2mods[index2]
                # mod2smeetingcriteria = mvmttree_checked_subnodes(mod2.movementtreemodel, typename)
                mod2smeetingcriteria = get_tree_subnodes(ModuleTypes.MOVEMENT, mod2.movementtreemodel, typename, toplevel=False)
                if mod2smeetingcriteria is not None:
                    if set(mod1smeetingcriteria) == set(mod2smeetingcriteria):
                        matchedmods.append((mod1, mod2))
                        sign1mods.remove(mod1)
                        sign2mods.remove(mod2)

                index2 += 1
        index1 += 1

    if sign1mods or sign2mods:
        # if there are still some of this type of module left unmatched, it's because there were no sub-type matches
        #   e.g., maybe we had two Perceptual shape movement modules, but one was Straight and the other was Arc
        # so just go ahead and match these types by coding order
        matchedbycodingorder, unmatched = alignbycodingorder({1: sign1mods, 2: sign2mods}, matchwithnone=False)
        matchedmods.extend(matchedbycodingorder)

    return matchedmods, unmatched


def alignbymoveorloc_helper(modsbysign, modtype, nodename=""):
    matchedmods = []
    unmatched = {1: [], 2: []}

    if len(modsbysign[1]) == len(modsbysign[2]) == 1:
        matchedmods.append((modsbysign[1][0], modsbysign[2][0]))
        return matchedmods, unmatched

    # do I need this stage or is this already taken care of above? ... or maybe I do need it because recursion? TODO
    elif len(modsbysign[1]) == 0 or len(modsbysign[2]) == 0:
        return matchedmods, modsbysign

    else:  # both signs have modules of this type, and at least one sign has more than one
        modsbysubnodesbysign = {1: defaultdict(list), 2: defaultdict(list)}

        for snum in snums:
            thissignmods = modsbysign[snum]
            for mod in thissignmods:
                treemodel = mod.movementtreemodel if modtype == ModuleTypes.MOVEMENT else mod.locationtreemodel
                toplevel = False if modtype == ModuleTypes.MOVEMENT else (nodename == "")
                checkedsubnodes = get_tree_subnodes(modtype, treemodel, nodename, toplevel=toplevel)
                checkedsubnodes_tuple = tuple(sorted(checkedsubnodes))
                modsbysubnodesbysign[snum][checkedsubnodes_tuple].append(mod)

        # now run through all the subnode groupings and see if we can match any
        s1subnodegroups = set(modsbysubnodesbysign[1].keys())
        s2subnodegroups = set(modsbysubnodesbysign[2].keys())
        subnodegroups_inbothsigns = s1subnodegroups.intersection(s2subnodegroups)
        for sharedsubnodegroup in subnodegroups_inbothsigns:
            if len(sharedsubnodegroup) == 1:
                matches, unmatches = alignbymoveorloc_helper({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, modtype=modtype, nodename=sharedsubnodegroup[0])
            else:
                matches, unmatches = alignbycodingorder({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, matchwithnone=False)
            matchedmods.extend(matches)
            unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)
        for s1onlysubnodegroup in s1subnodegroups.difference(subnodegroups_inbothsigns):
            unmatched[1].extend(modsbysubnodesbysign[1][s1onlysubnodegroup])
        for s2onlysubnodegroup in s2subnodegroups.difference(subnodegroups_inbothsigns):
            unmatched[2].extend(modsbysubnodesbysign[2][s2onlysubnodegroup])

        matches, unmatches = alignbycodingorder(unmatches, matchwithnone=False)
        matchedmods.extend(matches)
        unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)

        return matchedmods, unmatched


# # TODO copied from location_helper
# def alignbymovement_helper(movmodsbysign, movnodename=""):
#     matchedmods = []
#     unmatched = {1: [], 2: []}
#
#     if len(movmodsbysign[1]) == len(movmodsbysign[2]) == 1:
#         matchedmods.append((movmodsbysign[1][0], movmodsbysign[2][0]))
#         return matchedmods, unmatched
#
#     # do I need this stage or is this already taken care of above? ... or maybe I do need it because recursion? TODO
#     elif len(movmodsbysign[1]) == 0 or len(movmodsbysign[2]) == 0:
#         return matchedmods, movmodsbysign
#
#     else:  # both signs have movmods, and at least one sign has more than one
#         modsbysubnodesbysign = {1: defaultdict(list), 2: defaultdict(list)}
#
#         for snum in snums:
#             movmods = movmodsbysign[snum]
#             for mmod in movmods:
#                 treemodel = mmod.movementtreemodel
#                 checkedsubnodes = get_tree_subnodes(ModuleTypes.MOVEMENT, treemodel, movnodename, toplevel=False)
#                 checkedsubnodes_tuple = tuple(sorted(checkedsubnodes))
#                 modsbysubnodesbysign[snum][checkedsubnodes_tuple].append(mmod)
#
#         # now run through all the subnode groupings and see if we can match any
#         s1subnodegroups = set(modsbysubnodesbysign[1].keys())
#         s2subnodegroups = set(modsbysubnodesbysign[2].keys())
#         subnodegroups_inbothsigns = s1subnodegroups.intersection(s2subnodegroups)
#         for sharedsubnodegroup in subnodegroups_inbothsigns:
#             if len(sharedsubnodegroup) == 1:
#                 matches, unmatches = alignbylocation_helper({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, sharedsubnodegroup[0])
#             else:
#                 matches, unmatches = alignbycodingorder({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, matchwithnone=False)
#             matchedmods.extend(matches)
#             unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)
#         for s1onlysubnodegroup in s1subnodegroups.difference(subnodegroups_inbothsigns):
#             unmatched[1].extend(modsbysubnodesbysign[1][s1onlysubnodegroup])
#         for s2onlysubnodegroup in s2subnodegroups.difference(subnodegroups_inbothsigns):
#             unmatched[2].extend(modsbysubnodesbysign[2][s2onlysubnodegroup])
#
#         matches, unmatches = alignbycodingorder(unmatches, matchwithnone=False)
#         matchedmods.extend(matches)
#         unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)
#
#         return matchedmods, unmatched


# TODO can I reduce the number of args here?
def get_tree_subnodes(moduletype, treemodel, nodename, toplevel=False):  # TODO are the last two args redundant wrt each other?
    role = Qt.DisplayRole  # (Qt.UserRole + udr.nodedisplayrole) if moduletype == ModuleTypes.LOCATION else Qt.DisplayRole  # for MOVEMENT
    checked_subnodes = []
    if not nodename and not toplevel:
        return checked_subnodes

    startitem = treemodel.invisibleRootItem() if toplevel else treemodel.findItemsByRoleValues(role, [nodename])[0]

    for r in range(startitem.rowCount()):  # one level only
        child = startitem.child(r, 0)
        if child is not None:
            nodetext = child.data(role)
            checkstate = child.checkState()
            if checkstate in [Qt.Checked, Qt.PartiallyChecked]:
                checked_subnodes.append(nodetext)
    return checked_subnodes


# ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
#   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
#   while sign 2 has only joint-specific movement, align the two joint-specific movements,
#   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
#   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
#   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
#   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
#   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
def alignbymovement(movmodsbysign):
    modsbymovementtypebysign = {}

    for snum in snums:
        for movmod in movmodsbysign[snum]:
            # movtype = mvmttree_checked_subnodes(movmod.movementtreemodel, 'Movement type')
            movtype = get_tree_subnodes(ModuleTypes.MOVEMENT, movmod.movementtreemodel, 'Movement type', toplevel=False)
            movtype = movtype[0] if movtype else ""
            if movtype not in modsbymovementtypebysign.keys():
                modsbymovementtypebysign[movtype] = {1: [], 2: []}
            modsbymovementtypebysign[movtype][snum].append(movmod)

    toreturn = []
    rematchmods = {1: [], 2: []}
    for movementtype, movementtypemodsbysign in modsbymovementtypebysign.items():
        if movementtypemodsbysign[1] and movementtypemodsbysign[2]:
            # match up the modules of this movement type
            # matchedpairs, unmatchedmodsbysign = alignbymovement_helper(movementtypemodsbysign, movementtype)
            matchedpairs, unmatchedmodsbysign = alignbymoveorloc_helper(movementtypemodsbysign, modtype=ModuleTypes.MOVEMENT, nodename=movementtype)
            toreturn.extend(matchedpairs)

            if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
                # there should not be unmatched movement module(s) of this movement type in both signs at this point
                print("error: why are there unmatched " + movementtype + " module(s) in both signs?", unmatchedmodsbysign)
            else:
                for snum in snums:
                    rematchmods[snum].extend(unmatchedmodsbysign[snum])
        else:
            # there was only one sign with any modules of this movement type; add them back to the rematch list
            for snum in snums:
                rematchmods[snum].extend(movementtypemodsbysign[snum])

    return toreturn, rematchmods


# ii. After aligning by hand, try to align by general location type (body-anchored or signing space)
#   -- e.g., if sign1 has both body-anchored and signing space locations, and sign2 has only a body-anchored location,
#   then align the body-anchored modules and leave the signing-space module unmatched.
#   If there are multiple locations of the same type (e.g., multiple body-anchored locations),
#   use the uppermost (in the tree) location specifications to align
#   (e.g., align two head-locations rather than a head location with a torso location, if possible).
def alignbylocation(locmodsbysign):
    modsbylocationtypebysign = {}

    for snum in snums:
        for locmod in locmodsbysign[snum]:
            loctype = locmod.locationtreemodel.locationtype
            loctype_repr = repr(loctype)
            if loctype_repr not in modsbylocationtypebysign.keys():
                modsbylocationtypebysign[loctype_repr] = {1: [], 2: []}
            modsbylocationtypebysign[loctype_repr][snum].append(locmod)

    rematchbodymods = {1: [], 2: []}
    rematchallmods = {1: [], 2: []}

    toreturn = []
    for loctype, loctypemodsbysign in modsbylocationtypebysign.items():
        if loctypemodsbysign[1] and loctypemodsbysign[2]:
            # match up the modules of this location type
            # matchedpairs, unmatchedmodsbysign = alignbyloctreeitems_helper(loctypemodsbysign)
            # matchedpairs, unmatchedmodsbysign = alignbylocation_helper(loctypemodsbysign)
            matchedpairs, unmatchedmodsbysign = alignbymoveorloc_helper(loctypemodsbysign, modtype=ModuleTypes.LOCATION)
            toreturn.extend(matchedpairs)

            if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
                # there should not be unmatched location module(s) of this location type in both signs at this point
                print("error: why are there unmatched " + loctype + " module(s) in both signs?", unmatchedmodsbysign)
            else:
                for snum in snums:
                    if "body" in loctype:
                        rematchbodymods[snum].extend(unmatchedmodsbysign[snum])
                    else:
                        rematchallmods[snum].extend(unmatchedmodsbysign[snum])
        else:
            # there was only one sign with any modules of this location type; add them back to the rematch list
            for snum in snums:
                if "body" in loctype:
                    rematchbodymods[snum].extend(loctypemodsbysign[snum])
                else:
                    rematchallmods[snum].extend(loctypemodsbysign[snum])

    if rematchbodymods[1] and rematchbodymods[2]:
        # there is at least one pair of potentially-matchable body-based location modules,
        #   where some are body type and some are body-anchored type
        # matchedpairs, unmatchedmodsbysign = alignbyloctreeitems_helper(rematchbodymods)
        # matchedpairs, unmatchedmodsbysign = alignbylocation_helper(rematchbodymods)
        matchedpairs, unmatchedmodsbysign = alignbymoveorloc_helper(rematchbodymods, modtype=ModuleTypes.LOCATION)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched body-based module(s) in both signs at this point
            print("error: why are there unmatched body-based module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any body-based modules to rematch; add them back to the rematch-all list
        for snum in snums:
            rematchallmods[snum].extend(rematchbodymods[snum])

    return toreturn, rematchallmods


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
            unmatchedmods[2] = modulesbysign[2][lendiff:]
        # else they're equal so there are no unmatched modules

    # pair up the modules in the sign1 & sign2 lists
    matchedmods = [modpair for modpair in zip(modulesbysign[1], modulesbysign[2])]
    return matchedmods, unmatchedmods

def alignbyarticulator(modulesbysign, moduletype):
    if moduletype == ModuleTypes.MOVEMENT:
        temp = 1

    matchedmods = []

    sign1modsbyarticulator = {
        HAND: {1: [], 2: [], 3: []},  # with 3 meaning both 1 and 2
        ARM: {1: [], 2: [], 3: []},
        LEG: {1: [], 2: [], 3: []},
    }

    sign2modsbyarticulator = {
        HAND: {1: [], 2: [], 3: []},  # with 3 meaning both 1 and 2
        ARM: {1: [], 2: [], 3: []},
        LEG: {1: [], 2: [], 3: []},
    }

    # works in-place
    arrangemodsbyarticulator(modulesbysign, sign1modsbyarticulator, sign2modsbyarticulator)

    for art in [HAND, ARM, LEG]:
        for artnum in [1, 2, 3]:
            if sign1modsbyarticulator[art][artnum] and sign2modsbyarticulator[art][artnum]:
                # the articulators are a perfect match (eg, H1-H1 or L1&2-L1&2) so try and align whatever modules are in those lists
                alignedmodules, unmatched = alignmodules_helper({
                    1: sign1modsbyarticulator[art][artnum],
                    2: sign2modsbyarticulator[art][artnum]
                },
                moduletype)
                # save aligned modules to be returned at the end of the function
                matchedmods.extend(alignedmodules)
                # put any unmatched ones back into the pot
                sign1modsbyarticulator[art][artnum] = unmatched[1]
                sign2modsbyarticulator[art][artnum] = unmatched[2]

        # once that previous loop is done, we will have tried to make all possible precise articulator matches
        #   (eg H1 with H1, A2 with A2, L1&2 with L1&2, etc)

        # next we will try to make any subset matches (eg H1 with H1&2)

        for artnum in [1, 2]:
            if sign1modsbyarticulator[art][artnum] and sign2modsbyarticulator[art][3]:
                # the articulators are a subset match (eg, H1-H1&2 or A2-A1&2) so try and align whatever modules are in those lists
                alignedmodules, unmatched = alignmodules_helper({
                    1: sign1modsbyarticulator[art][artnum],
                    2: sign2modsbyarticulator[art][3]
                },
                moduletype)
                # save aligned modules to be returned at the end of the function
                matchedmods.extend(alignedmodules)
                # put any unmatched ones back into the pot
                sign1modsbyarticulator[art][artnum] = unmatched[1]
                sign2modsbyarticulator[art][3] = unmatched[2]
            if sign1modsbyarticulator[art][3] and sign2modsbyarticulator[art][artnum]:
                # the articulators are a subset match (eg, H1&2-H2 or L1&2-L1) so try and align whatever modules are in those lists
                alignedmodules, unmatched = alignmodules_helper({
                    1: sign1modsbyarticulator[art][3],
                    2: sign2modsbyarticulator[art][artnum]
                },
                moduletype)
                # save aligned modules to be returned at the end of the function
                matchedmods.extend(alignedmodules)
                # put any unmatched ones back into the pot
                sign1modsbyarticulator[art][3] = unmatched[1]
                sign2modsbyarticulator[art][artnum] = unmatched[2]

        # and then we'll align any leftovers within an articulator (eg A1 with A2)
        stillunmatchedwithinarticulator = {
            1: sign1modsbyarticulator[art][1] + sign1modsbyarticulator[art][2] + sign1modsbyarticulator[art][3],
            2: sign2modsbyarticulator[art][1] + sign2modsbyarticulator[art][2] + sign2modsbyarticulator[art][3],
        }
        alignedmodules, unmatched = alignmodules_helper(stillunmatchedwithinarticulator, moduletype)
        # save aligned modules to be returned at the end of the function
        matchedmods.extend(alignedmodules)
        # put unmatched mods back into the pot
        sign1modsbyarticulator[art] = {1: [], 2: [], 3: []}
        sign2modsbyarticulator[art] = {1: [], 2: [], 3: []}

        # works in-place
        arrangemodsbyarticulator(unmatched, sign1modsbyarticulator, sign2modsbyarticulator)

    # once all the within-articulator matches have been attempted, we'll try to match across articulators
    #   first H&A, then H&L, then A&L
    for artpair in [(HAND, ARM), (HAND, LEG), (ARM, LEG)]:
        for arttype1, arttype2 in [artpair, artpair[::-1]]:
            for artnum in [1, 2, 3]:
                if sign1modsbyarticulator[arttype1][artnum] and sign2modsbyarticulator[arttype2][artnum]:
                    # the articulators are a near-perfect match (eg, H1-A1 or L1&2-H1&2) so try and align whatever modules are in those lists
                    alignedmodules, unmatched = alignmodules_helper({
                        1: sign1modsbyarticulator[arttype1][artnum],
                        2: sign2modsbyarticulator[arttype2][artnum]
                    },
                    moduletype)
                    # save aligned modules to be returned at the end of the function
                    matchedmods.extend(alignedmodules)
                    # put any unmatched ones back into the pot
                    sign1modsbyarticulator[arttype1][artnum] = unmatched[1]
                    sign2modsbyarticulator[arttype2][artnum] = unmatched[2]


            for artnum in [1, 2]:
                if sign1modsbyarticulator[arttype1][artnum] and sign2modsbyarticulator[arttype2][3]:
                    # the articulators are a near-subset match (eg, L1-H1&2 or H2-A1&2) so try and align whatever modules are in those lists
                    alignedmodules, unmatched = alignmodules_helper({
                        1: sign1modsbyarticulator[arttype1][artnum],
                        2: sign2modsbyarticulator[arttype2][3]
                    },
                    moduletype)
                    # save aligned modules to be returned at the end of the function
                    matchedmods.extend(alignedmodules)
                    # put any unmatched ones back into the pot
                    sign1modsbyarticulator[arttype1][artnum] = unmatched[1]
                    sign2modsbyarticulator[arttype2][3] = unmatched[2]
                if sign1modsbyarticulator[arttype1][3] and sign2modsbyarticulator[arttype2][artnum]:
                    # the articulators are a subset match (eg, H1&2-L2 or L1&2-A1) so try and align whatever modules are in those lists
                    alignedmodules, unmatched = alignmodules_helper({
                        1: sign1modsbyarticulator[arttype1][3],
                        2: sign2modsbyarticulator[arttype2][artnum]
                    },
                    moduletype)
                    # save aligned modules to be returned at the end of the function
                    matchedmods.extend(alignedmodules)
                    # put any unmatched ones back into the pot
                    sign1modsbyarticulator[arttype1][3] = unmatched[1]
                    sign2modsbyarticulator[arttype2][artnum] = unmatched[2]

            # and then we'll align any leftovers within an articulator pair (eg A1 with L2)

            stillunmatchedwithinarticulatorpair = {
                1: sign1modsbyarticulator[arttype1][1] + sign1modsbyarticulator[arttype1][2] + sign1modsbyarticulator[arttype1][3],
                2: sign2modsbyarticulator[arttype2][1] + sign2modsbyarticulator[arttype2][2] + sign2modsbyarticulator[arttype2][3],
            }

            alignedmodules, unmatched = alignmodules_helper(stillunmatchedwithinarticulatorpair, moduletype)
            # save aligned modules to be returned at the end of the function
            matchedmods.extend(alignedmodules)
            # put unmatched mods back into the pot
            sign1modsbyarticulator[arttype1] = {1: [], 2: [], 3: []}
            sign2modsbyarticulator[arttype2] = {1: [], 2: [], 3: []}
            # works in-place
            arrangemodsbyarticulator(unmatched, sign1modsbyarticulator, sign2modsbyarticulator)

    allremainingunmatchedmods = {1: [], 2: []}
    for articulatordict in sign1modsbyarticulator.values():
        for artnumlist in articulatordict.values():
            allremainingunmatchedmods[1].extend(artnumlist)
    for articulatordict in sign2modsbyarticulator.values():
        for artnumlist in articulatordict.values():
            allremainingunmatchedmods[2].extend(artnumlist)

    # TODO at this point any unmatched modules should be... aligned by coding order? left unmatched? ... it is tres confusing
    # TODO at this point will as much be aligned as possible? I think so... but just in case should we try by coding order?
    alignedmodules, unmatched = alignbycodingorder(allremainingunmatchedmods, matchwithnone=True)
    matchedmods.extend(alignedmodules)

    return matchedmods  # all the aligned modules, some possibly with 'none'


# in-place
def arrangemodsbyarticulator(modulesbysign, sign1modsbyart, sign2modsbyart):
    for snum in snums:
        for mod in modulesbysign[snum]:
            artname = mod.articulators[0]
            artnums_usage = mod.articulators[1]
            if artnums_usage[1] and artnums_usage[2]:
                if snum == 1:
                    sign1modsbyart[artname][3].append(mod)
                elif snum == 2:
                    sign2modsbyart[artname][3].append(mod)
            elif artnums_usage[1]:
                if snum == 1:
                    sign1modsbyart[artname][1].append(mod)
                elif snum == 2:
                    sign2modsbyart[artname][1].append(mod)
            elif artnums_usage[2]:
                if snum == 1:
                    sign1modsbyart[artname][2].append(mod)
                elif snum == 2:
                    sign2modsbyart[artname][2].append(mod)

    # return sign1modsbyart, sign2modsbyart


def whichsignshavemodulesoftype(modulesbysign):
    signswithmodules = []
    for snum in snums:
        if modulesbysign[snum]:
            signswithmodules.append(snum)
    return signswithmodules

