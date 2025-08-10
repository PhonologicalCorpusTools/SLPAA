import logging, fractions
from collections import defaultdict
from search.search_classes import XslotTypes
from lexicon.module_classes import ParameterModule, MovementModule, LocationModule, RelationModule, TimingInterval, TimingPoint, ModuleTypes, HandConfigurationHand, PREDEFINED_MAP
from lexicon.predefined_handshape import HandshapeEmpty
from constant import Precomputed

def filter_modules_by_articulators(modulelist, target_module: ParameterModule, matchtype='minimal'):
    """ Filter a list of parameter modules, returning a subset whose articulator / inphase specifications match that of a target module.
        
        If matchtype is 'minimal':
            A target with no articulators specified returns the full modulelist. 
            A target with articulators specified returns modules where articulators match exactly.
            A target with articulators specified and no inphase specified returns modules where articulators match exactly.
            A target with inphase specifications returns modules where the target inphase specs are a subset of the module inphase specs. (e.g. if target is 'connected', modules that are both 'connected' and 'in phase' will also be matched).
    """

    if not target_module.has_articulators() and matchtype == 'minimal':
        return modulelist

    # module.articulators is (Articulator: str, {1: bool, 2: bool})
    # module.inphase:
    # 0: not specifiable; 1: in phase; 2: out of phase; 3: connected; 4: connected & in phase; 5: connected & out of phase (impossible)
    # (see getphase() in modulespecification_dialog)
    target_art = target_module.articulators
    target_inphase = target_module.inphase if hasattr(target_module, "inphase") else 0
    matching_modules = []
    for m in modulelist:
        m_art = m.articulators
        m_inphase = m.inphase if hasattr(m, "inphase") else 0
        if matchtype == 'exact' and m_art == target_art and m_inphase == target_inphase:
            matching_modules.append(m)
        elif matchtype == 'minimal' and m_art == target_art:
            if target_inphase == m_inphase:
                matching_modules.append(m)
            elif (matchtype == 'minimal' 
                and (target_inphase == m_inphase 
                        or target_inphase == 1 and m_inphase == 4
                        or target_inphase == 2 and m_inphase == 5
                        or target_inphase == 3 and m_inphase in [4, 5])):
                matching_modules.append(m)
    return matching_modules


def filter_modules_by_phonlocs(modulelist, target_module, matchtype='minimal'):
    """ Filter a list of parameter modules, returning a subset whose phonlocs specifications match that of a target module.
        
        If matchtype is 'minimal':
            A target with no phonlocs specified will return the full modulelist. 
            A target with phonlocs specifications returns modules where the target specs are a subset of the module specs.
    """
    if target_module.phonlocs.allfalse() and matchtype == 'minimal':
        return modulelist
    if matchtype == 'exact':
        matching_modules = [m for m in modulelist if m.phonlocs == target_module.phonlocs]
        return matching_modules
    else:
        # just get the attribute names that are true in the target. For minimal matching, we don't care about unchecked attributes.
        target_attrs = [attr for attr, val in vars(target_module.phonlocs).items() if val] 
        matching_modules = [m for m in modulelist if all([m.phonlocs[attr] for attr in target_attrs])]
        return matching_modules

def filter_modules_by_loctype(modulelist, target_module, matchtype='minimal'):
    """ Filter a list of parameter modules, returning a subset whose loctype specifications match that of a target module.
        
        If matchtype is 'minimal':
            A target with no loctype specified will return the full modulelist. 
            A target with only 'signing space' specified will also return modules with 'body-anchored' or 'purely spatial'. 
    """
    if target_module.locationtreemodel.locationtype.allfalse() and matchtype == 'minimal':
        return modulelist
    if matchtype == 'exact':
        matching_modules = [m for m in modulelist if m.locationtreemodel.locationtype == target_module.locationtreemodel.locationtype]
        return matching_modules
    else:
        # just get the attribute names that are true in the target. For minimal matching, we don't care about unchecked attributes.
        target_attrs = [attr for attr, val in vars(target_module.locationtreemodel.locationtype).items() if val] 
        matching_modules = [m for m in modulelist if all([getattr(m.locationtreemodel.locationtype, attr) for attr in target_attrs])]
        return matching_modules

