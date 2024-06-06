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

    def __init__(self, sign=None, identifyingtext=None, isentryid=False, settings=None):
        super().__init__()

        self.sign = sign
        self.texttodisplay = identifyingtext
        self.isentryid = isentryid
        self.settings = settings
        self.setEditable(False)
        self.setCheckable(False)

    def data(self, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if self.texttodisplay is not None:
                return self.texttodisplay
            else:
                return ""
        elif role == Qt.UserRole+datecreatedrole:
            return self.sign.signlevel_information.datecreated
        elif role == Qt.UserRole+datemodifiedrole:
            return self.sign.signlevel_information.datelastmodified


class CorpusModel(QStandardItemModel):
    modelupdated = pyqtSignal()

    def __init__(self, signs=None, settings=None, **kwargs):
        super().__init__(**kwargs)
        self.signs = signs
        self.setsigns(signs)
        self.settings = settings
        self.col_labels = ["Entry ID", "Gloss", "Lemma", "ID-Gloss"]

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            header = self.col_labels[section]
            return header
        else:
            return super().headerData(section, orientation, role)

    def setsigns(self, signs):
        self.signs = signs or []
        self.clear()
        for sign in self.signs:
            glosses = sign.signlevel_information.gloss
            if len(glosses) == 0:
                glosses.append("")
            for gloss in glosses:
                entryiditem = CorpusItem(sign=sign, identifyingtext=str(sign.signlevel_information.entryid.display_string()), isentryid=True, settings=self.settings)
                glossitem = CorpusItem(sign, gloss)
                lemmaitem = CorpusItem(sign, sign.signlevel_information.lemma)
                idglossitem = CorpusItem(sign, sign.signlevel_information.idgloss)
                self.appendRow([entryiditem, glossitem, lemmaitem, idglossitem])
        self.modelupdated.emit()


class CorpusSortProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(CorpusSortProxyModel, self).__init__(parent)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterKeyColumn(-1)  # matches text from any column
        self.setSortRole(Qt.DisplayRole)
        self.sortorder = Qt.AscendingOrder
        self.sortcolumn = 1  # gloss
        self.sortnow()

    def getrownumsmatchingsign(self, sign):
        matchingrownums = []
        for rownum in range(self.rowCount()):
            if self.sourceModel().itemFromIndex(self.mapToSource(self.index(rownum, 0))).sign == sign:
                matchingrownums.append(rownum)
        return matchingrownums

    def updatesort(self, sortbytext=None, ascending=None):
        if ascending is not None:
            self.sortorder = Qt.AscendingOrder if ascending else Qt.DescendingOrder
            # otherwise leave sortorder as is
        if sortbytext is not None:
            if "entry ID" in sortbytext:
                self.setSortRole(Qt.DisplayRole)
                self.sortcolumn = 0  # entryID
            elif "alpha by gloss" in sortbytext:
                self.setSortRole(Qt.DisplayRole)
                self.sortcolumn = 1
            elif "alpha by lemma" in sortbytext:
                self.setSortRole(Qt.DisplayRole)
                self.sortcolumn = 2
                # self.setSortRole(Qt.UserRole+lemmarole)
            elif "alpha by ID-gloss" in sortbytext:
                self.setSortRole(Qt.DisplayRole)
                self.sortcolumn = 3
            elif "date created" in sortbytext:
                self.setSortRole(Qt.UserRole+datecreatedrole)
                # column doesn't matter
            elif "date last modified" in sortbytext:
                self.setSortRole(Qt.UserRole+datemodifiedrole)
                # column doesn't matter
            # otherwise leave sortRole & sortcolumn as they are
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

    def sortnow(self, sortorder=None):
        if sortorder is None:
            sortorder = self.sortorder
        self.sort(self.sortcolumn, sortorder)

