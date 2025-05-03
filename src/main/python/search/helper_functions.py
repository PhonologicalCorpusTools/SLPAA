import logging, fractions
from collections import defaultdict
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


def filter_modules_by_target_reln(modulelist, target_module, target_is_assoc_reln=False, matchtype='minimal', terminate_early=False): 
    """
    Filter a list of relation modules, returning a subset that matches a target relation module.
    Args:
        modulelist: list of relation modules. If `target_is_assoc_reln`, then we assume modulelist also contains associated relation modules with anchor modules of the correct type
        target_module: relation module built in the Search window
        target_is_assoc_reln: target is a relation module that was built as part of a mov+rel or loc+rel target. 
        matchtype: 'minimal' or 'exact'. TODO: exactly what does minimal / exact mean?
        terminate_early: bool. True if we only need to know whether `modulelist` has at least one matching module. 
    Returns:
        list. Returns the subset of `modules` that match `target_module`. If `terminate_early` is True and target paths are specified, the list contains only the first module in `modulelist` that matches `target_module`. If matchtype is `exact`, matching modules cannot contain any details or selections not specified in `target_module`.
    """ 
    
    # All relation_x possibilities are mutually exclusive, so check if target relation_x matches at least one relation_x in the list
    target_relationx = target_module.relationx.displaystr()
    if target_relationx != "":
        modulelist = [m for m in modulelist if target_relationx == m.relationx.displaystr()]
        if not modulelist: return []

    # If target relation_y is "Existing module", this can also match "existing module - locn" or "existing module - mvmt".
    # Otherwise, relation_y possibilities are mutually exclusive.
    # We don't have to check relation_y if target_is_assoc_reln, because in this case we assume modulelist is already filtered.
    if not target_is_assoc_reln and target_module.relationy.displaystr() != "": 
        target_relationy = target_module.relationy.displaystr()
        if target_relationy == "Y: existing module":
            modulelist = [m for m in modulelist if target_relationy in m.relationy.displaystr()]
        else:
            modulelist = [m for m in modulelist if target_relationy == m.relationy.displaystr()]
        if not modulelist: return []
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
        if not modulelist: return [] 

        if target_module.contactrel.manner.any:
            modulelist = [m for m in modulelist if m.contactrel.has_manner()]
        elif target_module.contactrel.has_manner(): # module must match manner (and have some contact / contacttype)
            modulelist = [m for m in modulelist if m.contactrel.manner == target_module.contactrel.manner]
        else: # only "contact" specified, so module must have some contact / contacttype
            modulelist = [m for m in modulelist if m.contactrel.contact]
    if not modulelist: return [] 
    
    # direction:
    if len(target_module.directions) == 1 and target_module.directions[0].any: 
        modulelist = [m for m in modulelist if m.has_any_direction()]
    else:
        if target_module.xy_linked:
            modulelist = [m for m in modulelist if m.xy_linked]
        if target_module.xy_crossed:
            modulelist = [m for m in modulelist if m.xy_crossed]
        for i in range(len(target_module.directions)):
            if target_module.directions[i].axisselected:
                if target_module.has_direction(i): # match exactly because suboption is selected
                    modulelist = [m for m in modulelist if m.directions[i] == target_module.directions[i]]
                else: # only axis is selected, so match if any suboption is selected
                    modulelist = [m for m in modulelist if m.has_direction(i)]
    if not modulelist:
        return []
    
    # Distance:
    if not target_module.contactrel.contact:
        if len(target_module.contactrel.distances) == 1 and target_module.contactrel.distances[0].any: 
            modulelist = [m for m in modulelist if m.has_any_distance()]
        else:
            for dist in target_module.contactrel.distances:
                if dist.has_selection():
                    modulelist = [m for m in modulelist if m.contactrel.distances[i].has_selection()]
                        
        if not modulelist:
            return []
    
    # Paths
    # fully_checked = target_module.locationtreemodel.nodes_are_terminal 
    # target_dict: 
    # Keys (str): Articulators ('H1', 'H2', 'Arm1', 'Arm2', 'Leg1', 'Leg2').
    # Values: list of dicts output from treemodel.get_checked_items(). Relevant keys are 'path', 'details'
    target_dict = target_module.get_paths()
    for m in modulelist:
        # module_dict = m.get_paths(nodes_are_terminal=False)]
        module_articulators = m.get_articulators_in_use(as_string=True)
        for articulator, target_paths in target_dict.items():
            if articulator in module_articulators:
                # convert to a list of tuples, since that's what we'll try to match when searching
                target_path_tuples = []
                for p in target_paths:
                    # details_tuple is tuple([], [])
                    details_tuple = tuple(tuple(selecteddetails) for selecteddetails in p['details'].get_checked_values().values())
                    target_path_tuples.append((p['path'], details_tuple))

                modulelist = filter_modules_by_locn_paths(modules=modulelist,
                                                          target_paths=target_path_tuples,
                                                          nodes_are_terminal=False,
                                                          is_relation=True,
                                                          articulator=articulator,
                                                          matchtype=matchtype)
                if not modulelist: return []     

    return modulelist          