def signtype_matches_target(specs_dict, target, matchtype='minimal'):
    """Used in search function to check if this signtype's specslist matches (i.e. is equal to or more restrictive than) target.
    Doesn't check Notes.

    Args:
        specs_dict (dict): Output of SignType.convertspecstodict(). For example, {'2h': {'different HCs': {}}, '1a': {}, 'Unspecified_legs': {}}
        target (dict): Target to match. Output of SignType.convertspecstodict().

    Returns:
        bool.
    """
    if matchtype != 'minimal': # exact match
        return specs_dict == target
    # otherwise, match minimally:
    for attr in target: # e.g. 'Unspecified_legs', '2h', '1a'
        if 'Unspecified' in attr:
            # For example, if target has "Unspecified_hands", then return false if specs_dict has 1h or 2h as keys
            art = attr[attr.index('_') + 1] # grabs 'h', 'a', or 'l'
            if f"1{art}" in specs_dict or f"2{art}" in specs_dict:
                return False
        elif not attr in specs_dict: # first-level specification doesn't match
            return False 
        else: # first-level specification matches. When matching minimally, if target[attr] == {}, then this is sufficient for a match.
            if bool(target[attr]): # there's a nested selection, eg {"2h" : {"both move" : {"move differently"}}}
                for _ in target[attr]:
                    if not signtype_matches_target(specs_dict[attr], target[attr],  matchtype=matchtype):
                        return False
    return True

def signlevelinfo_matches_target(sli, target_sli, matchtype='minimal'):
    '''
    Used in search function to check if this signtype's signlevelinfo matches (i.e. is equal to or more restrictive than) target.
    TODO: allow fuzzy matching for text (regex?) and date ranges

    For now searches are always minimal.
        If an attribute is empty, don't check that attribute.
        Eventually maybe this target will always match exactly, and specific attributes will allow greater precision
        e.g. by default a text attribute will have * specified

    '''
    if matchtype == 'exact':
        return sli == target_sli
    # Check gloss
    # TODO: eventually we will need to allow multiple target glosses
    target_gloss = getattr(target_sli, "gloss") 
    if target_gloss and not target_gloss in getattr(sli, "gloss"):
        return False
    target_entryid = getattr(target_sli, "entryid").display_string()
    if target_entryid and not getattr(sli, val).display_string() == target_entryid:
        return False

    # Text properties: for now, match exactly. TODO: allow regex or other matching methods?
    for val in ["idgloss", "lemma", "source", "signer", "frequency", "coder", "note"]:
        target_attr = getattr(target_sli, val)
        if target_attr and not getattr(sli, val) == target_attr:
            return False
    # Binary properties. 
    for val in ["fingerspelled", "compoundsign", "handdominance"]:
        target_attr = getattr(target_sli, val)
        # fingerspelled and compoundsign can be T/F/None; handdominance can be L/R/None
        if target_attr not in [None, ''] and not getattr(sli, val) == target_attr:
            return False
    # Dates. TODO: allow date ranges?
    for val in ["datecreated", "datelastmodified"]:
        target_attr = getattr(target_sli, val)
        if target_attr and not getattr(sli, val) == target_attr:
            return False
    return True

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
        modulelist: list of relation modules (list is not modified). If `target_is_assoc_reln`, then we assume modulelist also contains associated relation modules with anchor modules of the correct type
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

def filter_modules_by_target_mvmt(modulelist, target_module:MovementModule, matchtype='minimal', terminate_early=False):
    """
    Filter a list of movement modules, returning a subset that matches a target movement module.
    Args:
        modulelist: list of movement modules (list is not modified)
        target_module: movement module built in the Search window
        matchtype: 'minimal' or 'exact'. If minimal, matching modules can contain paths not specified in target_module's paths.
        terminate_early: bool. True if we only need to know whether `modulelist` has at least one matching module. 
    Returns:
        list. Returns the subset of `modules` that match `target_module`. 
        If `terminate_early` is True and target paths are specified, the list contains only the first module in `modulelist` that matches `target_module`. 
        If matchtype is `exact`, matching modules cannot contain any details or selections not specified in `target_module`.
    """ 
    if not modulelist:
        return []
    for filter in [filter_modules_by_articulators, filter_modules_by_phonlocs]:
        modulelist = filter(modulelist, target_module, matchtype)
        if not modulelist:
            return []

    # TODO filter by xslot types! 

    # Filter for modules that match target paths
    if target_module.selections is None:
        target_module.compute_selections()
    target_paths = target_module.selections[Precomputed.MOV_PATHS]
    matching_modules = []
    for m in modulelist:
        if m.selections is None:
                m.compute_selections()
        module_paths = m.selections[Precomputed.MOV_PATHS]
        if ((matchtype == "exact" and module_paths == target_paths) 
            or (matchtype == "minimal" and target_paths.issubset(module_paths))):
            matching_modules.append(m)
        if matching_modules and terminate_early:
            return matching_modules
    return matching_modules

                
