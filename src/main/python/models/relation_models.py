from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)

from PyQt5.QtCore import (
    Qt
)

from constant import ARTICULATOR_ABBREVS, ModuleTypes


class ModuleLinkingListModel(QStandardItemModel):

    def __init__(self, modules=None, modulenumsdict=None, **kwargs):
        super().__init__(**kwargs)
        self.setmoduleslist(modules, modulenumsdict)

    def setmoduleslist(self, modules=None, modulenumsdict=None):
        modules = modules or []
        self.clear()
        for idx, module in enumerate(modules):
            moduleitem = ModuleLinkingListItem(module, modulenumsdict[module.uniqueid])
            self.appendRow(moduleitem)
        # self.modelupdated.emit()
        # self.dataChanged.emit()

    def finditemswithuniqueIDs(self, uniqueIDs, parentnode=None):
        founditems = []

        if parentnode is None:
            parentnode = self.invisibleRootItem()

        numchildren = parentnode.rowCount()
        for i in range(numchildren):
            child = parentnode.child(i, 0)
            uid = child.module.uniqueid
            if uid in uniqueIDs:
                founditems.append(child)

        return founditems


class ModuleLinkingListItem(QStandardItem):

    def __init__(self, module, modulenumber):
        super().__init__()

        self.module = module
        self.modnum = modulenumber
        self.moduletype = module.moduletype
        self.setEditable(False)
        self.setCheckable(False)

    def data(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            # TODO KV can this abbreviated module name come from elsewhere?
            #  sign summary panel uses the same kind of abbreviation, eg
            articulator, articulators_dict = self.module.articulators
            # hands_dict = self.module.hands
            arts_list = [ARTICULATOR_ABBREVS[articulator] + str(a) for a in articulators_dict.keys() if articulators_dict[a]]
            arts_str = "+".join(arts_list)
            moduleabbrev = ModuleTypes.abbreviations[self.moduletype]
            return moduleabbrev

            # return moduleabbrev + str(self.modnum) + "(" + arts_str + "): " + self.module.getabbreviation()
        # TODO KV any other roles to worry about?
