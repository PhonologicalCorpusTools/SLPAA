import io


import copy 
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel, 
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QDialog
)
from PyQt5.QtWidgets import QStyledItemDelegate, QMessageBox

from PyQt5.QtCore import QModelIndex, Qt
from gui.panel import SignLevelMenuPanel
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, MovementModule
from constant import XSLOT_TARGET, SIGNLEVELINFO_TARGET, SIGNTYPEINFO_TARGET
import logging

from models.movement_models import MovementTreeModel
from serialization_classes import LocationModuleSerializable, MovementModuleSerializable, RelationModuleSerializable





class TargetHeaders:
    NAME = 0
    TYPE = 1
    VALUE = 2
    INCLUDE = 3
    NEGATIVE = 4
    XSLOTS = 5




class SearchModel(QStandardItemModel):
    def __init__(self, serializedsearchmodel=None,**kwargs):
        super().__init__(**kwargs)
        self.name = None
        self.path = None
        self._matchtype = None # exact / minimal
        self._matchdegree = None # any / all
        self._searchtype = None # new / add

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
            module = self.unserialize(ttype, row_data["module"]) 

            target = SearchTargetItem(name, targettype=ttype, xslottype=xtype, searchvaluesitem=svi, module=module, negative=negative, include=include)
            row = self.create_row_from_target(target)
            self.appendRow(row)
    
    def serialize(self):
        return SearchModelSerializable(self)
 
    def create_row_from_target(self, t):

        name = QStandardItem(t.name)
        name.setData(t.module, Qt.UserRole)

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
        value.setData(t.searchvaluesitem, Qt.UserRole+1)
        value.setData(t.searchvaluesitem.displayval, Qt.DisplayRole)
        

        return [name, ttype, value, include_cb, negative_cb, xslottype]

    def modify_target(self, t, row):
        row_data = self.create_row_from_target(t)
        for col, data in enumerate(row_data):
            self.setItem(row, col, data)

    
    def add_target(self, t):     
        self.appendRow(self.create_row_from_target(t))

    def get_selected_rows(self):
        row_numbers = []
        for row in range(self.rowCount()):
            if self.is_included(row):
                row_numbers.append(row)
        return row_numbers

    def search_corpus(self, corpus): # TODO potentially add a rows_to_skip for adding on to existing results table
        selected_rows = self.get_selected_rows()

        resultsdict = {}

        if self.matchdegree == 'all':
            target_name = tuple(self.target_name(row) for row in selected_rows)
            target_negative = []
            for row in selected_rows:
                if self.is_negative(row):
                    target_negative.append("Negative")
                else:
                    target_negative.append("Positive")
            matchingsigns = [] # each element is a gloss/id tuple
            for sign in corpus.signs:
                if self.sign_matches_all(selected_rows, sign):
                    matchingsigns.append([sign.signlevel_information.gloss, sign.signlevel_information.entryid])
            resultsdict[target_name] = {"corpus": corpus.name, "signs": matchingsigns, "negative": target_negative}
        return resultsdict

        # TODO for now, assume match type minimal, not exact
        # if self.matchdegree == 'all': #  
        #     mvmt_paths_to_match = []
        #     locn_paths_to_match = []

        #     for row in selected_rows:
        #         module = self.target_module(row)
        #         svi = self.target_values(row)
        #         ttype = self.target_type(row)
        #         if ttype == ModuleTypes.MOVEMENT:
        #             paths = module.movementtreemodel.get_checked_items()
        #             mvmt_paths_to_match.extend(paths)
        #         # eg if target_name is in rows_to_skip, continue
                
    def sign_matches_all(self, rows, sign):
        return True
        # for sign in corpus.signs:
        #     if len(mvmt_paths_to_match) > 0:
        #         # TODO switch to using the generic get module dict function 
        #         checked_mvmt_paths = set()
        #         for module in sign.movementmodules.values():
        #             checked_mvmt_paths.add(module.movementtreemodel.get_checked_items())
        #         logging.warning(checked_mvmt_paths)
        #         logging.warning(mvmt_paths_to_match)
        #         ok = all(path in checked_mvmt_paths for path in mvmt_paths_to_match)
        #         txt = sign.signlevel_information.gloss + " matches: " + str(ok)


    def unserialize(self, type, serialmodule):
        if serialmodule is not None:
            if type == ModuleTypes.MOVEMENT:
                mvmttreemodel = MovementTreeModel(serialmodule.movementtree)
                articulators = serialmodule.articulators
                inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
                timingintervals = serialmodule.timingintervals
                addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
                unserialized = MovementModule(mvmttreemodel, articulators, timingintervals, addedinfo, inphase)
                return unserialized
            elif type == SIGNTYPEINFO_TARGET:
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
    
    def target_type(self, row):
        return self.index(row, TargetHeaders.TYPE).data(Qt.DisplayRole)
    
    def target_xslottype(self, row):
        return self.index(row, TargetHeaders.XSLOTS).data(Qt.UserRole)
    
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