def filter_modules_by_target_locn(modulelist, target_module:LocationModule, matchtype='minimal', terminate_early=False): 
    """
    Filter a list of location modules, returning a subset that matches a target location module.
    Args:
        modulelist: list of location modules (list is not modified)
        target_module: location module built in the Search window
        matchtype: 'minimal' or 'exact'. If minimal, matching modules can contain paths/details not specified in target_module's paths/details.
        terminate_early: bool. True if we only need to know whether `modulelist` has at least one matching module. 
    Returns:
        list. Returns the subset of `modules` that match `target_module`. 
        If `terminate_early` and target paths are specified, the list contains only the first module in `modulelist` that matches `target_module`. 
        If matchtype is `exact`, matching modules cannot contain any details or selections not specified in `target_module`.
    """
    for filter in [filter_modules_by_articulators, filter_modules_by_phonlocs, filter_modules_by_loctype]:
        modulelist = filter(modulelist, target_module, matchtype)
        if not modulelist:
            return []
    fully_checked = target_module.locationtreemodel.nodes_are_terminal
    if target_module.selections is None:
        target_module.compute_selections()
    target_path_tuples = target_module.selections[Precomputed.LOC_PATHS]
    modulelist = filter_modules_by_locn_paths(modules=modulelist, 
                                                    target_paths=target_path_tuples, 
                                                    nodes_are_terminal=fully_checked, 
                                                    matchtype=matchtype, 
                                                    terminate_early=terminate_early)

    return modulelist
    
def filter_modules_by_locn_paths(modules: list[LocationModule] | list[RelationModule], target_paths, nodes_are_terminal, matchtype='minimal', terminate_early=False, is_relation=False, articulator=None):
    """
    Filter a list of location or relation modules by selected paths. This doesn't check for matching loctypes (e.g. body vs body-anchored), phonlocs, articulators, xslottypes, etc.
    Args:
        modules: list of location or relation modules
        target_paths: target paths to match. This is a list of tuples where each tuple contains:
            target_path[0]: str. The full path.
            target_path[1]: tuple(tuple(), tuple()). The selected details (e.g. surfaces and subareas)
        nodes_are_terminal: bool. True if a path should only be matched if fully checked.
        matchtype: 'minimal' or 'exact'
        terminate_early: bool. True if we only need to know whether `modules` has at least one matching module. 
        is_relation: bool. True if we're filtering for location paths belonging to relation modules. In this case `articulator` must be specified.
        articulator: string. A label such as "hand1" or "arm2"

    Returns:
        list. Contains the subset of `modules` with modules that contain all the paths and details tables in `paths`. If `terminate_early` is True, the list contains only the first module in `modules` that matches `target_paths`. If matchtype is `exact`, matching modules cannot contain any other paths or details tables.
    """
    matching_modules = []
    for module in modules:
        if is_relation:
            treemodel = module.get_treemodel_from_articulator_label(articulator)
            module_paths_to_check = treemodel.get_checked_items(only_fully_checked=nodes_are_terminal, include_details=True)
            module_paths = set()
            for mp in module_paths_to_check:
                # module_paths is a list of dicts {'path', 'abbrev', 'details'}. 
                # Convert the details to tuples to match the target_path format, and so that we can store them in a set later.
                # details_tuple is tuple(tuple(), tuple())
                details_tuple = tuple(tuple(selecteddetails) for selecteddetails in mp['details'].get_checked_values().values())
                module_paths.add((mp['path'], details_tuple))

        else:
            if module.selections is None:
                module.compute_selections(nodes_are_terminal)
            module_paths = module.selections[Precomputed.LOC_PATHS]
        
        # to match exactly, a module must contain _only_ the target paths and no other paths
        if matchtype == 'exact' and module_paths == target_paths: 
            matching_modules.append(module)
            
        elif matchtype == 'minimal':
            # create module_details as dict so we can sort by path for faster lookup.
            # This is ok because we don't expect any repeated paths in module_paths, so keys are unique.
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

