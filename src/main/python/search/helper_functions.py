import logging, fractions
from search.search_classes import XslotTypes
from lexicon.module_classes import TimingInterval, TimingPoint, ModuleTypes

def articulatordisplaytext(arts, phase):
    todisplay = ""
    k = arts[0] # hand, arm, or leg
    if arts[1][1] and not arts[1][2]:
        todisplay = k + " " + str(1)
    elif arts[1][2] and not arts[1][1]:
        todisplay = k + " " + str(2)
    elif arts[1][1] and arts[1][2]:
        
        todisplay = "Both " + k.lower() + "s"
        if phase == 1:
            todisplay += " in phase"
        elif phase == 2:
            todisplay += " out of phase"
        elif phase == 3:
            todisplay += " connected"
        elif phase == 4:
            todisplay += " connected, in phase"
    return todisplay

def relationdisplaytext(relmod):
    todisplay = []
    relX_str = ""
    relY_str = ""
    bodyparts1 = []
    bodyparts2 = []
    contact = ""
    manner = ""
    direction = ""
    distance = ""

    relX_str = relmod.relationx.displaystr()
    relY_str = relmod.relationy.displaystr()


    if relmod.contactrel.contact == False: # if None, then no contact has been specified.
        contact = "no contact"
    elif relmod.contactrel.contact:
        hascontacttype = True
        hascontactmanner = True
        contact = "contact"
        contacttype = relmod.contactrel.contacttype
        if contacttype.light:
            contact += ": light"
        elif contacttype.firm:
            contact += ": firm"
        elif contacttype.other:
            contact += ": other"
            if len(contacttype.othertext) > 0:
                contact += f" ({contacttype.othertext})"
        else:
            hascontacttype = False
        contactmanner = relmod.contactrel.manner
        if contactmanner.holding:
            manner += "holding"
        elif contactmanner.continuous:
            manner += "continuous"
        elif contactmanner.intermittent:
            manner += "intermittent"
        else:
            hascontactmanner = False
        
        if hascontacttype and hascontactmanner:
            contact = contact + ", " + manner
        elif hascontactmanner:
            contact = contact + ": " + manner

    if relmod.xy_linked:
        direction += "x/y linked"
    if relmod.xy_crossed:
        direction += "x/y crossed"
    # TODO hori, vert, sag; distance
                
    

    for s in relX_str, relY_str, contact, direction, distance:
        if len(s) > 0:
            todisplay.append(s)
    return todisplay

# TODO update 
def phonlocsdisplaytext(phonlocs):
    todisplay = []
    if phonlocs.phonologicalloc:
        if phonlocs.majorphonloc:
            todisplay.append("Maj. phonological locn")
        if phonlocs.minorphonloc:
            todisplay.append("Min. phonological locn")
        else:
            todisplay.append("Phonological locn")
    if phonlocs.phoneticloc:
        todisplay.append("Phonetic locn")
    return ", ".join(todisplay)

def loctypedisplaytext(loctype):
    todisplay = ""
    if loctype.body:
       todisplay = "Body"
    elif loctype.signingspace:
        txt = "Signing space"
        if loctype.bodyanchored:
            txt += " (body anchored)"
        elif loctype.purelyspatial:
            txt += " (purely spatial)"
        todisplay = txt
    return todisplay

def signtypedisplaytext(specslist):
    
    specs = [s[0] for s in specslist]
    disp = []
    if 'Unspecified' in specs:
        disp.append('Unspecified')
    if '1h' in specs:
        oneh = ['1h']
        for s in ['1h.moves', '1h.no mvmt']:
            if s in specs:
                oneh.append(s)
        if len(oneh) > 0:
            disp.extend(oneh)
        else:
            disp.append('1h')

    if '2h' in specs:
        twoh = ['2h']
        for s in ['same HCs', 'different HCs', 'maintain contact', 'contact not maintained', 'bilaterally symmetric', 'not bilaterally symmetric', 'neither moves']:
            if ('2h.' + s) in specs:
                twoh.append('2h.' + s)
        if '2h.only 1 moves' in specs:
            only1moves = []
            for s in ['H1 moves', 'H2 moves']:
                if ('2h.only 1 moves.' + s) in specs:
                    only1moves.append('2h.only ' + s)
            if len(only1moves) > 0:
                twoh.extend(only1moves)
            else:
                twoh.append('2h.one hand moves')
        if '2h.both move' in specs:
            bothmove = []
            for s in ['move differently', 'move similarly']:
                if ('2h.both move.' + s) in specs:
                    bothmove.append('2h.hands ' + s)
            if len(bothmove) > 0:
                twoh.extend(bothmove)
            else:
                twoh.append('2h.both move')     
        if (len(twoh) > 0):
            disp.extend(twoh)
        else:
            disp.append('2h')

    return disp