def filter_modules_by_target_mvmt(modulelist, target_module, matchtype='minimal', terminate_early=False):
    """
    Filter a list of movement modules, returning a subset that matches a target movement module.
    Args:
        modulelist: list of movement modules
        target_module: movement module built in the Search window
        matchtype: 'minimal' or 'exact'. TODO: exactly what does minimal / exact mean?
        terminate_early: bool. True if we only need to know whether `modulelist` has at least one matching module. 
    Returns:
        list. Returns the subset of `modules` that match `target_module`. If `terminate_early` is True and target paths are specified, the list contains only the first module in `modulelist` that matches `target_module`. If matchtype is `exact`, matching modules cannot contain any details or selections not specified in `target_module`.
    """ 
    matching_modules = modulelist
    if target_module.has_articulators():
        target_art = articulatordisplaytext(target_module.articulators, target_module.inphase)
        matching_modules = [m for m in matching_modules if articulatordisplaytext(m.articulators, m.inphase) == target_art]
        if not matching_modules: return []

    if not target_module.phonlocs.allfalse():
        target_phonlocs = phonlocsdisplaytext(target_module.phonlocs)
        matching_modules = [m for m in matching_modules if phonlocsdisplaytext(m.locationtreemodel.locationtype) == target_phonlocs]
        if not matching_modules: return []

    # Filter for modules that match target paths
    target_paths = set(target_module.movementtreemodel.get_checked_items())
    if target_paths:
        # TODO matching_modules = m for m in ... if module_matches_xslottype(module.timingintervals, target_module.timingintervals, xslottype, sign.xslotstructure, self.matchtype):
        # TODO minimal vs exact, and terminate_early
        matching_modules = [m for m in matching_modules if target_paths.issubset(set(m.movementtreemodel.get_checked_items()))]
        
        if not matching_modules: return []
                
    return matching_modules

def filter_modules_by_target_locn(modulelist, target_module, matchtype='minimal', terminate_early=False): 
    """
    Filter a list of location modules, returning a subset that matches a target location module.
    Args:
        modulelist: list of location modules
        target_module: location module built in the Search window
        matchtype: 'minimal' or 'exact'. TODO: exactly what does minimal / exact mean?
        terminate_early: bool. True if we only need to know whether `modulelist` has at least one matching module. 
    Returns:
        list. Returns the subset of `modules` that match `target_module`. If `terminate_early` is True and target paths are specified, the list contains only the first module in `modulelist` that matches `target_module`. If matchtype is `exact`, matching modules cannot contain any details or selections not specified in `target_module`.
    """
    matching_modules = modulelist
    if target_module.has_articulators():
        target_art = articulatordisplaytext(target_module.articulators, target_module.inphase)
        matching_modules = [m for m in matching_modules if articulatordisplaytext(m.articulators, m.inphase) == target_art]
        if not matching_modules: return []

    if not target_module.locationtreemodel.locationtype.allfalse():
        target_loctype = loctypedisplaytext(target_module.locationtreemodel.locationtype)
        matching_modules = [m for m in matching_modules if loctypedisplaytext(m.locationtreemodel.locationtype) == target_loctype]
        if not matching_modules: return []

    if not target_module.phonlocs.allfalse():
        target_phonlocs = phonlocsdisplaytext(target_module.phonlocs)
        matching_modules = [m for m in matching_modules if phonlocsdisplaytext(m.locationtreemodel.locationtype) == target_phonlocs]
        if not matching_modules: return []
    
    fully_checked = target_module.locationtreemodel.nodes_are_terminal
    target_paths = target_module.locationtreemodel.get_checked_items(only_fully_checked=True, include_details=True)
    if target_paths:
        # convert to a list of tuples, since that's what we'll try to match when searching
        target_path_tuples = []
        for p in target_paths:
            # details_tuple is tuple([], [])
            details_tuple = tuple(tuple(selecteddetails) for selecteddetails in p['details'].get_checked_values().values())
            target_path_tuples.append((p['path'], details_tuple))

        matching_modules = filter_modules_by_locn_paths(modules=matching_modules, 
                                                        target_paths=target_path_tuples, 
                                                        nodes_are_terminal=fully_checked, 
                                                        matchtype=matchtype, 
                                                        terminate_early=terminate_early)
        if not matching_modules: return []     

    return matching_modules
    
