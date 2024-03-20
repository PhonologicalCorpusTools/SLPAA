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

class ResultHeaders:
    NAME = 0
    TYPE = 1
    VALUE = 2
    NEGATIVE = 3
    XSLOTS = 4


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
        self.serializedsearchmodel = serializedsearchmodel
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

        type = QStandardItem(t.targettype)

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
        value.setData(t.searchvaluesitem.displayval(t.module), Qt.DisplayRole)
        value.setData(t.searchvaluesitem, Qt.UserRole+1)

        return [name, type, value, include_cb, negative_cb, xslottype]

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
        dialog = QDialog()
        layout = QVBoxLayout()

        # TODO for now, assume match type minimal, not exact
        if self.matchdegree == 'all': #  
            mvmt_paths_to_match = []
            locn_paths_to_match = []

            for row in selected_rows:
                ttype = self.target_type(row)
                if ttype == ModuleTypes.MOVEMENT:
                    mvmt_paths_to_match.extend(self.target_paths(row))
                # eg if target_name is in rows_to_skip, continue
                

            layout.addWidget(QLabel("matching mvmt"))
            for sign in corpus.signs:
                if len(mvmt_paths_to_match) > 0:
                    # TODO switch to using the generic get module dict function 
                    checked_mvmt_paths = {}
                    for module in sign.movementmodules.values():
                        checked_mvmt_paths.extend(module.movementtreemodel.get_checked_items())
                    logging.warning(checked_mvmt_paths)
                    logging.warning(mvmt_paths_to_match)
                    ok = all(path in checked_mvmt_paths for path in mvmt_paths_to_match)
                    txt = sign.signlevel_information.gloss + " matches: " + str(ok)
                    layout.addWidget(QLabel(txt))


        dialog.setLayout(layout)
        dialog.exec_()


    def unserialize(self, type, serialmodule):
        if type == ModuleTypes.MOVEMENT:
            mvmttreemodel = MovementTreeModel(serialmodule.movementtree)
            articulators = serialmodule.articulators
            inphase = serialmodule.inphase if (hasattr(serialmodule, 'inphase') and serialmodule.inphase is not None) else 0
            timingintervals = serialmodule.timingintervals
            addedinfo = serialmodule.addedinfo if hasattr(serialmodule, 'addedinfo') else AddedInfo()  # for backward compatibility with pre-20230208 movement modules
            unserialized = MovementModule(mvmttreemodel, articulators, timingintervals, addedinfo, inphase)
            return unserialized
        else:
            logging.warn("Unserialize not implemented for this type")
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
            row_data = {} 
            for r in range(searchmodel.rowCount()):
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

