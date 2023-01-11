from PyQt5.QtCore import (
    Qt,
    QAbstractListModel,
    QAbstractItemModel,
    QSortFilterProxyModel,
    pyqtSignal,
    QModelIndex,
    QItemSelectionModel
)

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QLineEdit,
    QListView,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox
)

from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel
)

from lexicon.lexicon_classes import Sign

#from PyQt5.QtGui import ()

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
        # self.dataChanged.emit()


# class CorpusModel(QAbstractItemModel):
#     def __init__(self, signs=None, **kwargs):  # glosses=None, **kwargs):
#         super().__init__(**kwargs)
#         # self.glosses = glosses or []
#         self.signs = signs or []
#
#     def data(self, index, role):
#         print("the index you clicked has data...")
#         print("row: ", index.row())
#         # print("display (gloss): ", index.data(Qt.DisplayRole))
#         # print("entry id: ", index.data(Qt.UserRole+entryidrole))
#         # print("date created: ", index.data(Qt.UserRole+datecreatedrole))
#         # print("date modified: ", index.data(Qt.UserRole+datemodifiedrole))
#         if role == Qt.DisplayRole:
#             # return self.glosses[index.row()]
#             return self.signs[index.row()].signlevel_information.gloss
#         elif role == Qt.UserRole+datecreatedrole:
#             return self.signs[index.row()].signlevel_information.datecreated
#         elif role == Qt.UserRole+datemodifiedrole:
#             return self.signs[index.row()].signlevel_information.datelastmodified
#         elif role == Qt.UserRole+entryidrole:
#             return self.signs[index.row()].signlevel_information.entryid
#
#     def rowCount(self, index):
#         # return len(self.glosses)
#         return len(self.signs)

class CorpusTitleEdit(QLineEdit):
    focus_out = pyqtSignal(str)

    def __init__(self, corpus_title, **kwargs):
        super().__init__(**kwargs)
        self.setFocusPolicy(Qt.StrongFocus)

    def focusOutEvent(self, event):
        # use focusOutEvent as the proxy for finishing editing
        self.focus_out.emit(self.text())
        super().focusInEvent(event)


class CorpusDisplay(QWidget):
    # selected_gloss = pyqtSignal(str)
    selected_sign = pyqtSignal(Sign)
    title_changed = pyqtSignal(str)

    def __init__(self, corpus_title="", **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # self.corpus_title = QLineEdit(corpus_title, parent=self)
        self.corpus_title = CorpusTitleEdit(corpus_title, parent=self)
        self.corpus_title.focus_out.connect(lambda title: self.title_changed.emit(title))
        self.corpus_title.setPlaceholderText('Untitled')
        main_layout.addWidget(self.corpus_title)

        self.corpus_model = CorpusModel(parent=self)
        self.corpus_view = QListView(parent=self)
        self.corpus_sortproxy = CorpusSortProxyModel(parent=self)
        self.corpus_sortproxy.setSourceModel(self.corpus_model)
        self.corpus_model.modelupdated.connect(lambda: self.corpus_sortproxy.sort(0))
        # self.corpus_view.setModel(self.corpus_model)
        self.corpus_view.setModel(self.corpus_sortproxy)
        self.corpus_view.clicked.connect(self.handle_selection)
        main_layout.addWidget(self.corpus_view)

        sort_layout = QHBoxLayout()
        sortlabel = QLabel("Sort by:")
        sort_layout.addWidget(sortlabel)
        self.sortcombo = QComboBox()
        self.sortcombo.addItems(
            ["alpha by gloss (default)", "date created", "date last modified"])
        self.sortcombo.setInsertPolicy(QComboBox.NoInsert)
        self.sortcombo.currentTextChanged.connect(self.sort)
        sort_layout.addWidget(self.sortcombo)
        # sort_layout.addStretch()
        main_layout.addLayout(sort_layout)

    def sort(self, sorttext):
        self.corpus_sortproxy.updatesorttype(sorttext)

    def handle_selection(self, index):
        # gloss = self.corpus_model.glosses[index.row()]
        # themodel = index.model()
        # if hasattr(themodel, 'mapToSource'):
        #     print("selected index is from a proxy model!")
        #     underlyingindex = themodel.mapToSource(index)
        #     underlyingsign = self.corpus_model.signs[underlyingindex.row()]
        #     print("row: ", underlyingindex.row(), " / sign gloss: ", underlyingsign.signlevel_information.gloss)
        # else:
        #     print("selected index is no from from a uproxy model!")

        index = index.model().mapToSource(index)
        sign = self.corpus_model.itemFromIndex(index).sign  #  signs[index.row()]  #.signlevel_information.gloss
        # print("row: ", index.row(), " / sign gloss: ", sign.signlevel_information.gloss)
        # self.selected_gloss.emit(gloss)
        self.selected_sign.emit(sign)

    # def updated_glosses(self, glosses, current_gloss):
    #     self.corpus_model.glosses.clear()
    #     self.corpus_model.glosses.extend(glosses)
    #     self.corpus_model.glosses.sort()
    #     self.corpus_model.layoutChanged.emit()
    #
    #     index = self.corpus_model.glosses.index(current_gloss)
    #
    #     # Ref: https://www.qtcentre.org/threads/32007-SetSelection-QListView-Pyqt
    #     self.corpus_view.selectionModel().setCurrentIndex(self.corpus_view.model().index(index, 0),
    #                                                       QItemSelectionModel.SelectCurrent)

    def updated_signs(self, signs, current_sign=None):
        # self.corpus_model.signs.clear()
        # self.corpus_model.signs.extend(signs)
        # self.corpus_model.clear()
        self.corpus_model.setsigns(signs)
        # self.corpus_model.signs.sort()
        self.corpus_model.layoutChanged.emit()

        index = 0 if current_sign is None else list(signs).index(current_sign)

        # TODO KV crash happens at exec of line below, at addition of second sign
        # Ref: https://www.qtcentre.org/threads/32007-SetSelection-QListView-Pyqt
        sourcemodelindex = self.corpus_view.model().index(index, 0)
        proxymodelindex = self.corpus_view.model().mapFromSource(sourcemodelindex)
        self.corpus_view.selectionModel().setCurrentIndex(proxymodelindex, QItemSelectionModel.SelectCurrent)
        # self.corpus_view.selectionModel().setCurrentIndex(self.corpus_view.model().index(index, 0),
        #                                                   QItemSelectionModel.SelectCurrent)

    # def remove_gloss(self, gloss):
    #     self.corpus_model.glosses.remove(gloss)
    #     self.corpus_model.layoutChanged.emit()
    #     self.corpus_view.clearSelection()

    def remove_sign(self, sign):
        self.corpus_model.signs.remove(sign)
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()

    # def clear(self):
    #     self.corpus_title.setText("")
    #
    #     self.corpus_model.glosses.clear()
    #     self.corpus_model.layoutChanged.emit()
    #     self.corpus_view.clearSelection()

    def clear(self):
        self.corpus_title.setText("")

        # self.corpus_model.signs.clear()
        self.corpus_model.clear()
        self.corpus_model.layoutChanged.emit()
        self.corpus_view.clearSelection()


class CorpusSortProxyModel(QSortFilterProxyModel):

    def __init__(self, parent=None):
        super(CorpusSortProxyModel, self).__init__(parent)
        self.setSortCaseSensitivity(Qt.CaseInsensitive)
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