def filter_modules_by_locn_paths(modules, target_paths, nodes_are_terminal, matchtype='minimal', terminate_early=False, is_relation=False, articulator=None):
    """
    Filter a list of location modules by selected paths. This doesn't check for matching loctypes (e.g. body vs body-anchored), phonlocs, articulators, xslottypes, etc.
    Args:
        modules: list of location modules
        target_paths: target paths to match. This is a list of tuples where each tuple contains:
            target_path[0]: str. The full path.
            target_path[1]: tuple(tuple(), tuple()). The selected details (e.g. surfaces and subareas)
        nodes_are_terminal: bool. True if a path should only be matched if fully checked.
        matchtype: 'minimal' or 'exact'
        terminate_early: bool. True if we only need to know whether `modules` has at least one matching module. 
        is_relation: bool. True if we're filtering for location paths belonging to relation modules. In this case `articulator` must be specified.
        articulator: string. A label such as "hand1" or "arm2"

    Returns:
        list. Returns the subset of `modules` with modules that contain all the paths and details tables in `paths`. If `terminate_early` is True, the list contains only the first module in `modules` that matches `target_paths`. If matchtype is `exact`, matching modules cannot contain any other paths or details tables.
    """
    matching_modules = []
    for module in modules:
        if is_relation:
            treemodel = module.get_treemodel_from_articulator_label(articulator)
            module_paths_to_check = treemodel.get_checked_items(only_fully_checked=nodes_are_terminal, include_details=True)
        else:
            module_paths_to_check = module.locationtreemodel.get_checked_items(only_fully_checked=nodes_are_terminal, include_details=True)
        if len(module_paths_to_check) < len(target_paths): # all paths specified in the target need to be present in the module for it to match, regardless of matchtype
            continue
        module_paths = set()
        for mp in module_paths_to_check:
            # module_paths is a list of dicts {'path', 'abbrev', 'details'}. 
            # Convert the details to tuples to match the target_path format, and so that we can store them in a set later.
            # details_tuple is tuple(tuple(), tuple())
            details_tuple = tuple(tuple(selecteddetails) for selecteddetails in mp['details'].get_checked_values().values())
            module_paths.add((mp['path'], details_tuple))

        # to match exactly, a module must contain _only_ the target paths and no other paths
        if matchtype == 'exact' and module_paths == target_paths: 
            matching_modules.append(module)
            
        elif matchtype == 'minimal':
            # create module_details as dict so we can sort by path for faster lookup.
            # This is ok because we don't expect any repeated paths in module_paths, so keys are unique.
            # This is NOT the case for target_paths 
            # (we might have e.g. two instances of the same target path, but with different details)
            module_details = {}
            for p in module_paths:
                module_details[p[0]] = p[1]
            module_minimally_matches = True
            for target_path in target_paths: 
                # target_path is a tuple (path_name, ((surfaces),(subareas)))
                # module_details is a dict: {path_name_1: ((surfaces), (subareas)), path_name_2: ((blah), (blah))}
                target_path_name = target_path[0]
                if target_path_name not in module_details:
                    module_minimally_matches = False
                    break # break out of this loop, as all target_paths need to match.
                else:
                    if target_path[1] != module_details[target_path_name]: # check for at least a minimal match
                        target_details = [set(td) for td in target_path[1]] # eg [set(surface1, surface2), set(bonejoint1)]
                        if not all(target_details[i] <= set(module_details[target_path_name][i]) for i in range(len(target_details))):
                            module_minimally_matches = False
                            break
            if module_minimally_matches:
                matching_modules.append(module)
            if terminate_early and matching_modules:
                return matching_modules
    return matching_modules

