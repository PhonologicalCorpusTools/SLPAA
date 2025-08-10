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
from constant import TargetTypes, HAND, ARM, LEG, HandConfigSlots, Precomputed
import logging, time

from models.movement_models import MovementTreeModel
from models.location_models import LocationTreeModel, BodypartTreeModel
from serialization_classes import LocationModuleSerializable, MovementModuleSerializable, RelationModuleSerializable
from search.helper_functions import *
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
        include_cb.setUserTristate(False)
        include_cb.setCheckState(Qt.Checked if t.include else Qt.Unchecked)

        negative_cb = QStandardItem()
        negative_cb.setCheckable(True)
        negative_cb.setUserTristate(False)
        negative_cb.setCheckState(Qt.Checked if t.negative else Qt.Unchecked)

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
    
    def precompute_targets(self, selected_rows):
        # TODO potentially update each time a new target is created.
        # we pre-compute some things such as movement and location paths
        # to avoid re-computing them each time we call a filter or sign_matches_ function
        # Done so far: 
        # Movement modules: set of checked paths
        # Location modules: list of dicts, where keys are checked paths and values
        
        for row in selected_rows:
            if self.target_type in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION]:
                self.target_module(row).compute_selections()
            
        
        

    def search_corpus(self, corpus): # TODO potentially add a rows_to_skip for adding on to existing results table
        corpusname = os.path.split(corpus.path)[1]
        selected_rows = self.get_selected_rows()       
        self.precompute_targets(selected_rows)
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
    
    def sign_matches_target(self, sign, target_dict={}):
        # ORDER: xslot, sign level, sign type, mvmt, locn, reln
        if TargetTypes.XSLOT in target_dict: # one module per sign
            if not self.sign_matches_xslot(target_dict[TargetTypes.XSLOT], sign):
                return False
            
        if TargetTypes.SIGNLEVELINFO in target_dict: # one module per sign
            if not self.sign_matches_SLI(target_dict[TargetTypes.SIGNLEVELINFO], sign):
                return False

        if TargetTypes.SIGNTYPEINFO in target_dict: # one module per sign
            if not self.sign_matches_ST(target_dict[TargetTypes.SIGNTYPEINFO], sign):
                return False
            
        # TODO: I added a quick fix for the problem where "match all" doesn't work for two targets with the same target / module type.
        # But there should be a better way to do this
        # E.g. save a module object containing the info from all targets of one type, and pass that to the "filter modules" functions (in mvmt, locn, and reln)
        
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
            
        if ModuleTypes.ORIENTATION in target_dict: 
            modules_to_check = [m for m in sign.getmoduledict(ModuleTypes.ORIENTATION).values()]
            target_rows = target_dict[ModuleTypes.ORIENTATION]
            for row in target_rows:
                target_module = self.target_module(row)
                orientation_matching = filter_modules_by_target_orientation(modules_to_check, target_module, matchtype=self.matchtype)
                if not (self.is_negative(row) ^ bool(orientation_matching)):
                    return False
        
        if ModuleTypes.MOVEMENT in target_dict:
            if not self.sign_matches_movement(target_dict[ModuleTypes.MOVEMENT], sign):
                return False
        
        if ModuleTypes.LOCATION in target_dict:
            if not self.sign_matches_location(target_dict[ModuleTypes.LOCATION], sign):
                return False

        for ttype in [ ModuleTypes.RELATION]:
            if ttype in target_dict:                
                modules_to_check = [m for m in sign.getmoduledict(ttype).values()]
                if not modules_to_check:
                    return False
                target_rows = target_dict[ttype]
                for row in target_rows:
                    matching_modules = modules_to_check
                    terminate_early = True if row == target_rows[-1] else False
                    target_module = self.target_module(row)
                    if ttype == ModuleTypes.LOCATION:
                        matching_modules = filter_modules_by_target_locn(matching_modules, target_module, matchtype=self.matchtype, terminate_early=terminate_early)
                    elif ttype == ModuleTypes.RELATION:
                        matching_modules = filter_modules_by_target_reln(matching_modules, target_module, matchtype=self.matchtype, terminate_early=terminate_early)

                    if not matching_modules: return False    

        for ttype in [TargetTypes.LOC_REL, TargetTypes.MOV_REL]:
            if ttype in target_dict:
                anchortype = ModuleTypes.LOCATION if ttype == TargetTypes.LOC_REL else ModuleTypes.MOVEMENT
                modules_to_check = [m for m in sign.getmoduledict(ModuleTypes.RELATION).values() if m.relationy.linkedmoduletype == anchortype]
                if not modules_to_check: return False
                target_rows = target_dict[ttype]
                for row in target_rows:  
                    matching_relation_modules = modules_to_check
                    terminate_early = True if row == target_rows[-1] else False
                    target_reln_module = self.target_associatedrelnmodule(row)
                    matching_relation_modules = filter_modules_by_target_reln(matching_relation_modules, target_reln_module, matchtype=self.matchtype, terminate_early=terminate_early)
                    if not matching_relation_modules: return False
                    anchormodulelist = []
                    for m in matching_relation_modules:
                        anchormod = sign.getmoduledict(anchortype)[m.relationy.linkedmoduleids[0]]
                        anchormodulelist.append(anchormod)
                        # TODO: terminate early?
                        if ttype == TargetTypes.LOC_REL:
                            anchormodulelist = filter_modules_by_target_locn(anchormodulelist, self.target_module(row), matchtype=self.matchtype, terminate_early=False)
                        elif ttype == TargetTypes.MOV_REL:
                            anchormodulelist = filter_modules_by_target_mvmt(anchormodulelist, self.target_module(row), matchtype=self.matchtype, terminate_early=False)
                        if not anchormodulelist: return False
        return True
    
    def sign_matches_xslot(self, rows, sign):
        # there's no difference between minimal and exact matchtypes for this module type.
        numxslots = int(sign.xslotstructure.number)
        for row in rows:
            min_val = self.target_module(row).min_xslots
            max_val = self.target_module(row).max_xslots
            if not (self.is_negative(row) ^ (min_val <= numxslots and numxslots <= max_val)):
                return False
        return True
            
  
    
    def sign_matches_SLI(self, sli_rows, sign):
        # TODO: handle Notes (AdditionalInfo)
        sli = sign.signlevel_information
        for row in sli_rows:
            target_sli = self.target_module(row)
            if not (self.is_negative(row) ^ signlevelinfo_matches_target(sli, target_sli, self.matchtype)):
                return False
        return True
    
    
    def sign_matches_ST(self, rows, sign):
        # TODO: handle Notes (AdditionalInfo)

        specs_dict = sign.signtype.convertspecstodict() if sign.signtype else {}
        for row in rows:
            target_specs_dict = self.target_module(row).convertspecstodict()
            if not (self.is_negative(row) ^ signtype_matches_target(specs_dict, target_specs_dict, self.matchtype)):
                return False
        return True


    def sign_matches_handconfig(self, rows, sign):
        
        modulelist = [m for m in sign.getmoduledict(ModuleTypes.HANDCONFIG).values()]

        for row in rows:
            target_module = self.target_module(row)
            if not (self.is_negative(row) ^ bool(filter_modules_by_target_handconfig(modulelist, target_module, self.matchtype))):
                return False
        return True
        
    def sign_matches_extendedfingers(self, rows, sign):
        matching_modules = [m for m in sign.getmoduledict(ModuleTypes.HANDCONFIG).values()]

        for row in rows:
            target_module = self.target_module(row)
            if not (self.is_negative(row) ^ bool(filter_modules_by_target_extendedfingers(matching_modules, target_module, self.matchtype))):
                return False
        return True
    
    def sign_matches_movement(self, rows, sign):
           
        modules_to_check = [m for m in sign.getmoduledict(ModuleTypes.MOVEMENT).values()]
        for row in rows:
            target_module = self.target_module(row)
            # if negative ("match signs not containing path xyz"), stop as soon as we find a module containing path xyz
            terminate_early = True if self.is_negative(row) else False 
            
            matching_modules = filter_modules_by_target_mvmt(modules_to_check, target_module, matchtype=self.matchtype, terminate_early=terminate_early)
            if not (self.is_negative(row) ^ bool(matching_modules)):
                return False
        return True
        
    def sign_matches_location(self, rows, sign):
        modules_to_check = [m for m in sign.getmoduledict(ModuleTypes.LOCATION).values()]
        for row in rows:
            target_module = self.target_module(row)            
            # if negative ("match signs not containing path xyz"), stop as soon as we find a module containing path xyz
            terminate_early = True if self.is_negative(row) else False 
            
            matching_modules = filter_modules_by_target_locn(modules_to_check, target_module, matchtype=self.matchtype, terminate_early=terminate_early)
            if not (self.is_negative(row) ^ bool(matching_modules)):
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
            else:
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
            # else: # relation
            #     # paths is a dict matching selected articulators to a list of dicts: "path", "abbrev", "details"
            #     paths = module.get_paths()
            #     if len(paths) > 0:
            #         self.paths = paths # TODO
                # todisplay.extend(relationdisplaytext(module))

        
        # elif self.type == TargetTypes.SIGNTYPEINFO:
            # todisplay.extend(signtypedisplaytext(module.specslist))
        # else:
        #     if self.values is not None:
        #         for k, v in self.values.items():
        #             if v not in [None, ""]:
        #                 todisplay.append(str(k)+"="+str(v))
        
        self.displayval = todisplay
    