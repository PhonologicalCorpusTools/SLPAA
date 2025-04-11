import io, os


import copy 
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel, 
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QDialog
)
from collections import defaultdict
from PyQt5.QtWidgets import QStyledItemDelegate, QMessageBox

from PyQt5.QtCore import QModelIndex, Qt
from gui.panel import SignLevelMenuPanel
from lexicon.module_classes import (AddedInfo, TimingInterval, TimingPoint, ParameterModule, 
                                    ModuleTypes, BodypartInfo, MovementModule, LocationModule, RelationModule,
                                    HandConfigurationHand, PREDEFINED_MAP)
from constant import TargetTypes, HAND, ARM, LEG, HandConfigSlots
import logging

from models.movement_models import MovementTreeModel
from models.location_models import LocationTreeModel, BodypartTreeModel
from serialization_classes import LocationModuleSerializable, MovementModuleSerializable, RelationModuleSerializable
from search.helper_functions import (relationdisplaytext, articulatordisplaytext, phonlocsdisplaytext, loctypedisplaytext, 
                                     signtypedisplaytext, module_matches_xslottype, reln_module_matches, locn_module_matches, mvmt_module_matches,
                                     filter_modules_by_locn_paths)
from search.search_classes import SearchTargetItem




class TargetHeaders:
    NAME = 0
    TYPE = 1
    VALUE = 2
    INCLUDE = 3
    NEGATIVE = 4
    XSLOTS = 5
    MODULE = 6
    MODULE_ID = 7
    ASSOCRELNMODULE = 8
    ASSOCRELNMODULE_ID = 9
    