# TODO
def module_matches_xslottype(timingintervals, targetintervals, xslottype, xslotstructure, matchtype):
    # logging.warning(timingintervals)
    if xslottype == XslotTypes.IGNORE:
        return True
    
    if xslottype == XslotTypes.CONCRETE:
        if matchtype == 'exact':
            if timingintervals == targetintervals:
                return True
            # else:
            #     collapsetimingintervals(timingintervals)
            # else:
            #     targets = list(targetintervals)
            #     timings = list(timingintervals)
            #     leftmost = timings[0].startpoint
            #     rightmost = timings[0].endpoint
            #     for timing in timings:
            #         if timing.ispoint():
            #             if timing in targets:
            #                 timings.remove(timing)
            #                 targets.remove(timing)

                        
            #         elif t.startpoint == rightmost:
            #             rightmost = t.endpoint

                    


        elif matchtype == 'minimal':
            return timingintervals == targetintervals


    if xslottype == XslotTypes.ABSTRACT_WHOLE:
        targetint = targetintervals[0] # only one selection is possible: either startpt, endpt, or whole sign.
        if targetint.iswholesign() and timingintervals[0].iswholesign():
            return True
        # match if occurring during start of sign
        elif targetint.ispoint() and targetint.startpoint == TimingPoint(1, 0):
            for t in timingintervals:
                if t.startpoint == TimingPoint(1, 0) or t.startpoint == TimingPoint(0, 0):
                    return True
            return False
        # match if occurring during end of sign
        elif targetint.ispoint() and targetint.startpoint == TimingPoint(1, 1):
            # xslotstructure's additionalfraction is 0 if there are no additionalfractions, but the TimingPoint object will have fraction 1
            frac = 1 if xslotstructure.additionalfraction == 0 else xslotstructure.additionalfraction
            # xslotstructure's number is the number of whole xslots, but the TimingPoint object also couts partial xslots
            num = xslotstructure.number if frac == 1 else xslotstructure.number + 1
            endpoint = TimingPoint(num, frac)
            for t in timingintervals:
                if t.endpoint == endpoint or t.endpoint == TimingPoint(0, 1):
                    return True
            return False
        else:
            return False


    if xslottype == XslotTypes.ABSTRACT_XSLOT:
        for targetint in targetintervals:
            if targetint.ispoint():
                for t in timingintervals:
                    if targetint.startpoint.fractionalpart == t.startpoint.fractionalpart:
                        return True
            else:
                for t in timingintervals:
                    if targetint.startpoint.fractionalpart == t.startpoint.fractionalpart and targetint.endpoint.fractionalpart == t.endpoint.fractionalpart:
                        return True
            
        return False

def collapsetimingintervals(timingintervals):
    timings = list(timingintervals)
    
    collapsed = set()
    while len(timings) > 0:
        leftmost = timings[0].startpoint
        rightmost = timings[0].endpoint
        for timing in timings:
            if timing.ispoint():
                collapsed.add(timing)
                timings.remove(timing)
            else:
                
                if timing.endpoint == leftmost:
                    leftmost = timing.startpoint
                elif timing.startpoint == rightmost:
                    rightmost = timing.endpoint
                timings.remove(timing)
                logging.warning(collapsed)
                    
        collapsed.add((leftmost, rightmost))
        
    
    return collapsed


