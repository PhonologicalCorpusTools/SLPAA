from datetime import datetime

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
lemmarole = 4


class CorpusItem(QStandardItem):

    def __init__(self, sign=None, gloss=None):
        super().__init__()

        self.sign = sign
        self.glosstodisplay = gloss
        self.setEditable(False)
        self.setCheckable(False)

    def data(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if self.glosstodisplay is not None:
                return self.glosstodisplay
            else:
                return self.sign.signlevel_information.gloss[0]
        elif role == Qt.UserRole+lemmarole:
            return self.sign.signlevel_information.lemma
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
            for gloss in sign.signlevel_information.gloss:
                if len(gloss.strip()) > 0:
                    signitem = CorpusItem(sign, gloss)
                    self.appendRow(signitem)
        self.modelupdated.emit()


class CorpusSortProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(CorpusSortProxyModel, self).__init__(parent)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setSortRole(Qt.DisplayRole)
        self.sortorder = Qt.AscendingOrder
        self.sortnow()

    def updatesort(self, sortbytext=None, ascending=None):
        if ascending is not None:
            self.sortorder = Qt.AscendingOrder if ascending else Qt.DescendingOrder
            # otherwise leave sortorder as is
        if sortbytext is not None:
            if "alpha" in sortbytext:
                if "gloss" in sortbytext:
                    self.setSortRole(Qt.DisplayRole)
                elif "lemma" in sortbytext:
                    self.setSortRole(Qt.UserRole+lemmarole)
            elif "created" in sortbytext:
                self.setSortRole(Qt.UserRole+datecreatedrole)
            elif "modified" in sortbytext:
                self.setSortRole(Qt.UserRole+datemodifiedrole)
            # otherwise leave sortRole as is
        self.sortnow()

    def lessThan(self, leftindex, rightindex):
        leftdata = self.sourceModel().data(leftindex, self.sortRole())
        rightdata = self.sourceModel().data(rightindex, self.sortRole())

        # the default implementation of sort() in QSortFilterProxyModel isn't able to compare
        # datetime.datetime objects, so I deal with those explicitly and then pass the rest off
        if isinstance(leftdata, datetime) and isinstance(rightdata, datetime):
            return leftdata < rightdata
        else:
            return super().lessThan(leftindex, rightindex)

    def sortnow(self, column=0, sortorder=None):
        if sortorder is None:
            sortorder = self.sortorder
        self.sort(column, sortorder)

