from collections import defaultdict, Counter
import itertools

from PyQt5.QtCore import Qt, QObject, pyqtSignal

from lexicon.module_classes import HandConfigurationHand
from compare_signs.compare_helpers import parse_predefined_names, get_possible_bases
from constant import ModuleTypes, HAND, ARM, LEG, userdefinedroles as udr, PREDEFINED_MAP, alignmentcomplexitywarning
PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}

snums = [1, 2]

class AlignModel(QObject):

    def __init__(self, sign1, sign2, **kwargs):
        super().__init__(**kwargs)
        self.sign1 = sign1
        self.sign2 = sign2
        self.movmods_aligned = []
        self.locmods_aligned = []

    def alignmodules(self, moduletype):
        if moduletype == ModuleTypes.SIGNTYPE:
            return [(self.sign1.signtype, self.sign2.signtype)], ""
        else:
            modulesbysign = {
                1: list(self.sign1.getmoduledict(moduletype).values()),
                2: list(self.sign2.getmoduledict(moduletype).values())
            }
            signswiththismodule = whichsignshavemodulesoftype(modulesbysign)

            if signswiththismodule == [1]:
                # no need to try and align modules; this module type only exists in sign1
                return [(mod, None) for mod in modulesbysign[1]], ""
            elif signswiththismodule == [2]:
                # no need to try and align modules; this module type only exists in sign2
                return [(None, mod) for mod in modulesbysign[2]], ""
            elif signswiththismodule == []:
                # no need to try and align modules; this module type isn't used in sign1 or sign2
                return [], ""
            # else signswiththismodule == [1, 2]
            # try to align them; continue below

            # now we are at the point where we know that the module type in questions exists in both sign1 and sign2;
            #   we have to decide how to align them

            if moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.ORIENTATION,
                              ModuleTypes.HANDCONFIG]:
                # i. First 'align by hand.' That is, try to align hand1 modules from sign1 to hand1 modules from sign2.
                #   If sign1 and sign2 each have only hand1 modules, or each have only hand2 modules, then proceed to the next step of alignment.
                #   If sign1 has both hand1 and hand2 modules, while sign2 has only hand1 modules (or vice versa), then align the hand1 modules only,
                #   and leave all hand2 modules unmatched.
                #   If sign1 has only hand1 modules, and sign2 has only hand2 modules, then this is the only time that non-matching hand modules can be aligned.
                matchedmods, warningstring = self.alignbyarticulator(modulesbysign, moduletype)
                return matchedmods, warningstring
            elif moduletype in [ModuleTypes.RELATION, ModuleTypes.NONMANUAL]:
                # neither of these module types has articulators specified, so we can skip alignbyarticulator()
                # TODO implement (waiting for further intructions from Kathleen on nonmanuals)
                matched1, unmatched, warningstring = self.alignmodules_helper(modulesbysign, moduletype)
                matched2, unmatched = self.alignbycodingorder(unmatched, matchwithnone=True)
                return matched1 + matched2, warningstring

    # parameters:
    #   - modulesbysign is a dict of {signnum --> [list of modules of specified type from this signnum that need to be aligned]}
    #   - moduletype is the specified type that defines the contents of the first argument
    def alignbyarticulator(self, modulesbysign, moduletype):
        if len(modulesbysign[1]) == len(modulesbysign[2]) == 1:
            return [(modulesbysign[1][0], modulesbysign[2][0])], ""

        matchedmods = []
        warningstrings = []

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
                    alignedmodules, unmatched, warningstring = self.alignmodules_helper({
                        1: sign1modsbyarticulator[art][artnum],
                        2: sign2modsbyarticulator[art][artnum]
                    },
                    moduletype)
                    if warningstring not in warningstrings:
                        warningstrings.append(warningstring)
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
                    alignedmodules, unmatched, warningstring = self.alignmodules_helper({
                        1: sign1modsbyarticulator[art][artnum],
                        2: sign2modsbyarticulator[art][3]
                    },
                    moduletype)
                    if warningstring not in warningstrings:
                        warningstrings.append(warningstring)
                    # save aligned modules to be returned at the end of the function
                    matchedmods.extend(alignedmodules)
                    # put any unmatched ones back into the pot
                    sign1modsbyarticulator[art][artnum] = unmatched[1]
                    sign2modsbyarticulator[art][3] = unmatched[2]
                if sign1modsbyarticulator[art][3] and sign2modsbyarticulator[art][artnum]:
                    # the articulators are a subset match (eg, H1&2-H2 or L1&2-L1) so try and align whatever modules are in those lists
                    alignedmodules, unmatched, warningstring = self.alignmodules_helper({
                        1: sign1modsbyarticulator[art][3],
                        2: sign2modsbyarticulator[art][artnum]
                    },
                    moduletype)
                    if warningstring not in warningstrings:
                        warningstrings.append(warningstring)
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
            alignedmodules, unmatched, warningstring = self.alignmodules_helper(stillunmatchedwithinarticulator, moduletype)
            if warningstring not in warningstrings:
                warningstrings.append(warningstring)
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
                        # the articulators are a near-perfect match (eg, H1-A1 or L1&2-H1&2)
                        #   so try and align whatever modules are in those lists
                        alignedmodules, unmatched, warningstring = self.alignmodules_helper({
                            1: sign1modsbyarticulator[arttype1][artnum],
                            2: sign2modsbyarticulator[arttype2][artnum]
                        },
                        moduletype)
                        if warningstring not in warningstrings:
                            warningstrings.append(warningstring)
                        # save aligned modules to be returned at the end of the function
                        matchedmods.extend(alignedmodules)
                        # put any unmatched ones back into the pot
                        sign1modsbyarticulator[arttype1][artnum] = unmatched[1]
                        sign2modsbyarticulator[arttype2][artnum] = unmatched[2]


                for artnum in [1, 2]:
                    if sign1modsbyarticulator[arttype1][artnum] and sign2modsbyarticulator[arttype2][3]:
                        # the articulators are a near-subset match (eg, L1-H1&2 or H2-A1&2)
                        #   so try and align whatever modules are in those lists
                        alignedmodules, unmatched, warningstring = self.alignmodules_helper({
                            1: sign1modsbyarticulator[arttype1][artnum],
                            2: sign2modsbyarticulator[arttype2][3]
                        },
                        moduletype)
                        if warningstring not in warningstrings:
                            warningstrings.append(warningstring)
                        # save aligned modules to be returned at the end of the function
                        matchedmods.extend(alignedmodules)
                        # put any unmatched ones back into the pot
                        sign1modsbyarticulator[arttype1][artnum] = unmatched[1]
                        sign2modsbyarticulator[arttype2][3] = unmatched[2]
                    if sign1modsbyarticulator[arttype1][3] and sign2modsbyarticulator[arttype2][artnum]:
                        # the articulators are a subset match (eg, H1&2-L2 or L1&2-A1)
                        #   so try and align whatever modules are in those lists
                        alignedmodules, unmatched, warningstring = self.alignmodules_helper({
                            1: sign1modsbyarticulator[arttype1][3],
                            2: sign2modsbyarticulator[arttype2][artnum]
                        },
                        moduletype)
                        if warningstring not in warningstrings:
                            warningstrings.append(warningstring)
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

                alignedmodules, unmatched, warningstring = self.alignmodules_helper(stillunmatchedwithinarticulatorpair, moduletype)
                if warningstring not in warningstrings:
                    warningstrings.append(warningstring)
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

        # TODO KV at this point any unmatched modules should be... aligned by coding order? left unmatched? ... it is tres confusing
        # TODO KV at this point will as much be aligned as possible? I think so... but just in case should we try by coding order?
        alignedmodules, unmatched = self.alignbycodingorder(allremainingunmatchedmods, matchwithnone=True)
        matchedmods.extend(alignedmodules)

        return matchedmods, "\n".join(warningstrings)  # all the aligned modules, some possibly with 'none'

    def alignmodules_helper(self, modulesbysign, moduletype):
        if moduletype == ModuleTypes.MOVEMENT:
            # ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
            #   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
            #   while sign 2 has only joint-specific movement, align the two joint-specific movements,
            #   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
            #   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
            #   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
            #   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
            #   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
            modsalignedbymovtype, unmatched = self.alignbymovement(modulesbysign)
            #   If modules still can't be aligned, align by coding order.
            modsalignedbycodingorder, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            self.movmods_aligned.extend(modsalignedbymovtype + modsalignedbycodingorder)
            return modsalignedbymovtype + modsalignedbycodingorder, unmatched, ""
        elif moduletype == ModuleTypes.LOCATION:
            # ii. After aligning by hand, try to align by general location type (body-anchored or signing space)
            #   -- e.g., if sign1 has both body-anchored and signing space locations, and sign2 has only a body-anchored location,
            #   then align the body-anchored modules and leave the signing-space module unmatched.
            #   If there are multiple locations of the same type (e.g., multiple body-anchored locations),
            #   use the uppermost (in the tree) location specifications to align
            #   (e.g., align two head-locations rather than a head location with a torso location, if possible).
            modsalignedbyloctype, unmatched = self.alignbylocation(modulesbysign)
            #   If modules still can't be aligned, align by coding order.
            modsalignedbycodingorder, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            self.locmods_aligned.extend(modsalignedbyloctype + modsalignedbycodingorder)
            return modsalignedbyloctype + modsalignedbycodingorder, unmatched, ""
        elif moduletype == ModuleTypes.ORIENTATION:
            # ii. After aligning by hand, align by palm orientation if possible (e.g. align two palm-up modules).
            # modsalignedbypalm, unmatched = alignbypalmori(modulesbysign)
            modsalignedbypalm, unmatched = self.alignbyorientation(modulesbysign, focus='palm', level='specific')
            #   If not possible, align by finger root direction.
            # modsalignedbyfingerroot, unmatched = alignbyfingerrootdir(unmatched)
            modsalignedbyfingerroot, unmatched = self.alignbyorientation(unmatched, focus='root', level='specific')
            #   If still not possible, align by coding order.
            modsalignedbycodingorder, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            return modsalignedbypalm + modsalignedbyfingerroot + modsalignedbycodingorder, unmatched, ""
        elif moduletype == ModuleTypes.HANDCONFIG:
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
            modsalignedbyhs, unmatched, warningstring = self.alignbyhandshape(modulesbysign)
            # v. If there are still unaligned handshapes, align by coding order.
            modsalignedbycodingorder, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            return modsalignedbyhs + modsalignedbycodingorder, unmatched, warningstring
        elif moduletype == ModuleTypes.RELATION:
            modsalignedbyrelation, unmatched = self.alignbyrelation(modulesbysign)
            modsalignedbycodingorder, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            return modsalignedbyrelation + modsalignedbycodingorder, unmatched, ""
        elif moduletype == ModuleTypes.NONMANUAL:
            modsalignedbynonman, unmatched = self.alignbynonmanual(modulesbysign)
            modsalignedbycodingorder, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            return modsalignedbynonman + modsalignedbycodingorder, unmatched, ""

    # TODO this currently uses *solely* uniqueid (which is a timestamp) to determine coding order within the list of
    #   modules for each sign. If for some reason we need it to refer to the module numbers themselves (eg Loc1, Loc2) more
    #   explicitly, then this function will also need moduletype & sign1 & sign2 (or sign1 & 2 modulenumberdicts) as input too
    # parameters:
    #   - modulesbysign is a dict of {signnum --> [list of modules from this signnum that need to be aligned]}
    #   - matchwithnone is a boolean that specifies whether any leftover modules (in case of one sign having more than the other)
    #       should be (if True) paired with "None" and added to the matched list or (if False) not paired and added to the unmatched list
    def alignbycodingorder(self, modulesbysign, matchwithnone=False):
        if (len(modulesbysign[1]) == 0 or len(modulesbysign[2]) == 0) and not matchwithnone:
            return [], modulesbysign
        elif len(modulesbysign[1]) == len(modulesbysign[2]) == 1:
            return [(modulesbysign[1][0], modulesbysign[2][0])], {1: [], 2: []}

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

    # try to match as specifically as possible (eg vertical/up with vertical/up)
    # any leftovers, try to match at least to the general direction (eg vertical/up with vertical/down or just vertical)
    # any leftovers, punt back up to next step
    # parameters:
    #   - orimodsbysign is a dict of {signnum --> [list of orientation modules from this signnum that need to be aligned]}
    #   - focus is a string that specifies which element of the orientation module to focus on: 'palm' or (finger) 'root'
    #   - level is a string that specifies how loosely directions should be matched: 'specific' (eg only match down/down) or 'general' (eg could match vertical/down)
    def alignbyorientation(self, orimodsbysign, focus, level='specific'):
        if len(orimodsbysign[1]) == 0 or len(orimodsbysign[2]) == 0:
            return [], orimodsbysign
        elif len(orimodsbysign[1]) == len(orimodsbysign[2]) == 1:
            return [(orimodsbysign[1][0], orimodsbysign[2][0])], {1: [], 2: []}

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
            morematchedmods, unmatchedmods = self.alignbyorientation(unmatchedmods, focus, level='general')
            matchedmods.extend(morematchedmods)

        return matchedmods, unmatchedmods

    # parameters:
    #   - nonmadmodsbysign is a dict of {signnum --> [list of nonmanual modules from this signnum that need to be aligned]}
    def alignbynonmanual(self, nonmanmodsbysign):
        if len(nonmanmodsbysign[1]) == 0 or len(nonmanmodsbysign[2]) == 0:
            return [], nonmanmodsbysign
        elif len(nonmanmodsbysign[1]) == len(nonmanmodsbysign[2]) == 1:
            return [(nonmanmodsbysign[1][0], nonmanmodsbysign[2][0])], {1: [], 2: []}

        # TODO implement - waiting for more info from Kathleen
        return self.alignbycodingorder(nonmanmodsbysign)

    # 1. At any point where we are left with just two relation modules, one in each sign, that are otherwise not aligned, align them.
    # 2. If there are multiple modules that *could* be aligned at some stage, but we don’t have enough information to
    #   differentiate them yet, split them off into their own group and proceed with the steps of alignment separately in each group.
    # 3. Align any relation modules that are associated with Location or Movement modules that are themselves aligned with each other.
    #   This means that aligning location and movement modules needs to happen before the alignment of relation modules.
    #       i. If there is more than one relation module associated with aligned anchor modules, then first align by “X” value.
    #       ii. If not possible to align by “X” values, then align by presence/absence of contact.
    # 4. If there are still multiple unaligned modules, align by coding order.
    # 5. If you’re trying to align Relation modules that do not have aligned anchor modules, then start by trying to align by X,
    #   then align by Y, then align by contact, then align by coding order, then align any leftover modules.
    # parameters:
    #   - relmodsbysign is a dict of {signnum --> [list of relation modules from this signnum that need to be aligned]}
    def alignbyrelation(self, relmodsbysign):
        if len(relmodsbysign[1]) == 0 or len(relmodsbysign[2]) == 0:
            return [], relmodsbysign
        elif len(relmodsbysign[1]) == len(relmodsbysign[2]) == 1:
            return [(relmodsbysign[1][0], relmodsbysign[2][0])], {1: [], 2: []}

        matchedmods = []
        unmatchedmods = {1: [], 2: []}

        modstomatch = {1: [], 2: []}

        # categorize based on whether there are associated (Loc or Mov) modules
        relmodswithexistingmods = {1: [], 2: []}
        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationy.existingmodule and len(relmod.relationy.linkedmoduleids) > 0:
                    relmodswithexistingmods[snum].append(relmod)
                else:
                    modstomatch[snum].append(relmod)

        # align relation modules that do have linked (loc or mov) modules
        matchedbyexistingmod, unmatchedbyexistingmod = self.alignbyrel_existingmod(relmodswithexistingmods)
        matchedmods.extend(matchedbyexistingmod)
        
        # align relation modules that do not have linked modules
        matchedbyX, unmatchedbyX = self.alignbyrel_x(modstomatch, "Y")
        matchedmods.extend(matchedbyX)
        matchedbyY, unmatchedbyY = self.alignbyrel_y(unmatchedbyX)
        matchedmods.extend(matchedbyY)
        matchedbycontact, unmatchedbycontact = self.alignbyrel_contact(unmatchedbyY)
        matchedmods.extend(matchedbycontact)
        matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder(unmatchedbycontact, matchwithnone=False)

        # recombine and rematch any leftovers from the above two categories
        torematch = {1: unmatchedbyexistingmod[1]+unmatchedbycodingorder[1], 2: unmatchedbyexistingmod[2]+unmatchedbycodingorder[2]}
        matchedleftovers, unmatchedleftovers = self.alignbycodingorder(torematch)
        matchedmods.extend(matchedleftovers)
        unmatchedmods = concatenate_dictlists(unmatchedmods, unmatchedleftovers)

        return matchedmods, unmatchedmods

    # parameters:
    #   - relmodsbysign is a dict of {signnum --> [list of relation modules from this signnum that need to be aligned]}
    def alignbyrel_existingmod(self, relmodsbysign):
        if len(relmodsbysign[1]) == 0 or len(relmodsbysign[2]) == 0:
            return [], relmodsbysign
        elif len(relmodsbysign[1]) == len(relmodsbysign[2]) == 1:
            return [(relmodsbysign[1][0], relmodsbysign[2][0])], {1: [], 2: []}

        matchedmods = []
        unmatchedmods = {1: [], 2: []}

        # categorize based on whether the associated module is a Location module(s) or a Movement module(s)
        relmodswithlocmods = {1: [], 2: []}
        relmodswithmovmods = {1: [], 2: []}
        # relmodswithnospecifiedmods = {1: [], 2: []}
        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationy.linkedmoduletype == ModuleTypes.LOCATION:
                    relmodswithlocmods[snum].append(relmod)
                elif relmod.relationy.linkedmoduletype == ModuleTypes.MOVEMENT:
                    relmodswithmovmods[snum].append(relmod)
                else:
                    # no specified linkedmoduletype -- this function shouldn't encounter such a module, but
                    #   if it does then just add it to the unmatched dictionary
                    unmatchedmods[snum].append(relmod)

        # get the lists of already-aligned movement and location modules
        for modtype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION]:
            if modtype == ModuleTypes.MOVEMENT:
                if not self.movmods_aligned:
                    anchormods_aligned_s1 = []
                    anchormods_aligned_s2 = []
                else:
                    anchormods_aligned_s1, anchormods_aligned_s2 = tuple([list(entry) for entry in zip(*self.movmods_aligned)])
                relmods_withthistypeofanchor = relmodswithmovmods
            else:
                if not self.locmods_aligned:
                    anchormods_aligned_s1 = []
                    anchormods_aligned_s2 = []
                else:
                    anchormods_aligned_s1, anchormods_aligned_s2 = tuple([list(entry) for entry in zip(*self.locmods_aligned)])
                relmods_withthistypeofanchor = relmodswithlocmods

            matchedbyanchortype, unmatchedbyanchortype = self.alignbyrel_existingmod_oneanchortype(relmods_withthistypeofanchor, anchormods_aligned_s1, anchormods_aligned_s2)
            matchedmods.extend(matchedbyanchortype)
            # use coding order to align any remaining relation modules that are linked to an anchor module of this type
            matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder(unmatchedbyanchortype, matchwithnone=False)
            matchedmods.extend(matchedbycodingorder)
            unmatchedmods = concatenate_dictlists(unmatchedmods, unmatchedbycodingorder)

        # use coding order to align any remaining relation modules that are linked to an anchor module (of any type)
        matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder(unmatchedmods, matchwithnone=False)
        matchedmods.extend(matchedbycodingorder)
        return matchedmods, unmatchedbycodingorder

    # parameters:
    #   - relmodsbysign is a dict of {signnum --> [list of relation modules *with one type of anchor* from this signnum that need to be aligned]}
    #   - anchormods_aligned_s1 and anchormods_aligned_s2 are parallel lists in which item n in the first list is the anchor module that was
    #       aligned with the anchor module that is item n in the second list
    def alignbyrel_existingmod_oneanchortype(self, relmodsbysign, anchormods_aligned_s1, anchormods_aligned_s2):
        matchedmods = []

        anchormodIDs_aligned_s1 = [mod.uniqueid for mod in anchormods_aligned_s1]
        anchormodIDs_aligned_s2 = [mod.uniqueid for mod in anchormods_aligned_s2]

        s1_linkedmoduleids = [sorted([id for id in s1_relmod.relationy.linkedmoduleids if id != 0.0]) for s1_relmod in relmodsbysign[1]]
        s2_linkedmoduleids = [sorted([id for id in s2_relmod.relationy.linkedmoduleids if id != 0.0]) for s2_relmod in relmodsbysign[2]]

        def anchormodIDsarealigned(anchormodIDs_of_one_S1relmod, anchormodIDs_of_one_S2relmod):
            if isinstance(anchormodIDs_of_one_S1relmod, list) and isinstance(anchormodIDs_of_one_S2relmod, list):
                if len(anchormodIDs_of_one_S1relmod) != len(anchormodIDs_of_one_S2relmod):
                    return False
                else:
                    aligned_pairs = zip(anchormodIDs_aligned_s1, anchormodIDs_aligned_s2)
                    IDs_are_aligned = [pair_to_test in aligned_pairs for pair_to_test in zip(anchormodIDs_of_one_S1relmod, anchormodIDs_of_one_S2relmod)]
                    return all(IDs_are_aligned)
            return False

        idx1 = 0
        while idx1 < len(s1_linkedmoduleids):
            anchormodIDs_of_one_S1relmod = s1_linkedmoduleids[idx1]
            if len(anchormodIDs_of_one_S1relmod) > 0:
                s1relmodindices_withtheseanchors = [i for i, anchorIDs in enumerate(s1_linkedmoduleids) if anchorIDs == anchormodIDs_of_one_S1relmod]
                s2relmodindices_withalignedanchors = [i for i, anchorIDs in enumerate(s2_linkedmoduleids) if anchormodIDsarealigned(anchormodIDs_of_one_S1relmod, anchorIDs)]
                if len(s2relmodindices_withalignedanchors) == 0:
                    # no exact alignments with the anchor modules from s1
                    idx1 += 1
                elif len(s1relmodindices_withtheseanchors) == len(s2relmodindices_withalignedanchors) == 1:
                    alignedidx_s2 = s2relmodindices_withalignedanchors[0]
                    matchedmods.append((relmodsbysign[1].pop(idx1),
                                       relmodsbysign[2].pop(alignedidx_s2)))
                    s1_linkedmoduleids.pop(idx1)
                    s2_linkedmoduleids.pop(alignedidx_s2)
                    # don't increment idx1, because the next item in the list will have moved down into the same spot we're in
                else:
                    # s1 and/or s2 have more than one rel mod with this exact set of anchor modules
                    # align within the perfectly matched anchor mods; increment if necessary
                    matchedbyx, unmatchedbyx = self.alignbyrel_x({1: [relmod for i, relmod in enumerate(relmodsbysign[1])
                                                                      if i in s1relmodindices_withtheseanchors],
                                                                  2: [relmod for i, relmod in enumerate(relmodsbysign[2])
                                                                      if i in s2relmodindices_withalignedanchors]},
                                                                 "contact type")
                    matchedmods.extend(matchedbyx)
                    for matched_1, matched_2 in matchedbyx:
                        try:
                            remove_idx1 = relmodsbysign[1].index(matched_1)
                            relmodsbysign[1].pop(remove_idx1)
                            s1_linkedmoduleids.pop(remove_idx1)
                        except ValueError:
                            pass
                        try:
                            remove_idx2 = relmodsbysign[2].index(matched_2)
                            relmodsbysign[2].pop(remove_idx2)
                            s2_linkedmoduleids.pop(remove_idx2)
                        except ValueError:
                            pass

                    # any modules that didn't manage to get matched by X, try to match by contact
                    matchedbycontact, unmatchedbycontact = self.alignbyrel_contact({snum: relmodsbysign[snum] for snum in snums})
                    matchedmods.extend(matchedbycontact)
                    for matched_1, matched_2 in matchedbycontact:
                        try:
                            remove_idx1 = relmodsbysign[1].index(matched_1)
                            relmodsbysign[1].pop(remove_idx1)
                            s1_linkedmoduleids.pop(remove_idx1)
                        except ValueError:
                            pass
                        try:
                            remove_idx2 = relmodsbysign[2].index(matched_2)
                            relmodsbysign[2].pop(remove_idx2)
                            s2_linkedmoduleids.pop(remove_idx2)
                        except ValueError:
                            pass

                    idx1 += 1
            else:
                # this S1 relation module doesn't have any linked anchor modules
                idx1 += 1

        matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder(relmodsbysign, matchwithnone=False)
        matchedmods.extend(matchedbycodingorder)
        return matchedmods, unmatchedbycodingorder

    # - first find identical matches (e.g. H2 = H2, Both arms = Both arms, etc.);
    #   “other” counts as an exact match with “other” regardless of specified content
    # - then allow “Arm1” to match “Both arms” and “Leg1” to match “Both legs”
    # - then allow “Arm2” to match “Both arms” and “Leg2” to match “Both legs”
    # - if still no match (or multiple possible matches), move on to align-by-contact, instead of continuing trying to match Y-values
    # parameters:
    #   - relmodsbysign is a dict of {signnum --> [list of relation modules from this signnum that need to be aligned]}
    def alignbyrel_y(self, relmodsbysign):
        if len(relmodsbysign[1]) == 0 or len(relmodsbysign[2]) == 0:
            return [], relmodsbysign
        elif len(relmodsbysign[1]) == len(relmodsbysign[2]) == 1:
            return [(relmodsbysign[1][0], relmodsbysign[2][0])], {1: [], 2: []}

        matchedmods = []

        modsbysignbyrelY = {1: {}, 2: {}}
        for snum in modsbysignbyrelY.keys():
            modsbysignbyrelY[snum] = {k:[] for k in ['h1', 'h2', 'hboth', 'arm1', 'arm2', 'aboth', 'leg1', 'leg2', 'lboth', 'existingmodule', 'other']}

        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationy.h2:
                    modsbysignbyrelY[snum]['h2'].append(relmod)
                elif relmod.relationy.arm1:
                    modsbysignbyrelY[snum]['arm1'].append(relmod)
                elif relmod.relationy.arm2:
                    modsbysignbyrelY[snum]['arm2'].append(relmod)
                elif relmod.relationy.aboth:
                    modsbysignbyrelY[snum]['aboth'].append(relmod)
                elif relmod.relationy.leg1:
                    modsbysignbyrelY[snum]['leg1'].append(relmod)
                elif relmod.relationy.leg2:
                    modsbysignbyrelY[snum]['leg2'].append(relmod)
                elif relmod.relationy.lboth:
                    modsbysignbyrelY[snum]['lboth'].append(relmod)
                elif relmod.relationy.existingmodule:
                    modsbysignbyrelY[snum]['existingmodule'].append(relmod)
                elif relmod.relationy.other:
                    modsbysignbyrelY[snum]['other'].append(relmod)

        # align as much as possible within each relation Y type
        for relytype in modsbysignbyrelY[snum].keys():
            # we can get a bit more specific if the relation Y type is "existing module"...
            #   align *within* existing module types (ie, location or movement)
            if relytype == 'existingmodule':
                for modtype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION]:
                    modsbysignbythismodtype = {
                        snum: [rmod for rmod in modsbysignbyrelY[snum][relytype] if rmod.relationy.linkedmoduletype == modtype]
                        for snum in snums
                    }
                    # if multiple possible matches, align by contact type
                    matchedbycontact, unmatchedbycontact = self.alignbyrel_contact({snum:modsbysignbythismodtype[snum] for snum in snums})
                    matchedmods.extend(matchedbycontact)
                for matched_1, matched_2 in matchedbycontact:
                    if matched_1 in relmodsbysign[1]:
                        relmodsbysign[1].remove(matched_1)
                        modsbysignbyrelY[1][relytype].remove(matched_1)
                    if matched_2 in relmodsbysign[2]:
                        relmodsbysign[2].remove(matched_2)
                        modsbysignbyrelY[2][relytype].remove(matched_2)

            # if multiple possible matches, align by contact type
            matchedbycontact, unmatchedbycontact = self.alignbyrel_contact({snum:modsbysignbyrelY[snum][relytype] for snum in snums})
            matchedmods.extend(matchedbycontact)
            for matched_1, matched_2 in matchedbycontact:
                if matched_1 in relmodsbysign[1]:
                    relmodsbysign[1].remove(matched_1)
                if matched_2 in relmodsbysign[2]:
                    relmodsbysign[2].remove(matched_2)

        # re-group for second round
        modsbysignbyrelY = {1: {}, 2: {}}
        for snum in modsbysignbyrelY.keys():
            modsbysignbyrelY[snum] = {k:[] for k in ['a1_or_both', 'l1_or_both']}
        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationy.arm1 or relmod.relationy.aboth:
                    modsbysignbyrelY[snum]['a1_or_both'].append(relmod)
                elif relmod.relationy.leg1 or relmod.relationy.lboth:
                    modsbysignbyrelY[snum]['l1_or_both'].append(relmod)

        # if any leftovers, match R1 to both Rs, where R = any of the articulators
        # if multiple possible matches, align by contact type

        # align as much as possible within each relation Y type
        for relytype in modsbysignbyrelY[snum].keys():
            # if multiple possible matches, align by contact type
            matchedbycontact, unmatchedbycontact = self.alignbyrel_contact({snum: modsbysignbyrelY[snum][relytype] for snum in snums})
            matchedmods.extend(matchedbycontact)
        for matched_1, matched_2 in matchedbycontact:
            if matched_1 in relmodsbysign[1]:
                relmodsbysign[1].remove(matched_1)
                modsbysignbyrelY[1][relytype].remove(matched_1)
            if matched_2 in relmodsbysign[2]:
                relmodsbysign[2].remove(matched_2)
                modsbysignbyrelY[2][relytype].remove(matched_2)

        # re-group for third round
        modsbysignbyrelY = {1: {}, 2: {}}
        for snum in modsbysignbyrelY.keys():
            modsbysignbyrelY[snum] = {k:[] for k in ['a2_or_both', 'l2_or_both']}
        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationy.arm2 or relmod.relationy.aboth:
                    modsbysignbyrelY[snum]['a2_or_both'].append(relmod)
                elif relmod.relationy.leg2 or relmod.relationy.lboth:
                    modsbysignbyrelY[snum]['l2_or_both'].append(relmod)

        # if any leftovers, match R2 to voth R2, where R = any of the articulators
        # if multiple possible matches, align by contact type

        # align as much as possible within each relation Y type
        for relytype in modsbysignbyrelY[snum].keys():
            # if multiple possible matches, align by contact type
            matchedbycontact, unmatchedbycontact = self.alignbyrel_contact({snum: modsbysignbyrelY[snum][relytype] for snum in snums})
            matchedmods.extend(matchedbycontact)
        for matched_1, matched_2 in matchedbycontact:
            if matched_1 in relmodsbysign[1]:
                relmodsbysign[1].remove(matched_1)
            if matched_2 in relmodsbysign[2]:
                relmodsbysign[2].remove(matched_2)

        return matchedmods, relmodsbysign

    # - first find identical matches (e.g. H1 = H1, Both hands = Both hands, etc.);
    #   “other” counts as an exact match with “other” regardless of specified content
    # - then allow “H1” to match “Both hands,” “Arm1” to match “Both arms,” and “Leg1” to match “Both legs”
    # - then allow “H2” to match “Both hands,” “Arm2” to match “Both arms,” and “Leg2” to match “Both legs”
    # - if still no match (or multiple possible matches), move on to next category (whether contact or relation Y),
    #   instead of continuing trying to match X-values
    # parameters:
    #   - relmodsbysign is a dict of {signnum --> [list of relation modules from this signnum that need to be aligned]}
    #   - nextcategory = "Y" or "contact type"
    def alignbyrel_x(self, relmodsbysign, nextcategory):
        if len(relmodsbysign[1]) == 0 or len(relmodsbysign[2]) == 0:
            return [], relmodsbysign
        elif len(relmodsbysign[1]) == len(relmodsbysign[2]) == 1:
            return [(relmodsbysign[1][0], relmodsbysign[2][0])], {1: [], 2: []}

        matchedmods = []

        modsbysignbyrelX = {1: {}, 2: {}}
        for snum in modsbysignbyrelX.keys():
            modsbysignbyrelX[snum] = {k:[] for k in ['h1', 'h2', 'hboth', 'arm1', 'arm2', 'aboth', 'leg1', 'leg2', 'lboth', 'other']}

        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationx.h1:
                    modsbysignbyrelX[snum]['h1'].append(relmod)
                elif relmod.relationx.h2:
                    modsbysignbyrelX[snum]['h2'].append(relmod)
                elif relmod.relationx.hboth:
                    modsbysignbyrelX[snum]['hboth'].append(relmod)
                elif relmod.relationx.arm1:
                    modsbysignbyrelX[snum]['arm1'].append(relmod)
                elif relmod.relationx.arm2:
                    modsbysignbyrelX[snum]['arm2'].append(relmod)
                elif relmod.relationx.aboth:
                    modsbysignbyrelX[snum]['aboth'].append(relmod)
                elif relmod.relationx.leg1:
                    modsbysignbyrelX[snum]['leg1'].append(relmod)
                elif relmod.relationx.leg2:
                    modsbysignbyrelX[snum]['leg2'].append(relmod)
                elif relmod.relationx.lboth:
                    modsbysignbyrelX[snum]['lboth'].append(relmod)
                elif relmod.relationx.other:
                    modsbysignbyrelX[snum]['other'].append(relmod)

        # align as much as possible within each relation X type
        for relxtype in modsbysignbyrelX[snum].keys():
            # if multiple possible matches, align by next category down
            if nextcategory == "contact type":
                matchedbynext, unmatchedbynext = self.alignbyrel_contact({snum:modsbysignbyrelX[snum][relxtype] for snum in snums})
            elif nextcategory == "Y":
                matchedbynext, unmatchedbynext = self.alignbyrel_y({snum:modsbysignbyrelX[snum][relxtype] for snum in snums})
            else:
                matchedbynext = []
                unmatchedbynext = {snum:modsbysignbyrelX[snum][relxtype] for snum in snums}
            matchedmods.extend(matchedbynext)
            matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder(unmatchedbynext)
            matchedmods.extend(matchedbycodingorder)
            for matched_1, matched_2 in matchedbynext+matchedbycodingorder:
                if matched_1 in relmodsbysign[1]:
                    relmodsbysign[1].remove(matched_1)
                if matched_2 in relmodsbysign[2]:
                    relmodsbysign[2].remove(matched_2)

        # re-group for second round
        modsbysignbyrelX = {1: {}, 2: {}}
        for snum in modsbysignbyrelX.keys():
            modsbysignbyrelX[snum] = {k:[] for k in ['h1_or_both', 'a1_or_both', 'l1_or_both']}
        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationx.h1 or relmod.relationx.hboth:
                    modsbysignbyrelX[snum]['h1_or_both'].append(relmod)
                elif relmod.relationx.arm1 or relmod.relationx.aboth:
                    modsbysignbyrelX[snum]['a1_or_both'].append(relmod)
                elif relmod.relationx.leg1 or relmod.relationx.lboth:
                    modsbysignbyrelX[snum]['l1_or_both'].append(relmod)

        # if any leftovers, match R1 to both Rs, where R = any of the articulators
        # if multiple possible matches, align by next category down

        # align as much as possible within each relation X type
        for relxtype in modsbysignbyrelX[snum].keys():
            # if multiple possible matches, align by next category down
            if nextcategory == "contact type":
                matchedbynext, unmatchedbynext = self.alignbyrel_contact({snum: modsbysignbyrelX[snum][relxtype] for snum in snums})
            elif nextcategory == "Y":
                matchedbynext, unmatchedbynext = self.alignbyrel_y({snum: modsbysignbyrelX[snum][relxtype] for snum in snums})
            else:
                matchedbynext = []
                unmatchedbynext = {snum: modsbysignbyrelX[snum][relxtype] for snum in snums}
            matchedmods.extend(matchedbynext)
            for matched_1, matched_2 in matchedbynext:
                if matched_1 in relmodsbysign[1]:
                    relmodsbysign[1].remove(matched_1)
                if matched_2 in relmodsbysign[2]:
                    relmodsbysign[2].remove(matched_2)

        # re-group for third round
        modsbysignbyrelX = {1: {}, 2: {}}
        for snum in modsbysignbyrelX.keys():
            modsbysignbyrelX[snum] = {k:[] for k in ['h2_or_both', 'a2_or_both', 'l2_or_both']}
        for snum in snums:
            for relmod in relmodsbysign[snum]:
                if relmod.relationx.h2 or relmod.relationx.hboth:
                    modsbysignbyrelX[snum]['h2_or_both'].append(relmod)
                elif relmod.relationx.arm2 or relmod.relationx.aboth:
                    modsbysignbyrelX[snum]['a2_or_both'].append(relmod)
                elif relmod.relationx.leg2 or relmod.relationx.lboth:
                    modsbysignbyrelX[snum]['l2_or_both'].append(relmod)

        # if any leftovers, match R2 to both Rs, where R = any of the articulators
        # if multiple possible matches, align by next category down

        # align as much as possible within each relation X type
        for relxtype in modsbysignbyrelX[snum].keys():
            # if multiple possible matches, align by next category down
            if nextcategory == "contact type":
                matchedbynext, unmatchedbynext = self.alignbyrel_contact({snum: modsbysignbyrelX[snum][relxtype] for snum in snums})
            elif nextcategory == "Y":
                matchedbynext, unmatchedbynext = self.alignbyrel_y({snum: modsbysignbyrelX[snum][relxtype] for snum in snums})
            else:
                matchedbynext = []
                unmatchedbynext = {snum: modsbysignbyrelX[snum][relxtype] for snum in snums}
            matchedmods.extend(matchedbynext)
            for matched_1, matched_2 in matchedbynext:
                if matched_1 in relmodsbysign[1]:
                    relmodsbysign[1].remove(matched_1)
                if matched_2 in relmodsbysign[2]:
                    relmodsbysign[2].remove(matched_2)

        return matchedmods, relmodsbysign

    # align by presence/absence of contact:
    #   - "contact" matches "contact" and "no contact" matches "no contact"
    #   - if contact is unspecified, then this is not a match / would be skipped and gone on to the next level
    # parameters:
    #   - relmodsbysign is a dict of {signnum --> [list of relation modules from this signnum that need to be aligned]}
    def alignbyrel_contact(self, relmodsbysign):
        if len(relmodsbysign[1]) == 0 or len(relmodsbysign[2]) == 0:
            return [], relmodsbysign
        elif len(relmodsbysign[1]) == len(relmodsbysign[2]) == 1:
            return [(relmodsbysign[1][0], relmodsbysign[2][0])], {1: [], 2: []}

        contacttypes = [True, False]
        matchedmods = []
        unmatchedmods = {1: [], 2: []}

        modsbysignbycontact = {1: {}, 2: {}}
        for snum in modsbysignbycontact.keys():
            modsbysignbycontact[snum] = {k:[] for k in contacttypes}

        for snum in snums:
            modsbysignbycontact[snum] = {k:[relmod for relmod in relmodsbysign[snum] if relmod.contactrel.contact == k] for k in contacttypes}
            unmatchedmods[snum].extend([relmod for relmod in relmodsbysign[snum] if relmod.contactrel.contact is None])

        # align as much as possible within each contact type
        for contacttype in contacttypes:
            matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder({snum:modsbysignbycontact[snum][contacttype] for snum in snums})
            matchedmods.extend(matchedbycodingorder)
            unmatchedmods = concatenate_dictlists(unmatchedmods, unmatchedbycodingorder)

        # if any leftovers, align by coding order across contact types
        matchedbycodingorder, unmatchedbycodingorder = self.alignbycodingorder(unmatchedmods)
        matchedmods.extend(matchedbycodingorder)
        # unmatchedmods = concatenate_dictlists(unmatchedmods, unmatchedbycodingorder)

        return matchedmods, unmatchedbycodingorder

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
    # parameters:
    #   - configmodsbysign is a dict of {signnum --> [list of handconfig modules from this signnum that need to be aligned]}
    def alignbyhandshape(self, configmodsbysign):
        if len(configmodsbysign[1]) == 0 or len(configmodsbysign[2]) == 0:
            return [], configmodsbysign, ""
        elif len(configmodsbysign[1]) == len(configmodsbysign[2]) == 1:
            return [(configmodsbysign[1][0], configmodsbysign[2][0])], {1: [], 2: []}, ""

        matchedmods = []
        unmatchedmods = {1: [], 2: []}

        sign1mods = [mod for mod in configmodsbysign[1]]
        sign2mods = [mod for mod in configmodsbysign[2]]

        # first, we try matching by exact name + forearm value

        names = {1: [get_hsname(mod) for mod in sign1mods],
                 2: [get_hsname(mod) for mod in sign2mods]}

        setofnames = set(names[1] + names[2])
        namesbysign = {1: {name: 0 for name in setofnames},
                       2: {name: 0 for name in setofnames}}
        signsbyname = {name: {1: 0, 2: 0} for name in setofnames}
        for snum in snums:
            for configname in names[snum]:
                namesbysign[snum][configname] += 1
                signsbyname[configname][snum] += 1

        # try to match by handshape name (including forearm info)
        for configname in signsbyname.keys():
            modsthisname_matched, modsthisname_unmatched, configmodsbysign, names = self.match_by_handshapename(configname, configmodsbysign, names)  # 2nd arg: signsbyname[configname],
            matchedmods.extend(modsthisname_matched)
            unmatchedmods = concatenate_dictlists(unmatchedmods, modsthisname_unmatched, allowduplicates=False)

        # send any unmatched modules onward to be matched by base/variant/forearm
        sign1mods = [mod for mod in unmatchedmods[1]]
        sign2mods = [mod for mod in unmatchedmods[2]]
        unmatchedmods = {1: [], 2: []}

        if len(sign1mods) > 6 or len(sign2mods) > 6:
            warningstring = alignmentcomplexitywarning
            # use original (greedy/simpler) alignment method
            matched_greedy, unmatched_greedy = self.alignbyhandshape_greedy(sign1mods, sign2mods, "base")
            matchedmods.extend(matched_greedy)
            unmatchedmods = unmatched_greedy
        else:
            warningstring = ""
            # use combinatoric (more complicated but better at finding optimal matchings) alignment method
            matched_combinatoric, unmatched_combinatoric = self.alignbyhandshape_combinatoric(sign1mods, sign2mods)
            matchedmods.extend(matched_combinatoric)
            unmatchedmods = unmatched_combinatoric

        return matchedmods, unmatchedmods, warningstring

    # parameters:
    #   - s1mods is a [list of handconfig modules from sign 1] to align with those from sign 2
    #   - s2mods is a [list of handconfig modules from sign 2] to align with those from sign 1
    #   - elementtoalignby is a string that specifies which level of the handshape to alignby: 'base', 'variant', or 'forearm'
    def alignbyhandshape_greedy(self, s1mods, s2mods, elementtoalignby):
        matchedmods = []
        unmatchedmods = {1: [], 2: []}
        matchedonelements = []

        index1 = 0
        while index1 < len(s1mods):
            mod1 = s1mods[index1]
            mod1hs = PREDEFINED_MAP.get(tuple(HandConfigurationHand(mod1.handconfiguration).get_hand_transcription_list()))
            if mod1hs is not None:
                mod1hsname = mod1hs.name

                index2 = 0
                while index2 < len(s2mods):
                    mod2 = s2mods[index2]
                    mod2hs = PREDEFINED_MAP.get(tuple(HandConfigurationHand(mod2.handconfiguration).get_hand_transcription_list()))
                    if mod2hs is not None:
                        mod2hsname = mod2hs.name

                        mod1bases, mod1variants = parse_predefined_names(mod1hsname, None, mod2hsname, return_path_form=False)
                        mod2bases, mod2variants = parse_predefined_names(mod2hsname, None, mod1hsname, return_path_form=False)

                        mod1bases = set(mod1bases)
                        mod2bases = set(mod2bases)
                        mod1variants = [v for v in mod1variants if v not in mod1bases]
                        mod2variants = [v for v in mod2variants if v not in mod2bases]

                        matchflag = False
                        if (elementtoalignby == 'base' and (mod1bases.issubset(mod2bases) or mod2bases.issubset(mod1bases))):
                            matchflag = True
                            # set is not hashable (needed later for Counter())-- store the intersection as a tuple instead
                            intersect_tuple = tuple(sorted(list(mod1bases.intersection(mod2bases))))
                            matchedonelements.append(intersect_tuple)
                        elif (elementtoalignby == 'variant' and mod1variants == mod2variants):
                            matchflag = True
                            matchedonelements.append(tuple(mod1variants))
                        elif (elementtoalignby == 'forearm' and mod1.overalloptions['forearm'] == mod2.overalloptions['forearm']):
                            matchflag = True
                            matchedonelements.append(mod1.overalloptions['forearm'])

                        if matchflag:
                            matchedmods.append((mod1, mod2))
                            s1mods.pop(index1)
                            s2mods.pop(index2)
                            index1 -= 1
                            index2 = len(s2mods)

                    index2 += 1
            index1 += 1

        # if matching by name/base/variant/forearm and there is > 1 pair in matchedmods with the same matched value,
        #   then feed those pairs through the next level down
        matchedelementcounts = Counter(matchedonelements) if len(matchedonelements) > 1 else []
        for matchedelement in matchedelementcounts:
            numpairs = matchedelementcounts[matchedelement]
            if numpairs > 1:
                # identify which positions in the matchedmods list they occupy
                indicestorematch = [i for i, x in enumerate(matchedonelements) if x == matchedelement]
                # re-match by next element down if possible (otherwise coding order);
                # there should not be any unmatched modules as a result of this process
                if elementtoalignby == 'base':
                    rematchedpairs, notrematched = self.alignbyhandshape_greedy([matchedmods[i][0] for i in indicestorematch],
                                                                [matchedmods[i][1] for i in indicestorematch],
                                                                'variant')
                elif elementtoalignby == 'variant':
                    rematchedpairs, notrematched = self.alignbyhandshape_greedy([matchedmods[i][0] for i in indicestorematch],
                                                                [matchedmods[i][1] for i in indicestorematch],
                                                                'forearm')
                elif elementtoalignby == 'forearm':
                    rematchedpairs, notrematched = self.alignbycodingorder({1: [matchedmods[i][0] for i in indicestorematch],
                                                            2: [matchedmods[i][1] for i in indicestorematch]},
                                                           matchwithnone=True)
                else:
                    rematchedpairs = []
                    notrematched = {1: [matchedmods[i][0] for i in indicestorematch], 2: [matchedmods[i][1] for i in indicestorematch]}
                # remove re-matched pairs from matchedmods
                matchedmods = [pair for idx, pair in enumerate(matchedmods) if idx not in indicestorematch]
                # add the re-matched pairs back to the matchedmods list
                matchedmods.extend(rematchedpairs)
                matchedmods.extend([(notrematched[1][i], notrematched[2][i]) for i in range(len(notrematched[1]))])

        # any unmatched modules should be sent to the next level down
        if s1mods and s2mods:
            if elementtoalignby == 'base':
                # try matching leftovers by variant
                nextlevel_matchedpairs, nextlevel_notmatched = self.alignbyhandshape_greedy(s1mods, s2mods, 'variant')
            elif elementtoalignby == 'variant':
                # try matching leftovers by forearm
                nextlevel_matchedpairs, nextlevel_notmatched = self.alignbyhandshape_greedy(s1mods, s2mods, 'forearm')
            elif elementtoalignby == 'forearm':
                # try matching leftovers by coding order
                nextlevel_matchedpairs, nextlevel_notmatched = self.alignbycodingorder({1: s1mods, 2: s2mods}, matchwithnone=True)
            else:
                # not sure what situation this would be, but just to cover our bases...
                nextlevel_matchedpairs = []
                nextlevel_notmatched = {1: s1mods, 2: s2mods}

            matchedmods.extend(nextlevel_matchedpairs)
            unmatchedmods = concatenate_dictlists(unmatchedmods, nextlevel_notmatched)

        else:
            unmatchedmods = concatenate_dictlists(unmatchedmods, {1: s1mods, 2: s2mods})

        return matchedmods, unmatchedmods

    # parameters:
    #   - s1mods is a [list of handconfig modules from sign 1] to align with those from sign 2
    #   - s2mods is a [list of handconfig modules from sign 2] to align with those from sign 1
    def alignbyhandshape_combinatoric(self, s1mods, s2mods):
        matchedmods = []
        unmatchedmods = {1: [], 2: []}

        lendiff = len(s2mods) - len(s1mods)
        if lendiff >= 0:
            allorderings_s1mods_tooshort = [list(ordering_tuple) for ordering_tuple in itertools.permutations(s1mods)]
            possible_unmatch_locs = get_all_combinations(len(allorderings_s1mods_tooshort)+1, lendiff)
            allorderings_s1mods = []
            for ordering_tooshort in [ordering for ordering in allorderings_s1mods_tooshort]:
                for unmatch_locs_list in possible_unmatch_locs:
                    thisordering_theseunmatches = [mod for mod in ordering_tooshort]
                    for idx, unmatch_loc in enumerate(unmatch_locs_list):
                        thisordering_theseunmatches.insert(unmatch_loc+idx, None)
                    allorderings_s1mods.append(thisordering_theseunmatches)

            # match up allorderings_s1mods vs s2mods in order to calculate the possible alignment scores
            allorderings_s2mods = [s2mods]
            which_has_multiple_orderings = 1

        else:
            lendiff = -lendiff
            allorderings_s2mods_tooshort = [list(ordering_tuple) for ordering_tuple in itertools.permutations(s2mods)]
            possible_unmatch_locs = get_all_combinations(len(allorderings_s2mods_tooshort)+1, lendiff)
            # possible_unmatch_idxs_1 = get_all_combinations(len(sign1mods), lendiff)

            allorderings_s2mods = []
            for ordering_tooshort in [ordering for ordering in allorderings_s2mods_tooshort]:
                for unmatch_locs_list in possible_unmatch_locs:
                    thisordering_theseunmatches = [mod for mod in ordering_tooshort]
                    for idx, unmatch_loc in enumerate(unmatch_locs_list):
                        thisordering_theseunmatches.insert(unmatch_loc+idx, None)
                    allorderings_s2mods.append(thisordering_theseunmatches)

            # match up allorderings_s2mods vs s1mods in order to calculate the possible alignment scores
            allorderings_s1mods = [s1mods]
            which_has_multiple_orderings = 2

        class AlignmentScoring:
            def __init__(self, listofscores):
                self.scores = listofscores
                self.basematches = sum([int(score[0]) for score in listofscores])
                self.variantmatches = sum([int(score[1]) for score in listofscores])
                self.forearmmatches = sum([int(score[2]) for score in listofscores])

        possiblescorings = []
        for s1ordering in allorderings_s1mods:
            for s2ordering in allorderings_s2mods:
                # match up s1ordering with s2ordering, then calculate pair-by-pair scores for this alignment
                #   and add the list of scores to possiblescores

                scores_thisalignment = []
                for idx, s1mod in enumerate(s1ordering):
                    s2mod = s2ordering[idx]

                    if s1mod is None or s2mod is None:
                        scores_thisalignment.append("000")
                    else:
                        s1hsname = get_hsname(s1mod)
                        s2hsname = get_hsname(s2mod)
                        mod1bases, mod1variants = parse_predefined_names(s1hsname, None, s2hsname, return_path_form=False)
                        mod2bases, mod2variants = parse_predefined_names(s2hsname, None, s1hsname, return_path_form=False)

                        mod1bases = set(mod1bases)
                        mod2bases = set(mod2bases)
                        mod1variants = [v for v in mod1variants if v not in mod1bases]
                        mod2variants = [v for v in mod2variants if v not in mod2bases]

                        basematch = int(mod1bases.issubset(mod2bases) or mod2bases.issubset(mod1bases))
                        variantmatch = int(mod1variants == mod2variants)
                        forearmmatch = int(s1mod.overalloptions['forearm'] == s2mod.overalloptions['forearm'])
                        score_thispair = str(basematch) + str(variantmatch) + str(forearmmatch)

                        scores_thisalignment.append(score_thispair)

                possiblescorings.append(AlignmentScoring(scores_thisalignment))

        # now compare alignment scorings and prune lower-scoring alignments
        def comparealignmentscorings_and_prune(elementformatching):
            elementmatches = [(alignscoring.basematches if elementformatching == 'base' else
                               (alignscoring.variantmatches if elementformatching == 'variant' else
                                alignscoring.forearmmatches  # if elementformatching == 'forearm'
                                )) for alignscoring in possiblescorings]
            max_element_matches = max(elementmatches)
            if max_element_matches != min(elementmatches):
                alignment_indices_to_prune = []
                for i, alignscoring in enumerate(possiblescorings):
                    alignscoring_elementmatches = (alignscoring.basematches if elementformatching == 'base' else
                                                   (alignscoring.variantmatches if elementformatching == 'variant' else
                                                    alignscoring.forearmmatches  # if elementformatching == 'forearm'
                                                    ))
                    # these correspond to the items in allorderings_s{1 or 2}mods, whichever is the one with >1 entry
                    if alignscoring_elementmatches < max_element_matches:
                        alignment_indices_to_prune.append(i)
                for idx_to_prune in reversed(alignment_indices_to_prune):
                    possiblescorings.pop(idx_to_prune)
                    if which_has_multiple_orderings == 1:
                        allorderings_s1mods.pop(idx_to_prune)
                    elif which_has_multiple_orderings == 2:
                        allorderings_s2mods.pop(idx_to_prune)

        # ... prioritizing first by base
        comparealignmentscorings_and_prune('base')
        # ... then by variant
        comparealignmentscorings_and_prune('variant')
        # ... then by forearm
        comparealignmentscorings_and_prune('forearm')

        # now all we have left is possible alignments with the maximum possible base, variant, and forearm matches
        #   (prioritized in that order)
        # TODO KV could there be more than one such alignment? I suppose so...
        #  in which case, do we just choose a random one? or is there a way to prioritize coding order here?
        s1mods_alignmentorder = allorderings_s1mods[0]
        s2mods_alignmentorder = allorderings_s2mods[0]
        for idx, s1mod in enumerate(s1mods_alignmentorder):
            s2mod = s2mods_alignmentorder[idx]

            if s1mod is not None and s2mod is not None:
                matchedmods.append((s1mod, s2mod))
            elif s1mod is None:
                unmatchedmods[2].append(s2mod)
            elif s2mod is None:
                unmatchedmods[1].append(s1mod)

        return matchedmods, unmatchedmods

    def match_by_handshapename(self, configname, configmodsbysign, names):  # 2nd arg: modswiththisname_dict,
        modsthisname_matched = []
        modsthisname_unmatched = {1: [], 2: []}

        # collect modules with this name (a) in general, and (b) organized by forearm value
        modsthisname = {1: [], 2: []}
        modsthisname_byforearmvalue = {1: {True: [], False: []},
                                       2: {True: [], False: []}}
        for snum in snums:
            for mod_idx in range(len(configmodsbysign[snum])-1, -1, -1):
                if names[snum][mod_idx] == configname:
                    names[snum].pop(mod_idx)
                    themod = configmodsbysign[snum].pop(mod_idx)
                    modsthisname_byforearmvalue[snum][themod.overalloptions['forearm']].append(themod)
                    modsthisname[snum].append(themod)

        if len(modsthisname[1]) == 0 or len(modsthisname[2]) == 0:
            # no matches possible since one or the other sign has 0 modules with this name
            modsthisname_unmatched = modsthisname
        else:
            # at least one match is possible
            for forearm_value in [True, False]:
                # since names are same and forearm values are the same, these matches will be done by coding order
                matchedpairs_thisforearmvalue, unmatched_thisforearmvalue = \
                    self.alignbycodingorder({1: modsthisname_byforearmvalue[1][forearm_value],
                                        2: modsthisname_byforearmvalue[2][forearm_value]},
                                       matchwithnone=False)
                modsthisname_matched.extend(matchedpairs_thisforearmvalue)
                modsthisname_unmatched = concatenate_dictlists(modsthisname_unmatched, unmatched_thisforearmvalue,
                                                               allowduplicates=False)

            # at this point we have one or more pairs of modules matched by name + forearm, and possibly some that
            #   didn't get matched by forearm... so now we will match the remaining same-name modules
            #   regardless of their forearm value
            matchedpairs_forearmmoot, unmatched_forearmmoot = self.alignbycodingorder(modsthisname_unmatched, matchwithnone=False)
            modsthisname_matched.extend(matchedpairs_forearmmoot)
            modsthisname_unmatched = unmatched_forearmmoot

        return modsthisname_matched, modsthisname_unmatched, configmodsbysign, names

    # parameters:
    #   - modsbysign is a dict of {signnum --> [list of modules of the specified type from this signnum that need to be aligned]}
    #   - modtype is a string specifying the type of module that populates the first argument
    #   - nodename is a string specifying the name of the node from which to start the comparison (TODO is this true??)
    def alignbymovorloc_helper(self, modsbysign, modtype, nodename=""):
        if len(modsbysign[1]) == 0 or len(modsbysign[2]) == 0:
            return [], modsbysign
        elif len(modsbysign[1]) == len(modsbysign[2]) == 1:
            return [(modsbysign[1][0], modsbysign[2][0])], {1: [], 2: []}

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
                    matches, unmatches = self.alignbymovorloc_helper({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, modtype=modtype, nodename=sharedsubnodegroup[0])
                else:
                    matches, unmatches = self.alignbycodingorder({1: modsbysubnodesbysign[1][sharedsubnodegroup], 2: modsbysubnodesbysign[2][sharedsubnodegroup]}, matchwithnone=False)
                matchedmods.extend(matches)
                unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)
            for s1onlysubnodegroup in s1subnodegroups.difference(subnodegroups_inbothsigns):
                unmatched[1].extend(modsbysubnodesbysign[1][s1onlysubnodegroup])
            for s2onlysubnodegroup in s2subnodegroups.difference(subnodegroups_inbothsigns):
                unmatched[2].extend(modsbysubnodesbysign[2][s2onlysubnodegroup])

                # TODO something weird is happening in here such that (eg) when i try to align S1 (one eyebrow ipsi module
                #  & one eyebrow contra module) with S2 (one temple ipsi module)... we somehow get three matches of temple
                #  ipsi with eyebrow contra, and no metnion whatsoever of eyebrow ipsi

            # matches, unmatches = alignbycodingorder(unmatches, matchwithnone=False)
            matches, unmatched = self.alignbycodingorder(unmatched, matchwithnone=False)
            matchedmods.extend(matches)
            # unmatched = concatenate_dictlists(unmatched, unmatches, allowduplicates=False)

            return matchedmods, unmatched

    # ii. After aligning by hand as described above, try to align by movement type (perceptual shape, joint specific, or handshape change)
    #   -- e.g., if sign 1 has both perceptual shape movement and joint-specific movement,
    #   while sign 2 has only joint-specific movement, align the two joint-specific movements,
    #   and then say that sign 1 has an extra perceptual shape movement that doesn’t have a match.
    #   If both signs have two of the same type of movements (e.g. two perceptual shapes), move down to the
    #   top-most characteristic (e.g., what the perceptual shape or the joint-specific movement is, like 'straight' or 'close/open'),
    #   and align ones that match at that level. If things can't be aligned based on any of the above, align by coding order
    #   (e.g. align sign 1’s H1.Mov3 with sign 2’s H1.Mov3, regardless of content).
    # parameters:
    #   - movmodsbysign is a dict of {signnum --> [list of movement modules from this signnum that need to be aligned]}
    def alignbymovement(self, movmodsbysign):
        if len(movmodsbysign[1]) == 0 or len(movmodsbysign[2]) == 0:
            return [], movmodsbysign
        elif len(movmodsbysign[1]) == len(movmodsbysign[2]) == 1:
            return [(movmodsbysign[1][0], movmodsbysign[2][0])], {1: [], 2: []}

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
                matchedpairs, unmatchedmodsbysign = self.alignbymovorloc_helper(movementtypemodsbysign, modtype=ModuleTypes.MOVEMENT, nodename=movementtype)
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
    # parameters:
    #   - locmodsbysign is a dict of {signnum --> [list of location modules from this signnum that need to be aligned]}
    def alignbylocation(self, locmodsbysign):
        if len(locmodsbysign[1]) == 0 or len(locmodsbysign[2]) == 0:
            return [], locmodsbysign
        elif len(locmodsbysign[1]) == len(locmodsbysign[2]) == 1:
            return [(locmodsbysign[1][0], locmodsbysign[2][0])], {1: [], 2: []}

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
                matchedpairs, unmatchedmodsbysign = self.alignbymovorloc_helper(loctypemodsbysign, modtype=ModuleTypes.LOCATION)
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
            matchedpairs, unmatchedmodsbysign = self.alignbymovorloc_helper(rematchbodymods, modtype=ModuleTypes.LOCATION)
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