class SearchModel(QStandardItemModel):
    def __init__(self, sign=None, serializedsearchmodel=None,**kwargs):
        super().__init__(**kwargs)
        self.name = None
        self.path = None
        self._matchtype = None # exact / minimal
        self._matchdegree = None # any / all
        self._searchtype = None # new / add

        self.sign = sign

        self.headers = ["Name", "Type", "Value", "Include?", "Negative?",  "X-slots"]
        self.setHorizontalHeaderLabels(self.headers)
        self.serializedsearchmodel = None
        if serializedsearchmodel is not None:
            self.serializedsearchmodel = serializedsearchmodel.serializedmodel
            self.setvaluesfromserializedmodel()
    


    def setvaluesfromserializedmodel(self):
        
        for name in self.serializedsearchmodel:
            row_data = self.serializedsearchmodel[name]
            ttype = row_data[TargetHeaders.TYPE]
            xtype = row_data[TargetHeaders.XSLOTS]
            svi = row_data[TargetHeaders.VALUE]
            include = row_data[TargetHeaders.INCLUDE] 
            negative = row_data[TargetHeaders.NEGATIVE] 

            module_id = row_data[TargetHeaders.MODULE_ID]
            module = self.unserialize(ttype, row_data[TargetHeaders.MODULE]) 
            
            assocrelnmodule_id = row_data[TargetHeaders.ASSOCRELNMODULE_ID]
            assocrelnmodule = self.unserialize(ModuleTypes.RELATION, row_data[TargetHeaders.ASSOCRELNMODULE]) 
            

            target = SearchTargetItem(name, targettype=ttype, xslottype=xtype, searchvaluesitem=svi, module=module, module_id=module_id, negative=negative, include=include, associatedrelnmodule=assocrelnmodule, associatedrelnmodule_id=assocrelnmodule_id)
            
            # logging.warning(f"{ttype}. setting value of module id: {module_id}")
            row = self.create_row_from_target(target)
            self.appendRow(row)
    
    def serialize(self):
        # return self.sign.serialize()
        return SearchModelSerializable(self)
 
    def create_row_from_target(self, t):

        name = QStandardItem(t.name)
        name.setData(t.module, Qt.UserRole)
        name.setData(t.associatedrelnmodule, Qt.UserRole+1)
        name.setData(t.module_id, Qt.UserRole+2)
        name.setData(t.associatedrelnmodule_id, Qt.UserRole+3)


        ttype = QStandardItem(t.targettype)

        include_cb = QStandardItem()
        include_cb.setCheckable(True)
        include_cb.setCheckState(t.include)

        negative_cb = QStandardItem()
        negative_cb.setCheckable(True)
        negative_cb.setCheckState(t.negative)

        xslottype = QStandardItem()
        xslottype.setData(repr(t.xslottype), Qt.DisplayRole)
        xslottype.setData(t.xslottype, Qt.UserRole)
        
        value = QStandardItem()
        value.setData(t.searchvaluesitem, Qt.UserRole+1) # TODO update
        value.setData(t.displaystring(), Qt.DisplayRole)
        

        return [name, ttype, value, include_cb, negative_cb, xslottype]

    def modify_target(self, t, row):
        row_data = self.create_row_from_target(t)
        for col, data in enumerate(row_data):
            self.setItem(row, col, data)


    def add_target(self, t):     
        self.appendRow(self.create_row_from_target(t))

    
    def get_selected_rows(self):
        rows = []
        for row in range(self.rowCount()):
            if self.is_included(row):
                rows.append(row)
        return rows

    def search_corpus(self, corpus): # TODO potentially add a rows_to_skip for adding on to existing results table
        corpusname = os.path.split(corpus.path)[1]
        selected_rows = self.get_selected_rows()       
        resultsdict = {}
        

        if self.matchdegree == 'all':
            # Create a dictionary to store like targets together. Keys are target type, values are lists containing row numbers.
            negative_rows = [] 
            target_dict = defaultdict(list) 
            display_vals = []
            for row in selected_rows:
                target_dict[self.target_type(row)].append(row)
                display_vals.append(self.target_display(row))
                if self.is_negative(row):
                    negative_rows.append("Negative")
                else:
                    negative_rows.append("Positive")
            target_name = tuple(self.target_name(row) for row in selected_rows)
            matchingsigns = []
            for sign in corpus.signs:
                if self.sign_matches_target(sign, target_dict):
                    matchingsigns.append(sign.signlevel_information)
            resultsdict[target_name] = {"corpus": corpusname, "display": display_vals,"signs": matchingsigns, "negative": negative_rows}
        
        elif self.matchdegree == 'any':
            for row in selected_rows:
                negative_rows = [] 
                target_dict = {self.target_type(row): [row]}
                if self.is_negative(row):
                    negative_rows.append("Negative")
                else:
                    negative_rows.append("Positive")
                target_name = self.target_name(row)
                matchingsigns = [] # each element is a gloss/id tuple
                for sign in corpus.signs:
                    if self.sign_matches_target(sign, target_dict):
                        matchingsigns.append(sign.signlevel_information)
                resultsdict[target_name] = {"corpus": corpusname, "display": self.target_display(row), "signs": matchingsigns, "negative": negative_rows}

        return resultsdict
    
    def sign_matches_target(self, sign, target_dict=None):
        # ORDER: xslot, sign level, sign type, mvmt, locn, reln
        if TargetTypes.XSLOT in target_dict:
            if not self.sign_matches_xslot(target_dict[TargetTypes.XSLOT], sign):
                return False
            
        if TargetTypes.SIGNLEVELINFO in target_dict:
            if not self.sign_matches_SLI(target_dict[TargetTypes.SIGNLEVELINFO], sign):
                return False

        if TargetTypes.SIGNTYPEINFO in target_dict:
            if not self.sign_matches_ST(target_dict[TargetTypes.SIGNTYPEINFO], sign):
                return False
        
        if ModuleTypes.HANDCONFIG in target_dict:
            hc_rows, ef_rows = [], []
            for r in target_dict[ModuleTypes.HANDCONFIG]:
                module_type = self.target_module(r).moduletype
                if module_type == ModuleTypes.HANDCONFIG:
                    hc_rows.append(r)
                elif module_type == TargetTypes.EXTENDEDFINGERS:
                    ef_rows.append(r)

            if hc_rows and not self.sign_matches_handconfig(hc_rows, sign):
                return False

            if ef_rows and not self.sign_matches_extendedfingers(ef_rows, sign):
                return False

        if ModuleTypes.MOVEMENT in target_dict:
            if not self.sign_matches_mvmt(target_dict[ModuleTypes.MOVEMENT], sign):
                return False
        if ModuleTypes.LOCATION in target_dict:
            if not self.sign_matches_locn(target_dict[ModuleTypes.LOCATION], sign):
                return False
        if ModuleTypes.RELATION in target_dict: 
            modulelist = [m for m in sign.getmoduledict(ModuleTypes.RELATION).values()]
            if not modulelist: return False

            for row in target_dict[ModuleTypes.RELATION]:
                target_module = self.target_module(row)
                if not reln_module_matches(modulelist, target_module, target_is_assoc_reln=False):
                    return False
        for ttype in [TargetTypes.LOC_REL, TargetTypes.MOV_REL]:
            if ttype in target_dict:
                anchortype = ModuleTypes.LOCATION if ttype == TargetTypes.LOC_REL else ModuleTypes.MOVEMENT
                relationmodulelist = [m for m in sign.getmoduledict(ModuleTypes.RELATION).values() if m.relationy.linkedmoduletype == anchortype]
                if not relationmodulelist: return False
                
                for row in target_dict[ttype]:  
                    target_reln_module = self.target_associatedrelnmodule(row)
                    # logging.warning(f"target module: {self.target_module_id(row)}; assoc module: {self.target_associatedrelnmodule_id(row)}; ")
                    if not reln_module_matches(relationmodulelist, target_reln_module, target_is_assoc_reln=True):
                        return False    
                    anchormodulelist = []
                    for m in relationmodulelist:
                        anchormod = sign.getmoduledict(anchortype)[m.relationy.linkedmoduleids[0]]
                        anchormodulelist.append(anchormod)

                    if ttype == TargetTypes.LOC_REL:
                        if not locn_module_matches(anchormodulelist, self.target_module(row)): return False
                    elif ttype == TargetTypes.MOV_REL:
                        if not mvmt_module_matches(anchormodulelist, self.target_module(row)): return False
                return True

        return True
    
    def sign_matches_xslot(self, rows, sign):
        # this is a minimal match
        numxslots = sign.xslotstructure.number
        if self.matchtype == 'minimal':
            for row in rows: # 
                min = self.target_values(row).values["xslot min"]
                max = self.target_values(row).values["xslot max"]
                if min == '': # only max specified
                    if numxslots <= int(max):
                        return True
                elif max == '': # only min specified
                    if numxslots >= int(min):
                        return True
                else:
                    if int(min) <= numxslots and numxslots <= int(max):
                        return True
            return False
        elif self.matchtype == 'exact':
            for row in rows:
                min = self.target_values(row).values["xslot min"]
                max = self.target_values(row).values["xslot max"]
                if min == '': # only max specified
                    if numxslots > int(max):
                        return False
                elif max == '': # only min specified
                    if numxslots < int(min):
                        return False
                else:
                    if int(min) > numxslots or numxslots > int(max):
                        return False
            return True     
    
    def sign_matches_SLI(self, sli_rows, sign):
        '''Returns True if the sign matches all specified rows (corresponding to SLI targets)'''
        
        binary_vals = {
            "fingerspelled": sign.signlevel_information.fingerspelled,
            "compoundsign": sign.signlevel_information.compoundsign,
            "handdominance": sign.signlevel_information.handdominance
        }
        date_vals = {
            "datecreated": sign.signlevel_information.datecreated,
            "datelastmodified": sign.signlevel_information.datelastmodified
        }
        text_vals = {
            "gloss": sign.signlevel_information.gloss,
            "entryid": sign.signlevel_information.entryid,
            "idgloss": sign.signlevel_information.idgloss,
            "lemma": sign.signlevel_information.lemma,
            "source": sign.signlevel_information.source,
            "signer": sign.signlevel_information.signer,
            "frequency": sign.signlevel_information.frequency,
            "coder": sign.signlevel_information.coder,
            "note": sign.signlevel_information.note
        }

        # CHECK TEXT PROPERTIES
        for val in text_vals:
            target_vals = []
            for row in sli_rows:
                this_val = self.target_values(row).values[val]
                if this_val not in [None, ""]:
                    target_vals.append(this_val)
            if val == "gloss":
                if not all(x in text_vals["gloss"] for x in target_vals):
                    return False
            else:
                if len(target_vals) > 1:
                    return False
                if len(target_vals) == 1:
                    # logging.warning("checking text val " + val + " is " + target_vals[0])
                    if text_vals[val] != target_vals[0]:
                        return False
        # CHECK BINARY PROPERTIES
        for val in binary_vals:
            target_vals = []
            for row in sli_rows:
                this_val = self.target_values(row).values[val]
                if this_val not in [None, ""]:
                    target_vals.append(this_val)
            if len(target_vals) > 1 and not all(x == target_vals[0] for x in target_vals):
                return False
            if len(target_vals) == 1:
                # logging.warning("checking binary val " + val + " is " + target_vals[0])
                if binary_vals[val] != target_vals[0]:
                    return False
        return True
    
    def sign_matches_ST(self, rows, sign):
        if sign.signtype is None:
            sign_st = []
        else:
            sign_st = signtypedisplaytext(sign.signtype.specslist)
        specs = set("")
        for row in rows:
            specs.update(signtypedisplaytext(self.target_module(row).specslist))
            # TODO what if a sign type target is present but nothing is specified? i.e. len(specs) = 0
            if len(sign_st) == 0 and len(specs) > 0:
                return False
            
        if not all (s in sign_st for s in specs):
            return False
        return True

    def sign_matches_handconfig(self, rows, sign):
        
        matching_modules = [m for m in sign.getmoduledict(ModuleTypes.HANDCONFIG).values()]

        for row in rows:
            matches_this_row = []
            target_module = self.target_module(row)
            target_forearm = target_module.overalloptions['forearm']
            # TODO: overalloptions['overall_addedinfo'], overalloptions['forearm_addedinfo']
            target_tuple = tuple(HandConfigurationHand(target_module.handconfiguration).get_hand_transcription_list())

            for m in matching_modules:
                sign_forearm = m.overalloptions['forearm']
                if sign_forearm == target_forearm: # Don't bother checking hand config if forearm doesn't match.
                    sign_tuple = tuple(HandConfigurationHand(m.handconfiguration).get_hand_transcription_list())
                    
                    # Searching for a custom tuple (not a predefined shape)
                    if target_tuple not in PREDEFINED_MAP: 
                        # items in certain positions are hardcoded for all tuples.
                        positions_to_check = [i for i in range(33) if i not in [6,7,14,19,24,29] and target_tuple[i] != ""]
                        # logging.warning(positions_to_check)
                        if all([target_tuple[i] == sign_tuple[i] for i in positions_to_check]):
                            matches_this_row.append(m)

                    # Searching for a predefined shape
                    else:
                        target_predefined_shape = PREDEFINED_MAP[target_tuple].name
                        if sign_tuple in PREDEFINED_MAP:
                            sign_shape = PREDEFINED_MAP[sign_tuple].name
                            # logging.warning(sign_shape)
                            if target_predefined_shape == sign_shape:
                                matches_this_row.append(m)   
            if len(matches_this_row) == 0:
                return False
            matching_modules = matches_this_row

        return True
        



    def sign_matches_extendedfingers(self, rows, sign):
        matching_modules = [m for m in sign.getmoduledict(ModuleTypes.HANDCONFIG).values()]
        extended_symbols = ['H', 'E', 'e']

        for row in rows:
            matches_this_row = []
            target_module = self.target_module(row)
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

            for m in matching_modules:
                sign_tuple = tuple(HandConfigurationHand(m.handconfiguration).get_hand_transcription_list())
                sign_ext_fingers = [finger for finger in range(5) if m.finger_is_extended(sign_tuple, extended_symbols, finger)]
                # logging.warning(f"target ext: {target_extended_fingers}. target not ext: {target_nonextended_fingers}. sign ext: {sign_ext_fingers}")


                if ((len(sign_ext_fingers) in target_extended_numbers or target_extended_numbers == [])  # TODO
                    and all(finger in sign_ext_fingers for finger in target_extended_fingers)
                    and all(finger not in sign_ext_fingers for finger in target_nonextended_fingers)):
                    matches_this_row.append(m)
                    # logging.warning("this module matches.")
            
            if len(matches_this_row) == 0:
                return False
            matching_modules = matches_this_row


        return True

    def sign_matches_reln(self, rows, sign):
        matching_modules = [m for m in sign.getmoduledict(ModuleTypes.RELATION).values()]
        if len(matching_modules) == 0:
            return False
        for row in rows:
            svi = self.target_values(row) 
            xslottype = self.target_xslottype(row)
            target_module = self.target_module(row)

            # All relation_x possibilities are mutually exclusive, so check if target relation_x matches at least one of sign's relation_xs
            target_relationx = target_module.relationx.displaystr()
            if target_relationx != "":
                matching_modules = [m for m in matching_modules if target_relationx == m.relationx.displaystr()]
                if len(matching_modules) == 0: return False

            # If target relation_y is "Existing module", this can also match "existing module - locn" or "existing module - mvmt".
            # Otherwise, relation_y possibilities are mutually exclusive.
            target_relationy = target_module.relationy.displaystr()
            if target_relationy != "": 
                if target_relationy == "Y: existing module":
                    matching_modules = [m for m in matching_modules if target_relationy in m.relationy.displaystr()]
                else:
                    matching_modules = [m for m in matching_modules if target_relationy == m.relationy.displaystr()]
                if len(matching_modules) == 0: return False
            # If target contact is only "Contact", this needs to match contact type suboptions (light, firm, other)
            # If target contact is "No contact", must match signs where contact is not specified or empty (?)
            # Manner options are mutually exclusive.
            if target_module.contactrel.contact is False: # if False, then "no contact" specified
                matching_modules = [m for m in matching_modules if m.contactrel.contact == False]
            elif target_module.contactrel.contact is not None:
                if target_module.contactrel.contacttype.any:
                    matching_modules = [m for m in matching_modules if m.contactrel.has_contacttype()]
                    if len(matching_modules) == 0: return False   
                elif target_module.contactrel.has_contacttype(): # module must match contacttype exactly
                    matching_modules = [m for m in matching_modules if m.contactrel.contacttype == target_module.contactrel.contacttype]
                    if len(matching_modules) == 0: return False 
                if target_module.contactrel.manner.any:
                    matching_modules = [m for m in matching_modules if m.contactrel.has_manner()]
                    if len(matching_modules) == 0: return False  
                elif target_module.contactrel.has_manner(): # module must match manner (and have some contact / contacttype)
                    matching_modules = [m for m in matching_modules if m.contactrel.manner == target_module.contactrel.manner]
                    if len(matching_modules) == 0: return False 
                else: # only "contact" specified, so module must have some contact / contacttype
                    matching_modules = [m for m in matching_modules if m.contactrel.contact]
            if len(matching_modules) == 0: return False 
            
            # direction:
            if len(target_module.directions) == 1 and target_module.directions[0].any: 
                matching_modules = [m for m in matching_modules if m.has_any_direction()]
            else:
                if target_module.xy_linked:
                    matching_modules = [m for m in matching_modules if m.xy_linked]
                if target_module.xy_crossed:
                    matching_modules = [m for m in matching_modules if m.xy_crossed]
                for i in range(3):
                    if target_module.directions[i].axisselected:
                        if target_module.has_direction(i): # match exactly because suboption is selected
                            matching_modules = [m for m in matching_modules if m.directions[i] == target_module.directions[i]]
                        else: # only axis is selected, so match if any suboption is selected
                            matching_modules = [m for m in matching_modules if m.has_direction(i)]
            if len(matching_modules) == 0:
                return False
            
            # Distance:
            if not target_module.contactrel.contact:
                if len(target_module.contactrel.distances) == 1 and target_module.contactrel.distances[0].any: 
                    matching_modules = [m for m in matching_modules if m.has_any_distance()]
                else:
                    for i in range(len(target_module.contactrel.distances)):
                        dist = target_module.contactrel.distances[i]
                        if dist.has_selection():
                            matching_modules = [m for m in matching_modules if m.contactrel.distances[i].has_selection()]
                                
                if len(matching_modules) == 0:
                    return False
            
            
            # Paths
            if hasattr(svi, "paths"):
                target_dict = target_module.get_paths()
                
                flag = False
                for m in matching_modules:
                    sign_dict = m.get_paths()
                    matching_keys = [k for k in sign_dict.keys() if k in target_dict.keys()]
                    for k in matching_keys:
                        if all(p in sign_dict[k] for p in target_dict[k]):
                            flag = True
                            break
                if not flag:
                    return False

        return True


    def sign_matches_mvmt(self, mvmt_rows, sign):
        modules = [m for m in sign.getmoduledict(ModuleTypes.MOVEMENT).values()]
        if len(modules) == 0:
            return False
        for row in mvmt_rows:
            xslottype = self.target_xslottype(row).type
            target_module = self.target_module(row)
            svi = self.target_values(row)
            arts = articulatordisplaytext(svi.articulators, svi.inphase) if hasattr(svi, "articulators") else ""
            if arts:
                sign_arts = set()
                for module in modules:
                    sign_arts.add(articulatordisplaytext(module.articulators, module.inphase))
                if arts not in sign_arts:
                    return False
            if hasattr(svi, "paths"):
                sign_paths = set()
                for module in modules:
                    if module_matches_xslottype(module.timingintervals, target_module.timingintervals, xslottype, sign.xslotstructure, self.matchtype):
                        for p in module.movementtreemodel.get_checked_items():
                            sign_paths.add(p)
                if not all(path in sign_paths for path in svi.paths):
                    return False
                    
        return True
    
    # locn_rows is not None
    def sign_matches_locn(self, locn_rows, sign):
        
        matching_modules = [m for m in sign.getmoduledict(ModuleTypes.LOCATION).values()]
        if len(matching_modules) == 0:
            return False
        
        terminate_early = True if len(locn_rows) == 1 else False
        for row in locn_rows:
            # TODO match xslottype
            target_module = self.target_module(row)
            if target_module.has_articulators():
                target_art = articulatordisplaytext(target_module.articulators, target_module.inphase)
                matching_modules = [m for m in matching_modules if articulatordisplaytext(m.articulators, m.inphase) == target_art]
                if not matching_modules: return False

            if not target_module.locationtreemodel.locationtype.allfalse():
                target_loctype = loctypedisplaytext(target_module.locationtreemodel.locationtype)
                matching_modules = [m for m in matching_modules if loctypedisplaytext(m.locationtreemodel.locationtype) == target_loctype]
                if not matching_modules: return False

            if not target_module.phonlocs.allfalse():
                target_phonlocs = phonlocsdisplaytext(target_module.phonlocs)
                matching_modules = [m for m in matching_modules if phonlocsdisplaytext(m.locationtreemodel.locationtype) == target_phonlocs]
                if not matching_modules: return False
            
            fully_checked = target_module.locationtreemodel.nodes_are_terminal
            target_paths = target_module.locationtreemodel.get_checked_items(only_fully_checked=fully_checked, include_details=True)
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
                                                                matchtype=self.matchtype, 
                                                                terminate_early=terminate_early)
                if not matching_modules: return False     

        return True
    
    def sign_matches_locn_old(self, locn_rows, sign):
        
        modules = [m for m in sign.getmoduledict(ModuleTypes.LOCATION).values()]
        if len(modules) == 0:
            return False
        for row in locn_rows:
            svi = self.target_values(row)
            xslottype = self.target_xslottype(row).type
            target_module = self.target_module(row)
            arts = articulatordisplaytext(svi.articulators, svi.inphase) if hasattr(svi, "articulators") else ""
            loctype = loctypedisplaytext(svi.loctype) if hasattr(svi, "loctype") else ""
            phonloc = phonlocsdisplaytext(svi.phonlocs) if hasattr(svi, "phonlocs") else ""
            paths = svi.paths if hasattr(svi, "paths") else []
            if arts:
                sign_arts = set()
                for module in modules:
                    sign_arts.add(articulatordisplaytext(module.articulators, module.inphase))
                if arts not in sign_arts:
                    return False
            if loctype:
                sign_loctypes = set()
                for module in modules:
                    sign_loctypes.add(loctypedisplaytext(module.locationtreemodel.locationtype))
                if loctype not in sign_loctypes:
                    return False
            if phonloc:
                sign_phonlocs = set()
                for module in modules:
                    sign_phonlocs.add(phonlocsdisplaytext(module.phonlocs))
                if phonloc not in sign_phonlocs:
                    return False
            if paths:
                sign_paths = set()
                for module in modules:
                    if (not arts or arts == articulatordisplaytext(module.articulators, module.inphase) 
                        and (not loctype or loctype == loctypedisplaytext(module.locationtreemodel.locationtype))
                        and (not phonloc or phonloc == phonlocsdisplaytext(module.phonlocs))
                        and module_matches_xslottype(module.timingintervals, target_module.timingintervals, xslottype, sign.xslotstructure, self.matchtype)
                        ):
                        fully_checked = target_module.locationtreemodel.nodes_are_terminal
                        # module_paths is a list of dicts {'path', 'abbrev', 'details'}. 
                        # To create a unique set of paths from all modules, convert the dicts to tuples.
                        module_paths = module.locationtreemodel.get_checked_items(only_fully_checked=fully_checked, include_details=True)
                        for mp in module_paths:
                            # details_tuple is tuple(tuple(), tuple())
                            details_tuple = tuple(tuple(selecteddetails) for label, selecteddetails in mp['details'].get_checked_values().items())
                            sign_paths.add((mp['path'], details_tuple))
                

                # exact match for details tables
                # if not all(path in sign_paths for path in svi.paths):
                #     return False

                # minimal match for details tables
                if all(path in sign_paths for path in paths):
                    return True
                else:
                    details_dict = defaultdict(set) # for faster lookup, sort by paths
                    for p in sign_paths:
                        details_dict[p[0]].add(p[1])

                    for targetpath in svi.paths:
                        if targetpath[0] not in details_dict: 
                            return False
                        potential_details_matches = details_dict[targetpath[0]] # a set of nested tuples ((), ())
                        targetdetails = [set(td) for td in targetpath[1]] # eg [set(surface1, surface2), set(bonejoint1)]
                        if not any(all(targetdetails[i] <= set(potential[i]) for i in range(len(targetdetails))) for potential in potential_details_matches):
                            return False

                    
        return True

    def unserialize(self, type, serialmodule): # TODO reduce repetition by combining param modules?
        if serialmodule is not None:
            if type in [ModuleTypes.MOVEMENT, TargetTypes.MOV_REL]:
                mvmttreemodel = MovementTreeModel(serialmodule.movementtree)
                articulators = serialmodule.articulators
                inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
                timingintervals = serialmodule.timingintervals
                addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
                phonlocs = serialmodule.phonlocs
                unserialized = MovementModule(mvmttreemodel, articulators, timingintervals, phonlocs, addedinfo, inphase)
                
                return unserialized
            elif type in [ModuleTypes.LOCATION, TargetTypes.LOC_REL]:
                locntreemodel = LocationTreeModel(serialmodule.locationtree)
                articulators = serialmodule.articulators
                inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
                timingintervals = serialmodule.timingintervals
                addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # 
                phonlocs = serialmodule.phonlocs
                unserialized = LocationModule(locntreemodel, articulators, timingintervals, phonlocs, addedinfo, inphase)
                return unserialized
            elif type == ModuleTypes.RELATION:

                articulators = serialmodule.articulators
                timingintervals = serialmodule.timingintervals
                addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()
                relationx = serialmodule.relationx
                relationy = serialmodule.relationy
                bodyparts_dict = {
                    HAND: {
                        1: BodypartInfo(
                            bodyparttype=HAND,
                            bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND, serializedlocntree=serialmodule.bodyparts_dict[HAND][1].bodyparttree),
                            addedinfo=serialmodule.bodyparts_dict[HAND][1].addedinfo),
                        2: BodypartInfo(
                            bodyparttype=HAND,
                            bodyparttreemodel=BodypartTreeModel(bodyparttype=HAND, serializedlocntree=serialmodule.bodyparts_dict[HAND][2].bodyparttree),
                            addedinfo=serialmodule.bodyparts_dict[HAND][2].addedinfo),
                    },
                    ARM: {
                        1: BodypartInfo(
                            bodyparttype=ARM,
                            bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM, serializedlocntree=serialmodule.bodyparts_dict[ARM][1].bodyparttree),
                            addedinfo=serialmodule.bodyparts_dict[ARM][1].addedinfo),
                        2: BodypartInfo(
                            bodyparttype=ARM,
                            bodyparttreemodel=BodypartTreeModel(bodyparttype=ARM, serializedlocntree=serialmodule.bodyparts_dict[ARM][2].bodyparttree),
                            addedinfo=serialmodule.bodyparts_dict[ARM][2].addedinfo),
                    },
                    LEG: {
                        1: BodypartInfo(
                            bodyparttype=LEG,
                            bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG, serializedlocntree=serialmodule.bodyparts_dict[LEG][1].bodyparttree),
                            addedinfo=serialmodule.bodyparts_dict[LEG][1].addedinfo),
                        2: BodypartInfo(
                            bodyparttype=LEG,
                            bodyparttreemodel=BodypartTreeModel(bodyparttype=LEG, serializedlocntree=serialmodule.bodyparts_dict[LEG][2].bodyparttree),
                            addedinfo=serialmodule.bodyparts_dict[LEG][2].addedinfo),
                    },
                }
                contactrel = serialmodule.contactrel
                xy_crossed = serialmodule.xy_crossed
                xy_linked = serialmodule.xy_linked
                directions = serialmodule.directions

                unserialized = RelationModule(relationx, relationy, bodyparts_dict, contactrel,
                                             xy_crossed, xy_linked, directionslist=directions,
                                             articulators=articulators, timingintervals=timingintervals,
                                             addedinfo=addedinfo)
                return unserialized
            elif type in [TargetTypes.SIGNTYPEINFO, ModuleTypes.HANDCONFIG, TargetTypes.EXTENDEDFINGERS]:
                return serialmodule

        else:
            return None

    def __repr__(self):
        repr = "searchmodel:\n " + str(self.matchtype) + " match; " +  "match " + str(self.matchdegree) + "\n" + str(self.searchtype) + " search"
        return repr
    
    def target_name(self, row):
        return self.index(row, TargetHeaders.NAME).data(Qt.DisplayRole)

    def target_module(self, row):
        return self.index(row, TargetHeaders.NAME).data(Qt.UserRole)
    
    def target_associatedrelnmodule(self, row):
        return self.index(row, TargetHeaders.NAME).data(Qt.UserRole+1)
    
    def target_module_id(self, row):
        return self.index(row, TargetHeaders.NAME).data(Qt.UserRole+2)
    
    def target_associatedrelnmodule_id(self, row):
        return self.index(row, TargetHeaders.NAME).data(Qt.UserRole+3)
    
    def target_type(self, row):
        return self.index(row, TargetHeaders.TYPE).data(Qt.DisplayRole)
    
    def target_xslottype(self, row):
        return self.index(row, TargetHeaders.XSLOTS).data(Qt.UserRole)

    def target_display(self, row):
        return self.index(row, TargetHeaders.VALUE).data(Qt.DisplayRole)
    
    def target_values(self, row):
        return self.index(row, TargetHeaders.VALUE).data(Qt.UserRole+1)

    def is_negative(self, row):
        return (self.itemFromIndex(self.index(row, TargetHeaders.NEGATIVE)).checkState() != Qt.Unchecked)

    def is_included(self, row):
        return (self.itemFromIndex(self.index(row, TargetHeaders.INCLUDE)).checkState() != Qt.Unchecked)
    
    @property
    def targets(self):
        return self._targets
    @targets.setter
    def targets(self, value):
        self._targets = value
    @property
    def matchtype(self):
        return self._matchtype

    @matchtype.setter
    def matchtype(self, value):
        self._matchtype = value

    @property
    def matchdegree(self):
        return self._matchdegree

    @matchdegree.setter
    def matchdegree(self, value):
        self._matchdegree = value

    @property
    def searchtype(self):
        return self._searchtype

    @searchtype.setter
    def searchtype(self, value):
        self._searchtype = value



