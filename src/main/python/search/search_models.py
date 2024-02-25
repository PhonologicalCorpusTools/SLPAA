import io


import copy 
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel, 
    QMessageBox
)
from PyQt5.QtWidgets import QStyledItemDelegate, QMessageBox

from PyQt5.QtCore import QModelIndex, Qt
from gui.panel import SignLevelMenuPanel
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes
from constant import XSLOT_TARGET, SIGNLEVELINFO_TARGET, SIGNTYPEINFO_TARGET


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
    def __init__(self, targets=[], **kwargs):
        super().__init__(**kwargs)
        self._matchtype = None # exact / minimal
        self._matchdegree = None # any / all
        self._searchtype = None # new / add
        self._targets = targets # TODO necessary? for loading targets eventually?

        self.headers = ["Name", "Type", "Value", "Include?", "Negative?",  "X-slots"]
        
        self.setHorizontalHeaderLabels(self.headers)

        if len(targets) > 0:
            for t in targets:
                self.add_target(t)
    
    def get_row_data(self, t):
        type = QStandardItem(t.targettype)
        include_cb = QStandardItem()
        include_cb.setCheckable(True)
        negative_cb = QStandardItem()
        negative_cb.setCheckable(True)
        name = QStandardItem(t.name)

        if t.xslottype is not None: # TODO specify exactly which target types should have an xslottype or not
            if t.xslottype == "concrete":
                xslotval = t.xslotnum
                xslottype = QStandardItem(xslotval + " x-slots")
            else:
                xslottype = QStandardItem(t.xslottype)
            xslottype.setData((t.xslottype, t.xslotnum), Qt.UserRole + 1)
        else:
            xslottype = QStandardItem()
        
        val = []
        for k,v in t.values.items(): # two-valued targets
            if v not in [None, ""]:
                val.append(str(k)+"="+str(v))
        value = QStandardItem()
        value.setData(val, Qt.DisplayRole)
        value.setData(t.values, Qt.UserRole + 1)
        return [name, type, value, include_cb, negative_cb, xslottype]

    def modify_target(self, t, row):
        row_data = self.get_row_data(t)
        for col, data in enumerate(row_data):
            self.setItem(row, col, data)

    
    # TODO maybe change to be more tree like (hierarchy by type)
    def add_target(self, t):
        # self.targets.append(t) # need to deal with modifying targets
        self.appendRow(self.get_row_data(t))

        # # TODO insert in a better place depending on the type
        # finalrow = self.rowCount() 
        # finalcol = len(self.headers) - 1
        # self.rowsInserted.emit(QModelIndex(), self.index(finalrow, 0), self.index(finalrow, finalcol))



    def __repr__(self):
        repr = "searchmodel:\n " + str(self.matchtype) + " match; " +  "match " + str(self.matchdegree) + "\n" + str(self.searchtype) + " search"
        return repr


    def is_negative(self, row):
        return (self.itemFromIndex(self.index(row, TargetHeaders.NEGATIVE)).checkState() == Qt.Checked)

    def is_included(self, row):
        return (self.itemFromIndex(self.index(row, TargetHeaders.INCLUDE)).checkState() == Qt.Checked)
    
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

# TODO should we do different item classes for each targettype, instead of having a dict ?
class SearchTargetItem(QStandardItem):
    def __init__(self, name=None, targettype=None, xslottype=None, xslotnum=None, values=dict(), **kwargs):
        super().__init__(**kwargs)
        self._name = name
        self._targettype = targettype
        self._xslottype = xslottype 
        self._xslotnum = xslotnum # only set if xslottype is concrete
        self.values = values # TODO for binary targets (eg xslot_min=3). update for unary targets (eg list of location nodes)


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
    def xslotnum(self):
        if self._xslotnum == None:
            return "None"
    
        return self._xslotnum

    @xslotnum.setter
    def xslotnum(self, value):
        self._xslotnum = value

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
