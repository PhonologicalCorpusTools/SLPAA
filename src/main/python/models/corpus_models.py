from PyQt5.QtCore import (
    Qt,
    QSortFilterProxyModel,
    pyqtSignal
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)


datecreatedrole = 1
datemodifiedrole = 2
entryidrole = 3


class CorpusItem(QStandardItem):

    def __init__(self, sign=None):
        super().__init__()

        self.sign = sign
        self.setEditable(False)
        # self.setText(sign.signlevel_information.gloss)
        self.setCheckable(False)

    def data(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self.sign.signlevel_information.gloss
        elif role == Qt.UserRole+datecreatedrole:
            return self.sign.signlevel_information.datecreated
        elif role == Qt.UserRole+datemodifiedrole:
            return self.sign.signlevel_information.datelastmodified
        elif role == Qt.UserRole+entryidrole:
            return self.sign.signlevel_information.entryid


class CorpusModel(QStandardItemModel):
    modelupdated = pyqtSignal()

    def __init__(self, signs=None, **kwargs):
        super().__init__(**kwargs)
        self.setsigns(signs)

    def setsigns(self, signs):
        signs = signs or []
        self.clear()
        for sign in signs:
            signitem = CorpusItem(sign)
            self.appendRow(signitem)
        self.modelupdated.emit()


class CorpusSortProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(CorpusSortProxyModel, self).__init__(parent)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortRole(Qt.DisplayRole)
        self.sort(0)

    def updatesorttype(self, sortbytext=""):
        if "alpha" in sortbytext:
            self.setSortRole(Qt.DisplayRole)
            self.sort(0)
        elif "created" in sortbytext:
            self.setSortRole(Qt.UserRole+datecreatedrole)
            self.sort(0)
        elif "modified" in sortbytext:
            self.setSortRole(Qt.UserRole+datemodifiedrole)
            self.sort(0)