# This class is a serializable form of the class SearchModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class SearchModelSerializable:

    def __init__(self, searchmodel):
        # self.sign = searchmodel.sign
        self.serializedmodel = self.collectdatafromSearchModel(searchmodel)
        

    def collectdatafromSearchModel(self, searchmodel):
        model = {}
        if searchmodel is not None:
            for r in range(searchmodel.rowCount()):
                row_data = {} 
                name = searchmodel.target_name(r)
                ttype = searchmodel.target_type(r)
                row_data[TargetHeaders.TYPE] = ttype
                row_data[TargetHeaders.VALUE] = searchmodel.target_values(r)
                row_data[TargetHeaders.INCLUDE] = searchmodel.is_included(r)
                row_data[TargetHeaders.NEGATIVE] = searchmodel.is_negative(r)
                row_data[TargetHeaders.XSLOTS] = searchmodel.target_xslottype(r)

                if ttype == TargetTypes.LOC_REL:
                    module = self.get_serialized_parameter_module(ModuleTypes.LOCATION, searchmodel.target_module(r))
                elif ttype == TargetTypes.MOV_REL:
                    module = self.get_serialized_parameter_module(ModuleTypes.MOVEMENT, searchmodel.target_module(r))
                else:                    
                    module = self.get_serialized_parameter_module(ttype, searchmodel.target_module(r))
                row_data[TargetHeaders.MODULE] = module
                row_data[TargetHeaders.MODULE_ID] = searchmodel.target_module_id(r)
                associatedrelnmodule = searchmodel.target_associatedrelnmodule(r)
                row_data[TargetHeaders.ASSOCRELNMODULE] = self.get_serialized_parameter_module(ModuleTypes.RELATION, associatedrelnmodule) if associatedrelnmodule is not None else None
                row_data[TargetHeaders.ASSOCRELNMODULE_ID] = searchmodel.target_associatedrelnmodule_id(r)
                model[name] = row_data  

                # logging.warning(f"Saving: {name}, {ttype}, module: {row_data[TargetHeaders.MODULE_ID]},  associatedrelnmodule: {row_data[TargetHeaders.ASSOCRELNMODULE_ID]} ")
        return model
    
    def get_serialized_parameter_module(self, type, module):
        if type == ModuleTypes.MOVEMENT:
            return MovementModuleSerializable(module)
        if type == ModuleTypes.LOCATION:
            return LocationModuleSerializable(module)
        if type == ModuleTypes.RELATION:
            return RelationModuleSerializable(module)
        else:
            return module

