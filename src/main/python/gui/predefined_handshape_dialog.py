from PyQt5.QtCore import (
    Qt,
    QSize,
    pyqtSlot,
    QPoint,
    QAbstractTableModel,
    pyqtSignal,
    QMimeData
)
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QTableView,
    QAction,
    QAbstractItemView,
    QMenu,
    QFrame,
    QRadioButton
)
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
    QColor,
    QDrag,
    QImage
)
from constant import PREDEFINED_MAP


class PredefinedTableModel(QAbstractTableModel):
    def __init__(self, predefined_images, **kwargs):
        super().__init__(**kwargs)
        self.predefined_images = predefined_images
        self.col_labels = ['Handshape',
                           'Bent',
                           'Clawed', 'Closed', 'Combined', 'Contracted', 'Covered', 'Crooked', 'Curved',
                           'Extended',
                           'Flat',
                           'Index',
                           'Modified',
                           'Offset', 'Open',
                           'Slanted', 'Spread']

        self.data_cached = [
            ['A',
             '',  # bent
             '', '', '', '', '', '', '',  # clawed, closed, combined, contracted, covered, crooked, curved
             'extended-A',  # extended
             '',  # flat
             '',  # index
             'modified-A',  # modified
             '', 'open-A',  # offset, open
             '', ''],  # slanted, spread
            ['',
             '',  # bent
             '', '', '', '', '', '', '',  # clawed, closed, combined, contracted, covered, crooked, curved
             '',  # extended
             '',  # flat
             'closed-A-index',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['B1',
             'bent-B',  # bent
             'clawed-extended-B', '', '', 'contracted-B', '', 'crooked-extended-B', '',  # 7 slots
             'extended-B',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             'slanted-extended-B', ''],  # slanted, spread
            ['B2',
             'bent-extended-B',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['C',
             '',  # bent
             'clawed-C', '', '', 'contracted-C', '', 'crooked-C', '',  # 7 slots
             'extended-C',  # extended
             'flat-C',  # flat
             'C-index',  # index
             '',  # modified
             '', '',  # offset, open
             '', 'spread-C'],  # slanted, spread
            ['',
             '',  # bent
             'clawed-spread-C', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             'double-C-index',  # index
             '',  # modified
             '', '',  # offset, open
             '', 'spread-extended-C'],  # slanted, spread
            ['D',
             'partially-bent-D',  # bent
             '', 'closed-bent-D', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             'modified-D',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             'closed-bent-D',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['E',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', 'open-E',  # offset, open
             '', ''],  # slanted, spread
            ['F',
             '',  # bent
             'clawed-F', '', '', '', 'covered-F', '', '',  # 7 slots
             '',  # extended
             'flat-F',  # flat
             '',  # index
             'adducted-F',  # modified
             'offset-F', 'open-F',  # offset, open
             'slanted-F', ''],  # slanted, spread
            ['',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             'flat-open-F',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             'flat-clawed-F',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['G',
             '',  # bent
             'closed-G', 'closed-modified-G', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             'modified-G',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             '',  # bent
             '', 'closed-double-modified-G', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             'double-modified-G',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['I',
             'bent-I',  # bent
             'clawed-I', '', 'combined-I+1', '', '', '', '',  # 7 slots
             '',  # extended
             'flat-combined-I+1',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             'bent-combined-I+1',  # bent
             '', '', 'combined-ILY', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             '',  # bent
             '', '', 'combined-I+A', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['K',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             'extended-K',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['L',
             'bent-L',  # bent
             'clawed-L', '', '', 'contracted-L', '', 'crooked-L', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             'bent-thumb-L',  # bent
             '', '', '', 'double-contracted-L', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['M',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             'flat-M',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['N',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['O',
             '',  # bent
             '', '', '', '', 'covered-O', '', '',  # 7 slots
             '',  # extended
             'flat-O',  # flat
             'O-index',  # index
             'modified-O',  # modified
             'offset-O', 'open-spread-O',  # offset, open
             '', ''],  # slanted, spread
            ['',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', 'open-O-index',  # offset, open
             '', ''],  # slanted, spread
            ['R',
             'bent-R',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             'extended-R',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['S',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['T',
             '',  # bent
             '', '', '', '', 'covered-T', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['U',
             'bent-U',  # bent
             'clawed-U', '', 'combined-U&Y', 'contracted-U', '', 'crooked-U', '',  # 7 slots
             'extended-U',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             'bent-extended-U',  # bent
             '', '', '', 'contracted-U-index', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['V',
             'bent-V',  # bent
             'clawed-V', 'closed-V', '', '', '', 'crooked-V', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             'slanted-V', ''],  # slanted, spread
            ['',
             'bent-extended-V',  # bent
             'clawed-extended-V', '', '', '', '', 'crooked-extended-V', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['W',
             '',  # bent
             'clawed-W', 'closed-W', '', '', '', 'crooked-W', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['X',
             '',  # bent
             'closed-X', '', '', '', '', '', '',  # 7 slots
             'extended-X',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['Y',
             '',  # bent
             '', '', 'combined-Y&middle', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             'modified-Y',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread

            ['1',
             'bent-1',  # bent
             'clawed-1', '', '', '', '', 'crooked-1', '',  # clawed, closed, combined, contracted, covered, crooked, curved (7 slots)
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['',
             'bent-offset-1',  # bent
             '', '', '', '', '', '', '', # clawed, closed, combined, contracted, covered, crooked, curved (7 slots)
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['3',
             '',  # bent
             'clawed-3', '', '', 'contracted-3', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['4',
             'bent-4',  # bent
             'clawed-4', '', '', '', '', 'crooked-4', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             'slanted-4', ''],  # slanted, spread
            ['5',
             'bent-5',  # bent
             'clawed-5', '', '', 'contracted-5', '', 'crooked-5', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             'modified-5',  # modified
             '', '',  # offset, open
             'slanted-5', ''],  # slanted, spread
            ['',
             'bent-midfinger-5',  # bent
             '', '', '', 'relaxed-contracted-5', '', 'crooked-slanted-5', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['6',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['8',
             '',  # bent
             '', '', '', '', 'covered-8', '', '',  # 7 slots
             'extended-8',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', 'open-8',  # offset, open
             '', ''],  # slanted, spread

            ['middle-finger',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', ''],  # slanted, spread
            ['base',
             '',  # bent
             '', '', '', '', '', '', '',  # 7 slots
             '',  # extended
             '',  # flat
             '',  # index
             '',  # modified
             '', '',  # offset, open
             '', '']  # slanted, spread
        ]

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.data_cached)

    def columnCount(self, parent=None, *args, **kwargs):
        return len(self.col_labels)

    def get_value(self, index):
        return self.data_cached[index.row()][index.column()]

    def data(self, index, role=None):
        if not index.isValid():
            return None

        value = self.get_value(index)
        if role == Qt.DisplayRole:# or role == Qt.EditRole:
            return PREDEFINED_MAP[value].name if value in PREDEFINED_MAP.keys() else None
        elif role == Qt.AccessibleTextRole:
            return value if value else None
        #elif role == Qt.TextAlignmentRole:
        #    return Qt.AlignCenter
        elif role == Qt.DecorationRole:
            return QIcon(self.predefined_images[value]) if value in PREDEFINED_MAP else None
        elif role == Qt.BackgroundRole:
            if value in {'1', '5', 'A', 'B1', 'B2', 'C', 'O', 'S'}:
                return QColor('#90ee90')
        return None

    def setData(self, index, value, role=None):
        if index.isValid() and role == Qt.EditRole:
            self.data_cached[index.row()][index.column()] = value
            self.dataChanged.emit(index, index)
            return True
        else:
            return False

    def headerData(self, section, orientation, role=None):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            header = self.col_labels[section]
            return header
        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return str(section + 1)

        return None


class FrozenTableView(QTableView):
    def __init__(self, predefined_images, drag_enabled=False, **kwargs):
        super().__init__(**kwargs)
        self.predefined_images = predefined_images
        self.setDragEnabled(drag_enabled)
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.SingleSelection)

    def mouseMoveEvent(self, e):
        if self.dragEnabled():
            self.startDrag(e)
        else:
            super().mouseMoveEvent(e)

    def dragMoveEvent(self, event):
        #TODO: need to look into this
        if self.dragEnabled():
            if event.mimeData().hasText() and event.mimeData().hasImage():
                label = event.mimeData().text()
                if label in self.getSetOfItemLabels():
                    event.ignore()
                else:
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
            else:
                event.ignore()
        else:
            super().dragMoveEvent(event)

    def startDrag(self, event):
        if self.dragEnabled():
            selectedshape = self.model().get_value(self.selectedIndexes()[0])
            symbol = str(selectedshape)
            icon = QPixmap(self.predefined_images[symbol])
            icon.scaled(100, 100)

            mime = QMimeData()
            mime.setImageData(QImage(self.predefined_images[symbol]))
            mime.setText(symbol)

            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(icon)
            drag.setHotSpot(QPoint(icon.width() / 2, icon.height() / 2))
            drag.exec_(Qt.CopyAction)
        else:
            super().startDrag(event)


class PredefinedHandshapeView(QTableView):
    def __init__(self, predefined_images, drag_enabled=False, **kwargs):
        super().__init__(**kwargs)

        self.predefined_images = predefined_images
        self.setDragDropMode(QAbstractItemView.DragOnly)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDragEnabled(drag_enabled)

        # set the table model
        predefined_model = PredefinedTableModel(predefined_images, parent=self)
        self.setModel(predefined_model)

        # the following view is only for the first froze column
        self.frozen_table_view = FrozenTableView(predefined_images, drag_enabled=drag_enabled, parent=self)
        self.frozen_table_view.setModel(predefined_model)

        self.frozen_table_view.setIconSize(QSize(50, 50))
        self.frozen_table_view.verticalHeader().hide()
        self.frozen_table_view.setFocusPolicy(Qt.NoFocus)

        # so there are no scroll bars in the frozen panel
        self.frozen_table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozen_table_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.frozen_table_view.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        # self.frozenTableView.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        #self.frozenTableView.setStyleSheet('''border: none; background-color: #CCC''')
        #self.frozen_table_view.setSelectionModel(QAbstractItemView.selectionModel(self))

        self.viewport().stackUnder(self.frozen_table_view)

        #self.setEditTriggers(QAbstractItemView.SelectedClicked)

        # style-related stuff
        self.setIconSize(QSize(50, 50))
        self.setShowGrid(False)
        self.setStyleSheet('font: 10pt')
        self.setAlternatingRowColors(True)

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)

        horizontal_header = self.horizontalHeader()
        horizontal_header.setDefaultAlignment(Qt.AlignCenter)
        horizontal_header.setStretchLastSection(True)

        vertical_header = self.verticalHeader()
        vertical_header.setDefaultSectionSize(25)
        vertical_header.setDefaultAlignment(Qt.AlignCenter)
        vertical_header.setVisible(True)

        num_col = predefined_model.columnCount(self)
        for col in range(num_col):
            if col == 0:
                self.horizontalHeader().resizeSection(col, 100)
                # self.horizontalHeader().setSectionResizeMode(col, QHeaderView.Fixed)
                self.frozen_table_view.setColumnWidth(col, self.columnWidth(col))
            else:
                self.horizontalHeader().resizeSection(col, 125)
                self.frozen_table_view.setColumnHidden(col, True)

        # connect the headers and scrollbars of both tableviews together
        self.horizontalHeader().sectionResized.connect(self.update_section_width)
        self.verticalHeader().sectionResized.connect(self.update_section_height)
        self.frozen_table_view.verticalScrollBar().valueChanged.connect(self.verticalScrollBar().setValue)
        self.verticalScrollBar().valueChanged.connect(self.frozen_table_view.verticalScrollBar().setValue)

        self.resizeRowsToContents()
        self.update_frozen_table_geometry()

        #self.makeMenu()
        #self.setContextMenuPolicy(Qt.CustomContextMenu)
        #self.customContextMenuRequested.connect(self.showContextMenu)

    def makeMenu(self):
        self.popMenu = QMenu(self)
        self.editHandshapeAct = QAction('Edit handshape', self, triggered=self.editHandshape)
        self.popMenu.addAction(self.editHandshapeAct)

    def editHandshape(self):
        pass

    def showContextMenu(self, point):
        # TODO: maybe need to initiate this...
        self.indexToBeEdited = self.indexAt(point)
        self.popMenu.exec_(self.mapToGlobal(point))

    def update_section_width(self, logical_index, old_size, new_size):
        if logical_index == 0:  # we're only concerned about the first column
            self.frozen_table_view.setColumnWidth(logical_index, new_size)
            self.update_frozen_table_geometry()

    def update_section_height(self, logical_index, old_size, new_size):
        self.frozen_table_view.setRowHeight(logical_index, new_size)

    def resizeEvent(self, event):
        self.update_frozen_table_geometry()
        super().resizeEvent(event)

    def scrollTo(self, index, hint=None):
        if index.column() >= 1:
            super().scrollTo(index, hint)

    def update_frozen_table_geometry(self):
        if self.verticalHeader().isVisible():
            self.frozen_table_view.setGeometry(self.verticalHeader().width() + self.frameWidth(),
                                             self.frameWidth(),
                                             self.columnWidth(0),
                                             self.viewport().height() + self.horizontalHeader().height())
        else:
            self.frozen_table_view.setGeometry(self.frameWidth(),
                                             self.frameWidth(),
                                             self.columnWidth(0),
                                             self.viewport().height() + self.horizontalHeader().height())

    # Ref: https://stackoverflow.com/questions/37496320/pyqt-dragging-item-from-list-view-and-dropping-to-table-view-the-drop-index-is
    def mouseMoveEvent(self, e):
        if self.dragEnabled():
            self.startDrag(e)
        else:
            super().mouseMoveEvent(e)

    def dragMoveEvent(self, event):
        #TODO: need to look into this
        if self.dragEnabled():
            if event.mimeData().hasText() and event.mimeData().hasImage():
                label = event.mimeData().text()
                if label in self.getSetOfItemLabels():
                    event.ignore()
                else:
                    event.setDropAction(Qt.CopyAction)
                    event.accept()
            else:
                event.ignore()
        else:
            super().dragMoveEvent(event)

    def startDrag(self, event):
        if self.dragEnabled():
            selectedshape = self.model().get_value(self.selectedIndexes()[0])
            symbol = str(selectedshape)
            icon = QPixmap(self.predefined_images[symbol])
            icon.scaled(100, 100)

            mime = QMimeData()
            mime.setImageData(QImage(self.predefined_images[symbol]))
            mime.setText(symbol)

            drag = QDrag(self)
            drag.setMimeData(mime)
            drag.setPixmap(icon)
            drag.setHotSpot(QPoint(icon.width() / 2, icon.height() / 2))
            drag.exec_(Qt.CopyAction)
        else:
            super().startDrag(event)

    '''
    def moveCursor(self, cursorAction, modifiers):
        current = QTableView.moveCursor(self, cursorAction, modifiers)
        x = self.visualRect(current).topLeft().x()
        frozen_width = self.frozenTableView.columnWidth(0) + self.frozenTableView.columnWidth(1)
        if cursorAction == self.MoveLeft and current.column() > 1 and x < frozen_width:
            new_value = self.horizontalScrollBar().value() + x - frozen_width
            self.horizontalScrollBar().setValue(new_value)
        return current
    '''


class PredefinedHandshapeDialog(QDialog):
    transcription = pyqtSignal(tuple)
    selected_hand = pyqtSignal(int)

    def __init__(self, predefined_images, focused_hand, **kwargs):
        super().__init__(**kwargs)
        self.resize(750, 750)
        self.setWindowTitle('Predefined Handshapes')
        self.setWindowFlags(Qt.Window | Qt.WindowTitleHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)

        # create table view
        self.table_view = PredefinedHandshapeView(predefined_images, parent=self)
        self.table_view.clicked.connect(self.emit_transcription)
        self.table_view.frozen_table_view.clicked.connect(self.emit_transcription)

        # layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table_view)
        self.setLayout(main_layout)

        hand_selection_widget = QFrame(parent=self)
        hand_selection_layout = QHBoxLayout()
        hand_selection_widget.setLayout(hand_selection_layout)

        self.c1h1_radio = QRadioButton('Config1 Hand1', parent=hand_selection_widget)
        self.c1h1_radio.clicked.connect(lambda : self.selected_hand.emit(1))
        self.c1h2_radio = QRadioButton('Config1 Hand2', parent=hand_selection_widget)
        self.c1h2_radio.clicked.connect(lambda: self.selected_hand.emit(2))
        self.c2h1_radio = QRadioButton('Config2 Hand1', parent=hand_selection_widget)
        self.c2h1_radio.clicked.connect(lambda: self.selected_hand.emit(3))
        self.c2h2_radio = QRadioButton('Config2 Hand2', parent=hand_selection_widget)
        self.c2h2_radio.clicked.connect(lambda: self.selected_hand.emit(4))

        if focused_hand == 1:
            self.c1h1_radio.setChecked(True)
        elif focused_hand == 2:
            self.c1h2_radio.setChecked(True)
        elif focused_hand == 3:
            self.c2h1_radio.setChecked(True)
        elif focused_hand == 4:
            self.c2h2_radio.setChecked(True)

        hand_selection_layout.addWidget(self.c1h1_radio)
        hand_selection_layout.addWidget(self.c1h2_radio)
        hand_selection_layout.addWidget(self.c2h1_radio)
        hand_selection_layout.addWidget(self.c2h2_radio)

        self.layout().setMenuBar(hand_selection_widget)

    def emit_transcription(self, clicked):
        predefined = clicked.data(role=Qt.AccessibleTextRole)
        if predefined in PREDEFINED_MAP:
            self.transcription.emit(PREDEFINED_MAP[predefined].canonical)

    @pyqtSlot(int)
    def change_hand_selection(self, hand):
        if hand == 1:
            self.c1h1_radio.setChecked(True)
        elif hand == 2:
            self.c1h2_radio.setChecked(True)
        elif hand == 3:
            self.c2h1_radio.setChecked(True)
        elif hand == 4:
            self.c2h2_radio.setChecked(True)
