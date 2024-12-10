from PyQt5.QtCore import Qt

from lexicon.module_classes import HandConfigurationHand
from constant import ModuleTypes, HAND, ARM, LEG, userdefinedroles as udr, PREDEFINED_MAP
PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}

snums = [1, 2]


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
        modsalignedbymovtype, unmatched = alignbymovementtype(modulesbysign)
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
        modsalignedbyloctype, unmatched = alignbylocationtype(modulesbysign)
        #   If modules still can't be aligned, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbyloctype + modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.ORIENTATION:
        # ii. After aligning by hand, align by palm orientation if possible (e.g. align two palm-up modules).
        modsalignedbypalm, unmatched = alignbypalmori(modulesbysign)
        #   If not possible, align by finger root direction.
        modsalignedbyfingerroot, unmatched = alignbyfingerrootdir(unmatched)
        #   If still not possible, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbypalm + modsalignedbyfingerroot + modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.HANDCONFIG:
        # ii. After aligning by hand, align by handshape name if possible (e.g. align two '5' handshapes).
        modsalignedbyhs, unmatched = alignbyhandshapename(modulesbysign)
        #   If not possible, align by coding order.
        modsalignedbycodingorder, unmatched = alignbycodingorder(unmatched, matchwithnone=False)
        return modsalignedbyhs + modsalignedbycodingorder, unmatched
        #   [NB: this one might eventually need to get refined.]
    elif moduletype == ModuleTypes.RELATION:
        # TODO - waiting for further intructions from Kathleen
        modsalignedbycodingorder, unmatched = alignbycodingorder(modulesbysign, matchwithnone=False)
        return modsalignedbycodingorder, unmatched
    elif moduletype == ModuleTypes.NONMANUAL:
        # TODO - waiting for further intructions from Kathleen
        modsalignedbycodingorder, unmatched = alignbycodingorder(modulesbysign, matchwithnone=False)
        return modsalignedbycodingorder, unmatched


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

                    if mod1hsname == mod2hsname:
                        matchedmods.append((mod1, mod2))
                        sign1mods.remove(mod1)
                        sign2mods.remove(mod2)

                index2 += 1
        index1 += 1

    return matchedmods, {1: sign1mods, 2: sign2mods}


def alignbyjointspecificmvmt(jointspecmodsbysign):
    return alignbymvmttype_helper(jointspecmodsbysign, 'Joint-specific movements')

def alignbyperceptualshape(perceptualshapemodsbysign):
    return alignbymvmttype_helper(perceptualshapemodsbysign, 'Perceptual shape')

def alignbyhandshapechange(jointspecmodsbysign):
    return alignbymvmttype_helper(jointspecmodsbysign, 'Handshape change')


def alignbymvmttype_helper(movmodsbysign, typename):
    sign1mods = [mod for mod in movmodsbysign[1]]
    sign2mods = [mod for mod in movmodsbysign[2]]

    matchedmods = []
    unmatched = {1: [], 2: []}

    index1 = 0
    while index1 < len(sign1mods):
        mod1 = sign1mods[index1]
        mod1smeetingcriteria = getmvmtsubtypes(mod1.movementtreemodel, typename)
        if mod1smeetingcriteria is not None:
            index2 = 0
            while index2 < len(sign2mods):
                mod2 = sign2mods[index2]
                mod2smeetingcriteria = getmvmtsubtypes(mod2.movementtreemodel, typename)
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


def getmvmtsubtypes(movtreemodel, typename):
    subtypenodes = []

    # typeitem = movtreemodel.findItemsByRoleValues(Qt.UserRole + udr.nodedisplayrole, [typename])[0]
    # typeitem = movtreemodel.findItemsByRoleValues(Qt.UserRole + udr.pathdisplayrole, [typename])[0]
    typeitem = movtreemodel.findItemsByRoleValues(Qt.DisplayRole, [typename])[0]

    for r in range(typeitem.rowCount()):  # top level only
        child = typeitem.child(r, 0)
        if child is not None:
            # nodetext = child.data(Qt.UserRole + udr.nodedisplayrole)
            # nodetext = child.data(Qt.UserRole + udr.pathdisplayrole)
            nodetext = child.data(Qt.DisplayRole)
            checkstate = child.checkState()
            if checkstate in [Qt.Checked, Qt.PartiallyChecked]:
                subtypenodes.append(nodetext)
    return subtypenodes