def filter_modules_by_target_orientation(modulelist, target_module, matchtype='minimal'):
    """
    Filter a list of orientation modules, returning a subset that matches a target orientation module.
    Args:
        modulelist: list of orientation modules (list is not modified)
        target_module: orientation module built in the Search window
        matchtype: 'minimal' or 'exact'.
    Returns:
        list. Returns the subset of `modulelist` that match `target_module`.
    """ 
    NUM_DIRECTIONS = 3
    for filter in [filter_modules_by_articulators, filter_modules_by_phonlocs]:
        modulelist = filter(modulelist, target_module, matchtype)
        if not modulelist:
            return []
    if matchtype != 'minimal': # exact matchtype
        for i in range(NUM_DIRECTIONS):
            matching_modules = [m for m in matching_modules if m.palm[i] == target_module.palm[i] and m.root[i] == target_module.root[i]]
            if not matching_modules:
                return []
    else: # minimal matchtype
        attr_names = ['root', 'palm']
        for attr_name in attr_names:
            target_dir = getattr(target_module, attr_name) # module.root or module.pam
            for i in range(NUM_DIRECTIONS):
                if target_dir[i].has_subselection(): 
                    # target includes an axis and a subselection, which need to be matched exactly (even with minimal matchtype)
                    matching_modules = [m for m in matching_modules if getattr(m, attr_name)[i] == target_dir[i]]
                elif target_dir[i].axisselected: 
                    # target has axis but no subselection. When matching minimally, signs can match with or without subselections.
                    matching_modules = [m for m in matching_modules if getattr(m, attr_name)[i].axisselected]
                else: 
                    # target axis not selected. when matching minimally, this direction can have any selection.
                    pass
                if not matching_modules:
                        return []
    return matching_modules

    
def filter_modules_by_target_handconfig(modulelist, target_module, matchtype='minimal'):
    """ Filter a list of hand config modules, returning a subset whose specifications match that of a target hand config module.
        
        If matchtype is 'minimal':
            A target with 'forearm' unchecked matches modules with any value of 'forearm'.
            A target with an empty handshape matches all hand configs.
            A target with a custom hand config tuple specified matches modules where the target specs are a subset of the module specs.
            Otherwise, match exactly.
    """
    for filter in [filter_modules_by_articulators, filter_modules_by_phonlocs]:
        modulelist = filter(modulelist, target_module, matchtype)
        if not modulelist:
            return []
    # filter by forearm
    target_forearm = target_module.overalloptions['forearm']
    modulelist = [
        m for m in modulelist
        if (
            m.overalloptions['forearm'] == target_forearm
            or (matchtype == 'minimal' and not target_forearm)
        )
    ]
    if not modulelist: return []
    # filter by hand config
    target_tuple = target_module.config_tuple()
    if matchtype == 'minimal' and target_tuple == HandshapeEmpty.canonical:
        return modulelist
    matching_modules = []
    
    for m in modulelist:
        if HandConfigurationHand(m.handconfiguration) == HandConfigurationHand(target_module.handconfiguration):
            matching_modules.append(m)
        elif matchtype == 'minimal':
            sign_tuple = m.config_tuple()
            # Searching for a custom tuple (not a predefined shape)
            # items in certain positions are hardcoded for all tuples.
            positions_to_check = [i for i in range(33) if i not in [6,7,14,19,24,29] and target_tuple[i] != ""]
            # logging.warning(positions_to_check)
            if all([target_tuple[i] == sign_tuple[i] for i in positions_to_check]):
                matching_modules.append(m)

    return matching_modules

        
def filter_modules_by_target_extendedfingers(modulelist, target_module, matchtype='exact'):
    """ This filter is always exact. """
    for filter in [filter_modules_by_articulators, filter_modules_by_phonlocs]:
        modulelist = filter(modulelist, target_module, matchtype)
        if not modulelist:
            return []
    extended_symbols = ['H', 'E', 'e', 'i'] if target_module.i_extended else ['H', 'E', 'e']
    # get lists of target extended vs nonextended fingers, where thumb=0, index=1, etc
    target_extended_fingers, target_nonextended_fingers = [], [] 
    for index, (finger, value) in enumerate(target_module.finger_selections.items()):
        if value == "Extended":
            target_extended_fingers.append(index)
        elif value == "Not extended":
            target_nonextended_fingers.append(index)
    # logging.warning(f"extended: {target_extended_fingers}. not: {target_nonextended_fingers}")
    # get a list of "Number of extended fingers" that were selected
    target_extended_numbers = [num for num, is_selected in target_module.num_extended_selections.items() if is_selected]
    # logging.warning(f"nums: {target_extended_numbers}")
    matching_modules = []
    for m in modulelist:
        sign_tuple = tuple(HandConfigurationHand(m.handconfiguration).get_hand_transcription_list())
        sign_ext_fingers = [finger for finger in range(5) if m.finger_is_extended(sign_tuple, extended_symbols, finger)]
        # logging.warning(f"target ext: {target_extended_fingers}. target not ext: {target_nonextended_fingers}. sign ext: {sign_ext_fingers}")

        if ((len(sign_ext_fingers) in target_extended_numbers or target_extended_numbers == [])  # TODO
            and all(finger in sign_ext_fingers for finger in target_extended_fingers)
            and all(finger not in sign_ext_fingers for finger in target_nonextended_fingers)):
            matching_modules.append(m)
            # logging.warning("this module matches.")
    
    return matching_modules