def whichsignshavemodulesoftype(modulesbysign):
    signswithmodules = []
    for snum in snums:
        if modulesbysign[snum]:
            signswithmodules.append(snum)
    return signswithmodules


# both lists of directions must be in this order: horizontal, vertical, sagittal
def directionsmatch(sign1dirs, sign2dirs, level='specific'):
    if level == 'specific':
        return sign1dirs == sign2dirs
    elif level == 'general':
        for dir1 in sign1dirs:
            if len([dir2 for dir2 in sign2dirs if dir2.sameaxisselection(dir1)]) == 0:
                return False
        return True


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


def get_hsname(handconfigmodule):
    hs = PREDEFINED_MAP.get(tuple(HandConfigurationHand(handconfigmodule.handconfiguration).get_hand_transcription_list()))
    if hs is not None:
        return hs.name
    else:
        return "unnamed"


def get_all_combinations(range_stop, size):
    prods_lists = []
    for prod in itertools.product(range(range_stop), repeat=size):
        sorted_list = sorted(list(prod))
        if sorted_list not in prods_lists:
            prods_lists.append(sorted_list)
    return prods_lists


# args: an arbitrary number of dicts, and each key has a list as its value
def concatenate_dictlists(*args, allowduplicates=False):
    newdict = defaultdict(list)
    keys = [item for arg in args for item in arg]
    keys = sorted(list(set(keys)))

    for d in args:
        for k in keys:
            for listitem in d[k]:
                if allowduplicates or listitem not in newdict[k]:
                    newdict[k].append(listitem)
    return newdict