# def getmovtype(movtreemodel):
#     movtypenodes = []
#
#     movtypeitem = movtreemodel.findItemsByRoleValues(Qt.UserRole + udr.nodedisplayrole, ['Movement type'])[0]
#
#     for r in range(movtypeitem.rowCount()):  # top level only
#         child = movtypeitem.child(r, 0)
#         if child is not None:
#             nodetext = child.data(Qt.UserRole + udr.nodedisplayrole)
#             checkstate = child.checkState()
#             if checkstate in [Qt.Checked, Qt.PartiallyChecked]:
#                 movtypenodes.append(nodetext)
#     return movtypenodes




# ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
#   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
#   while sign 2 has only joint-specific movement, align the two joint-specific movements,
#   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
#   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
#   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
#   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
#   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
def alignbymovementtype(movmodsbysign):
    perceptualshapemods = {1: [], 2: []}
    jointspecificmods = {1: [], 2: []}
    handshapechangemods = {1: [], 2: []}
    othermods = {1: [], 2: []}

    for snum in snums:
        for movmod in movmodsbysign[snum]:
            movtype = getmvmtsubtypes(movmod.movementtreemodel, 'Movement type')
            if "Perceptual shape" in movtype:
                perceptualshapemods[snum].append(movmod)
            elif "Joint-specific movements" in movtype:
                jointspecificmods[snum].append(movmod)
            elif "Handshape change" in movtype:
                handshapechangemods[snum].append(movmod)
            else:  # no movement type selected
                othermods[snum].append(movmod)

    toreturn = []
    rematchmods = {1: [], 2: []}
    if perceptualshapemods[1] and perceptualshapemods[2]:
        # match up perceptual shape modules
        matchedpairs, unmatchedmodsbysign = alignbyperceptualshape(perceptualshapemods)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched perceptual shape module(s) in both signs at this point
            print("error: why are there unmatched perceptual shape module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any perceptual shape modules; add them back to the rematch list
        for snum in snums:
            rematchmods[snum].extend(perceptualshapemods[snum])


    if jointspecificmods[1] and jointspecificmods[2]:
        # match up joint-specific modules
        matchedpairs, unmatchedmodsbysign = alignbyjointspecificmvmt(jointspecificmods)
        toreturn.extend(matchedpairs)  # unmatchedmodsbysign randomly empties at this point

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched joint-specific movement module(s) in both signs at this point
            print("error: why are there unmatched joint-specific movement module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any joint-specific modules; add them back to the rematch list
        for snum in snums:
            rematchmods[snum].extend(jointspecificmods[snum])

    if handshapechangemods[1] and handshapechangemods[2]:
        # match up handshape change modules
        matchedpairs, unmatchedmodsbysign = alignbyhandshapechange(handshapechangemods)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched handshape change module(s) in both signs at this point
            print("error: why are there unmatched handshape change module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any handshape-change modules; add them back to the rematch list
        for snum in snums:
            rematchmods[snum].extend(handshapechangemods[snum])

    if othermods[1] and othermods[2]:
        # match up modules without a movement type specified
        matchedpairs, unmatchedmodsbysign = alignbycodingorder(othermods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched other movement module(s) in both signs at this point
            print("error: why are there unmatched other movement module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any other modules; add them back to the rematch list
        for snum in snums:
            rematchmods[snum].extend(othermods[snum])

    # if rematchmods[1] and rematchmods[2]:
    #     # there is at least one pair of potentially-matchable movement modules of various movement types
    #     matchedpairs, unmatchedmodsbysign = alignbycodingorder(rematchmods, matchwithnone=True)
    #     toreturn.extend(matchedpairs)
    #
    #     if unmatchedmodsbysign[1] or unmatchedmodsbysign[2]:
    #         # there should not be unmatched movement module(s) in both signs at this point
    #         print("error: why are there unmatched movement module(s) in both signs?", unmatchedmodsbysign)
    #
    # return toreturn

    return toreturn, rematchmods


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
        matchedpairs, unmatchedmodsbysign = alignbybodybasedlocation(bodymods)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched body module(s) in both signs at this point
            print("error: why are there unmatched body module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchbodymods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any body modules; add them back to the rematch list
        for snum in snums:
            rematchbodymods[snum].extend(bodymods[snum])

    if bodyanchoredmods[1] and bodyanchoredmods[2]:
        # match up body-anchored modules
        matchedpairs, unmatchedmodsbysign = alignbybodybasedlocation(bodyanchoredmods)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched body-anchored module(s) in both signs at this point
            print("error: why are there unmatched body-anchored module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchbodymods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any body-anchored modules; add them back to the rematch list
        for snum in snums:
            rematchbodymods[snum].extend(bodyanchoredmods[snum])

    if purelyspatialmods[1] and purelyspatialmods[2]:
        # match up purely spatial modules
        matchedpairs, unmatchedmodsbysign = alignbypurelyspatiallocation(purelyspatialmods)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched purely-spatial module(s) in both signs at this point
            print("error: why are there unmatched purely-spatial module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any purely-spatial modules; add them back to the rematch list
        for snum in snums:
            rematchallmods[snum].extend(purelyspatialmods[snum])

    if signingspaceonlymods[1] and signingspaceonlymods[2]:
        # match up general signing space modules
        # ... since there is no more-detailed info (because user hasn't specified either body-anchored or purely spatial
        #   as a sub-type to "signing space"), there is no way to try and align these except by coding order
        matchedpairs, unmatchedmodsbysign = alignbycodingorder(signingspaceonlymods, matchwithnone=False)
        toreturn.extend(matchedpairs)

        if unmatchedmodsbysign[1] and unmatchedmodsbysign[2]:
            # there should not be unmatched signing-space-only module(s) in both signs at this point
            print("error: why are there unmatched signing-space-only module(s) in both signs?", unmatchedmodsbysign)
        else:
            for snum in snums:
                rematchallmods[snum].extend(unmatchedmodsbysign[snum])
    else:
        # there was only one sign with any signing-space-only modules; add them back to the rematch list
        for snum in snums:
            rematchallmods[snum].extend(signingspaceonlymods[snum])

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
    else:
        # there was only one sign with any no-location-type modules; add them back to the rematch list
        for snum in snums:
            rematchallmods[snum].extend(noloctypemods[snum])

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
    else:
        # there was only one sign with any body-based modules to rematch; add them back to the rematch-all list
        for snum in snums:
            rematchallmods[snum].extend(rematchbodymods[snum])

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
    return alignbyloctreeitems_helper(bodybasedlocmodsbysign)


def alignbypurelyspatiallocation(purelyspatiallocmodsbysign):
    return alignbyloctreeitems_helper(purelyspatiallocmodsbysign)


def alignbyloctreeitems_helper(locmodsybsign):
    sign1mods = [mod for mod in locmodsybsign[1]]
    sign2mods = [mod for mod in locmodsybsign[2]]

    matchedmods = []
    unmatched = {1: [], 2: []}

    index1 = 0
    while index1 < len(sign1mods):
        mod1 = sign1mods[index1]
        mod1toplevels = locationtreetoplevelnodes(mod1.locationtreemodel)
        if mod1toplevels:

            index2 = 0
            while index2 < len(sign2mods):
                mod2 = sign2mods[index2]
                mod2toplevels = locationtreetoplevelnodes(mod2.locationtreemodel)
                if mod2toplevels:
                    if set(mod1toplevels) == set(mod2toplevels):
                        matchedmods.append((mod1, mod2))
                        sign1mods.remove(mod1)
                        sign2mods.remove(mod2)

                index2 += 1
        index1 += 1

    if sign1mods or sign2mods:
        # if there are still some of this type of module left unmatched, it's because there were no sub-type matches
        #   e.g., maybe we had two body-based location modules, but one was Head and the other was Torso
        # so just go ahead and match these types by coding order
        matchedbycodingorder, unmatched = alignbycodingorder({1: sign1mods, 2: sign2mods}, matchwithnone=False)
        matchedmods.extend(matchedbycodingorder)

    return matchedmods, unmatched


def locationtreetoplevelnodes(locationtreemodel):
    toplevelnodes = []
    root = locationtreemodel.invisibleRootItem()

    for r in range(root.rowCount()):  # top level only
        child = root.child(r, 0)
        if child is not None:
            nodetext = child.data(Qt.UserRole + udr.nodedisplayrole)
            checkstate = child.checkState()
            if checkstate in [Qt.Checked, Qt.PartiallyChecked]:
                toplevelnodes.append(nodetext)
    return toplevelnodes


# def alignbynolocation(nolocmodsbysign):
#     return [], nolocmodsbysign  # TODO


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

    # works in place
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

        # works in place
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
            # works in place
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