# TODO move the methods above into here?
class SearchTargetItem(QStandardItem):
    def __init__(self, name=None, targettype=None, xslottype=None, searchvaluesitem=None, module=None, negative=False, include=False, **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._targettype = targettype
        self._xslottype = xslottype 
        self._searchvaluesitem = searchvaluesitem
        self._module = module
        self.negative = negative
        self.include = include

    def __repr__(self):
        msg =  "Name: " + str(self.name) + "\nxslottype: " + str(self.xslottype) + "\nxslotnum: " + str(self.xslotnum) + "\ntargettype " + str(self.targettype)  
        msg += "\nValues: " + repr(self.values)
        return msg
    
    @property
    def targettype(self):
        return self._targettype

    @targettype.setter
    def targettype(self, value):
        self._targettype = value

    @property
    def searchvaluesitem(self):
        return self._searchvaluesitem

    @searchvaluesitem.setter
    def searchvaluesitem(self, v):
        self._searchvaluesitem = v
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def xslottype(self):
        return self._xslottype

    @xslottype.setter
    def xslottype(self, value):
        self._xslottype = value

    @property
    def module(self):
        return self._module
    
    @module.setter
    def module(self, m):
        self._module = m

class ResultsModel(QStandardItemModel):
    def __init__(self, searchmodel, corpus, **kwargs):
        super().__init__(**kwargs)


        # self.headers = ["Name", "Type", "Value", "Negative?",  "X-slots"]
        # self.setHorizontalHeaderLabels(self.headers)

        # try:
        #     index = searchmodel.index(0, 0)
        #     print(searchmodel.data(index))
        # except:
        #     print("couldt")
        # self.searchmodel = searchmodel
        # print(self.searchmodel)
        # index = self.searchmodel.index(0, 0)
        # name_txt = self.searchmodel.data(index)
        # for row in range(self.searchmodel.rowCount()):
        #      print(row)
            # if self.searchmodel.is_included(row):

                # print(name_txt)
                # name_txt = self.searchmodel.data(self.searchmodel.index(row, TargetHeaders.NAME))

                # self.setItem(row, ResultHeaders.NAME, QStandardItem(name_txt))
                # self.setItem(row, ResultHeaders.NEGATIVE, self.searchmodel.itemFromIndex(self.index(row, TargetHeaders.NEGATIVE)).clone())
                # self.setItem(row, ResultHeaders.XSLOTS, self.searchmodel.itemFromIndex(self.index(row, TargetHeaders.XSLOTS)).clone())


# This class is a serializable form of the class SearchModel, which is itself not pickleable.
# Rather than being based on QStandardItemModel, this one uses dictionary structures to convert to
# and from saveable form.
class SearchModelSerializable:

    def __init__(self, searchmodel):
        self.serializedmodel = self.collectdatafromSearchModel(searchmodel)
        

    # collect data from the LocationTreeModel to store in this LocationTreeSerializable
    def collectdatafromSearchModel(self, searchmodel):
        model = {}
        if searchmodel is not None:
            for r in range(searchmodel.rowCount()):
                row_data = {} 
                name = searchmodel.target_name(r)
                ttype = searchmodel.target_type(r)
                module = self.get_serialized_parameter_module(ttype, searchmodel.target_module(r))
                row_data[TargetHeaders.TYPE] = ttype
                row_data[TargetHeaders.VALUE] = searchmodel.target_values(r)
                row_data[TargetHeaders.INCLUDE] = searchmodel.is_included(r)
                row_data[TargetHeaders.NEGATIVE] = searchmodel.is_negative(r)
                row_data[TargetHeaders.XSLOTS] = searchmodel.target_xslottype(r)
                row_data["module"] = module

                model[name] = row_data  
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
        self.displayval = self.getdisplayval(module)
        
    def has_arts(self, module):
        return module.articulators[1][1] or module.articulators[1][2]
    
    def has_phase(self, module):
        return module.inphase
    
    def has_added_info(self, module):
        return module.addedinfo is not None

    def get_paths(self, model):
        return model.get_checked_items() 

    def __repr__(self):
        return str(self.displayval)
    
    # for displaying in the "value" column of the searchmodel. Returns a list.
    def getdisplayval(self, module): # TODO consider if module can be an attribute (remove the module saved in searchmodel under name)
        todisplay = []
        if self.type == ModuleTypes.MOVEMENT: # TODO parameter modules share many of these options
            if self.has_arts(module): # if articulators are specified
                todisplay.append(self.articulatordisplaytext(module.articulators, module.inphase))
            if self.has_added_info(module):
                pass
                # todisplay.append("Additional info") # TODO could be more specific re type / contents of additional info
            todisplay.extend(self.get_paths(module.movementtreemodel))
        elif self.type == SIGNTYPEINFO_TARGET:
            for v in module.specslist:
                if v[1]:
                    todisplay.append(v[0])
        else:
            if self.values is not None:
                for k, v in self.values.items():
                    if v not in [None, ""]:
                        todisplay.append(str(k)+"="+str(v))
        return todisplay
        
    def articulatordisplaytext(self, arts, phase):
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


        