#  Returns True if modulelist (list of relation modules) contains a module that matches target_module
# If target_is_assoc_reln, then we assume modulelist also contains associated relation modules with anchor modules of the correct type
def reln_module_matches(modulelist, target_module, target_is_assoc_reln=False):

    # All relation_x possibilities are mutually exclusive, so check if target relation_x matches at least one relation_x in the list
    target_relationx = target_module.relationx.displaystr()
    if target_relationx != "":
        modulelist = [m for m in modulelist if target_relationx == m.relationx.displaystr()]
        if not modulelist: return False

    # If target relation_y is "Existing module", this can also match "existing module - locn" or "existing module - mvmt".
    # Otherwise, relation_y possibilities are mutually exclusive.
    # We don't have to check relation_y if target_is_assoc_reln, because in this case we assume modulelist is already filtered.
    if not target_is_assoc_reln and target_module.relationy.displaystr() != "": 
        target_relationy = target_module.relationy.displaystr()
        if target_relationy == "Y: existing module":
            modulelist = [m for m in modulelist if target_relationy in m.relationy.displaystr()]
        else:
            modulelist = [m for m in modulelist if target_relationy == m.relationy.displaystr()]
        if not modulelist: return False
    # If target contact is only "Contact", this needs to match contact type suboptions (light, firm, other)
    # If target contact is "No contact", must match signs where contact is not specified or empty (?)
    # Manner options are mutually exclusive.
    if target_module.contactrel.contact is False: # if False, then "no contact" specified
        modulelist = [m for m in modulelist if m.contactrel.contact == False]
    elif target_module.contactrel.contact is not None:
        if target_module.contactrel.contacttype.any:
            modulelist = [m for m in modulelist if m.contactrel.has_contacttype()]
        elif target_module.contactrel.has_contacttype(): # module must match contacttype exactly
            modulelist = [m for m in modulelist if m.contactrel.contacttype == target_module.contactrel.contacttype]
        if not modulelist: return False 

        if target_module.contactrel.manner.any:
            modulelist = [m for m in modulelist if m.contactrel.has_manner()]
        elif target_module.contactrel.has_manner(): # module must match manner (and have some contact / contacttype)
            modulelist = [m for m in modulelist if m.contactrel.manner == target_module.contactrel.manner]
        else: # only "contact" specified, so module must have some contact / contacttype
            modulelist = [m for m in modulelist if m.contactrel.contact]
    if not modulelist: return False 
    
    # direction:
    if len(target_module.directions) == 1 and target_module.directions[0].any: 
        modulelist = [m for m in modulelist if m.has_any_direction()]
    else:
        if target_module.xy_linked:
            modulelist = [m for m in modulelist if m.xy_linked]
        if target_module.xy_crossed:
            modulelist = [m for m in modulelist if m.xy_crossed]
        for i in range(3):
            if target_module.directions[i].axisselected:
                if target_module.has_direction(i): # match exactly because suboption is selected
                    modulelist = [m for m in modulelist if m.directions[i] == target_module.directions[i]]
                else: # only axis is selected, so match if any suboption is selected
                    modulelist = [m for m in modulelist if m.has_direction(i)]
    if not modulelist:
        return False
    
    # Distance:
    if not target_module.contactrel.contact:
        if len(target_module.contactrel.distances) == 1 and target_module.contactrel.distances[0].any: 
            modulelist = [m for m in modulelist if m.has_any_distance()]
        else:
            for i in range(4):
                dist = target_module.contactrel.distances[i]
                if dist.has_selection():
                    modulelist = [m for m in modulelist if m.contactrel.distances[i].has_selection()]
                        
        if not modulelist:
            return False
    
    # Paths
    target_dict = target_module.get_paths()
    if target_dict:
        flag = False
        for m in modulelist:
            sign_dict = m.get_paths()
            matching_keys = [k for k in sign_dict.keys() if k in target_dict.keys()]
            for k in matching_keys:
                if all(p in sign_dict[k] for p in target_dict[k]):
                    flag = True
                    break
        if not flag:
            return False


    return True    


def mvmt_module_matches(modulelist, target_module):
    
    # Filter for modules that match target articulators
    if target_module.has_articulators():
        target_art = articulatordisplaytext(target_module.articulators, target_module.inphase)
        modulelist = [m for m in modulelist if articulatordisplaytext(m.articulators, m.inphase) == target_art]
        if not modulelist: return False

    # Filter for modules that match target paths
    target_paths = set(target_module.movementtreemodel.get_checked_items())
    if target_paths:
        modulelist = [m for m in modulelist if target_paths.issubset(set(m.movementtreemodel.get_checked_items()))]
        if not modulelist: return False

    # TODO For final check, can break out of loop early if a match is found; don't have to filter the entire list.
    return True
        
def locn_module_matches(modulelist, target_module):
    # Filter for modules that match target articulators
    if target_module.has_articulators():
        target_art = articulatordisplaytext(target_module.articulators, target_module.inphase)
        modulelist = [m for m in modulelist if articulatordisplaytext(m.articulators, m.inphase) == target_art]
        if not modulelist: return False
    
    # Filter for modules that match locationtype
    if not target_module.locationtreemodel.locationtype.allfalse():
        target_loctype = loctypedisplaytext(target_module.locationtreemodel.locationtype)
        modulelist = [m for m in modulelist if loctypedisplaytext(m.locationtreemodel.locationtype) == target_loctype]
        if not modulelist: return False

    # Filter for modules that match phonlocs
    if not target_module.phonlocs.allfalse():
        target_phonlocs = phonlocsdisplaytext(target_module.phonlocs)
        modulelist = [m for m in modulelist if phonlocsdisplaytext(m.locationtreemodel.locationtype) == target_phonlocs]
        if not modulelist: return False

    # Filter for modules that match target paths
    # TODO deal with subareas and surfaces
    fully_checked = target_module.locationtreemodel.nodes_are_terminal
    target_paths = set(target_module.locationtreemodel.get_checked_items(only_fully_checked=fully_checked))
    if target_paths:
        modulelist = [m for m in modulelist if target_paths.issubset(set(m.locationtreemodel.get_checked_items(only_fully_checked=fully_checked)))]
        if not modulelist: return False
                

    # TODO For final check, can break out of loop early if a match is found; don't have to filter the entire list.
    return True