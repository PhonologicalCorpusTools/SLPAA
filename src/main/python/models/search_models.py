import io


import copy 
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel,
    
)
from PyQt5.QtCore import QModelIndex
from gui.panel import SignLevelMenuPanel
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes
from constant import XSLOT_TARGET, SIGNLEVELINFO_TARGET, SIGNTYPEINFO_TARGET


class SearchModel(QStandardItemModel):
    def __init__(self, targets=[], **kwargs):
        super().__init__(**kwargs)
        self._matchtype = None # exact / minimal
        self._matchdegree = None # any / all
        self._searchtype = None # new / add
        self._targets = targets

        self.headers = ["Type", "Value","Include?", "Negative?",  "X-slots", "Name"]

        self.setHorizontalHeaderLabels(self.headers)

        if len(targets) > 0:
            for t in targets:
                self.add_target(t)
    
    # TODO maybe change to be more tree like (hierarchy by type)
    def add_target(self, t):
        self.targets.append(t)
        for k,v in t.dict.items(): # two-valued targets
            if v not in [None, ""]:
                type = QStandardItem(t.targettype)
                
                val = QStandardItem(str(k)+"="+str(v))
                xslottype = QStandardItem(t.xslottype)
                if xslottype is not None: # TODO
                    xslotval = xslottype
                    if xslottype == "concrete":
                        xslotval = t.xslotnum
                include_cb = QStandardItem()
                include_cb.setCheckable(True)
                negative_cb = QStandardItem()
                negative_cb.setCheckable(True)
                name = QStandardItem(t.name)
                self.appendRow([type, val, include_cb, negative_cb, xslottype, name])

        # # TODO insert in a better place depending on the type
        # finalrow = self.rowCount() 
        # finalcol = len(self.headers) - 1
        # self.rowsInserted.emit(QModelIndex(), self.index(finalrow, 0), self.index(finalrow, finalcol))




        

                


    def __repr__(self):
        repr = "searchmodel:\n " + str(self.matchtype) + " match; " +  "match " + str(self.matchdegree) + "\n" + str(self.searchtype) + " search"
        return repr

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

class SearchTargetItem(QStandardItem):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._name = None
        self._targettype = None
        self._xslottype = None 
        self._xslotnum = None # only set if xslottype is concrete
        self.dict = dict() # for binary targets (eg xslot_min=3). update for unary targets (eg list of location nodes)


    def __repr__(self):
        msg =  "Name: " + str(self.name) + "\nxslottype: " + str(self.xslottype) + "\nxslotnum: " + str(self.xslotnum) + "\ntargettype " + str(self.targettype)  
        msg += "\nDict: " + repr(self.dict)
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