# Only store values that are included in the search target 
# e.g. if no paths are specified in the target, don't save a self.paths attribute
class SearchValuesItem:
    def __init__(self, type, module=None, values=None): # TODO consider if module and values parameters are needed here (module is already saved in model under name)
        self.type = type 
        self.values = values
        self.assign_attributes(module)
    
    def has_added_info(self, module):
        return module.addedinfo is not None


    def __repr__(self):
        return str(self.displayval)
    
    # for displaying in the "value" column of the searchmodel. Returns a list.
    def assign_attributes(self, module): # TODO consider if module can be an attribute (remove the module saved in searchmodel under name)
        '''Saves module attributes: e.g. parameter modules have articulators, inphase, paths attributes; 
        location module specifically has phonlocs and loctype attributes, etc. Also assigns the list to be displayed in the "values" column of the searchmodel.'''
        todisplay = []
        if self.type in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION]: 
            if module.articulators[1][1] or module.articulators[1][2]: # between articulator 1 and articulator 2, at least one is True
                self.articulators = module.articulators
                self.inphase = module.inphase
                # todisplay.append(articulatordisplaytext(module.articulators, module.inphase))
            if self.has_added_info(module):
                pass
                # todisplay.append("Additional info") # TODO could be more specific re type / contents of additional info
            paths = []
            if self.type == ModuleTypes.MOVEMENT:
                paths = module.movementtreemodel.get_checked_items()
                if len(paths) > 0: self.paths = paths
            elif self.type == ModuleTypes.LOCATION:
                # paths is a list of dicts: "path", "abbrev", "details"
                paths = module.locationtreemodel.get_checked_items(only_fully_checked=True, include_details=True)
                # convert to a list of tuples, since that's what we'll try to match when searching
                if len(paths) > 0:
                    self.paths = []
                    for p in paths:
                        # details_tuple is tuple([], [])
                        details_tuple = tuple(tuple(selecteddetails) for label, selecteddetails in p['details'].get_checked_values().items())
                        self.paths.append((p['path'], details_tuple))
                if not module.phonlocs.allfalse():
                    self.phonlocs = module.phonlocs
                    # todisplay.extend(phonlocsdisplaytext(self.phonlocs))
                if not module.locationtreemodel.locationtype.allfalse():
                    self.loctype = module.locationtreemodel.locationtype
                    # todisplay.extend(loctypedisplaytext(self.loctype))
            else: # relation
                # paths is a dict matching selected articulators to a list of dicts: "path", "abbrev", "details"
                paths = module.get_paths()
                if len(paths) > 0:
                    self.paths = paths # TODO
                # todisplay.extend(relationdisplaytext(module))

        
        # elif self.type == TargetTypes.SIGNTYPEINFO:
            # todisplay.extend(signtypedisplaytext(module.specslist))
        # else:
        #     if self.values is not None:
        #         for k, v in self.values.items():
        #             if v not in [None, ""]:
        #                 todisplay.append(str(k)+"="+str(v))
        
        self.displayval = todisplay
    