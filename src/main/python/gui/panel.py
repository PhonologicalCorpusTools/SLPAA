from datetime import date
from itertools import permutations
from collections import defaultdict
from PyQt5.QtCore import (
    Qt,
    QSize,
    QRectF,
    QPoint,
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QWidget,
    QScrollArea,
    QVBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QGridLayout,
    QHBoxLayout,
    QCheckBox,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
    QButtonGroup,
    QGroupBox,
    QPushButton,
    QColorDialog,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QMenu,
    QAction
)

from PyQt5.QtGui import (
    QPixmap,
    QColor,
    QPen,
    QBrush,
    QPolygonF
)

from gui.hand_configuration import ConfigGlobal, Config
from gui.helper_widget import CollapsibleSection, ToggleSwitch
from gui.decorator import check_date_format, check_empty_gloss
from constant import DEFAULT_LOCATION_POINTS


class LocationPolygon(QGraphicsPolygonItem):
    def __init__(self, polygon, pen_width=5, pen_color='orange', fill_color='#FFD141', fill_alpha=0.5, **kwargs):
        super().__init__(**kwargs)
        self.setPolygon(polygon)

        # set up the pen for the boundary
        pen = QPen(QColor(pen_color))
        pen.setWidth(pen_width)
        self.setPen(pen)

        # set up the brush for fill-in color
        self.brush = QBrush()
        color = QColor(fill_color)
        color.setAlphaF(fill_alpha)
        self.brush.setColor(color)
        self.brush.setStyle(Qt.SolidPattern)

        self.setAcceptHoverEvents(True)

    def hoverEnterEvent(self, event):
        self.setBrush(self.brush)

    def hoverLeaveEvent(self, event):
        self.setBrush(QColor('transparent'))


class SingleLocationViewer(QGraphicsView):
    location_specified = pyqtSignal()

    def __init__(self, location_identifier, locations, viewer_size, pen_width=5, pen_color='orange', **kwargs):
        super().__init__(**kwargs)

        self.location_identifier = location_identifier
        self.viewer_size = viewer_size

        self.pen_width = pen_width
        self.pen_color = pen_color

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(parent=self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

        self.point_D = QGraphicsEllipseItem(0, 0, 50, 50)
        self.text_D = QGraphicsTextItem('D')

        self.point_W = QGraphicsEllipseItem(0, 0, 50, 50)
        self.text_W = QGraphicsTextItem('W')

        self.hand = 'D'

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

        self.locations = {name: {LocationPolygon(QPolygonF([QPoint(x, y) for x, y in points])) for points in polygons} for name, polygons in locations.items()}

        self.add_polygons()

    def add_polygons(self):
        for loc_polys in self.locations.values():
            for loc_poly in loc_polys:
                self._scene.addItem(loc_poly)

    def has_photo(self):
        return not self._empty

    def set_photo(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    def remove_clicked_group(self):
        if self.hand == 'D':
            if self.text_D.scene() and self.point_D.scene():
                self._scene.removeItem(self.text_D)  # removeItem() only removes item from the scene but not delete it
                self._scene.removeItem(self.point_D)

        elif self.hand == 'W':
            if self.text_W.scene() and self.point_W.scene():
                self._scene.removeItem(self.text_W)
                self._scene.removeItem(self.point_W)

    def change_hand(self, hand):
        self.hand = hand

    def get_location_value(self):
        location_value_dict = dict()

        if self.text_D.scene():
            location_value_dict[self.text_D.toPlainText()] = {
                'image': self.location_identifier,
                'point': (self.text_D.x(), self.text_D.y())
            }
        else:
            location_value_dict[self.text_D.toPlainText()] = {
                'image': self.location_identifier,
                'point': None
            }

        if self.text_W.scene():
            location_value_dict[self.text_W.toPlainText()] = {
                'image': self.location_identifier,
                'point': (self.text_W.x(), self.text_W.y())
            }
        else:
            location_value_dict[self.text_W.toPlainText()] = {
                'image': self.location_identifier,
                'point': None
            }

        return location_value_dict

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_photo():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                scenerect = self.transform().mapRect(rect)
                factor = min(self.viewer_size / scenerect.width(),
                             self.viewer_size / scenerect.height())
                # viewrect = self.viewport().rect()
                # factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

    def enterEvent(self, event):
        self.viewport().setCursor(Qt.CrossCursor)
        super().enterEvent(event)

    def wheelEvent(self, event):
        if self.has_photo():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1
            if self._zoom > 0:
                self.scale(factor, factor)
            elif self._zoom == 0:
                self.fitInView()
            else:
                self._zoom = 0

    def mouseDoubleClickEvent(self, event):
        self.location_specified.emit()

        self.remove_clicked_group()

        x = self.mapToScene(event.pos()).toPoint().x()
        y = self.mapToScene(event.pos()).toPoint().y()

        if self.hand == 'D':
            self.text_D.setPos(x, y)
            self.point_D.setPos(x, y)
            self._scene.addItem(self.text_D)
            self._scene.addItem(self.point_D)

        elif self.hand == 'W':
            self.text_W.setPos(x, y)
            self.point_W.setPos(x, y)
            self._scene.addItem(self.text_W)
            self._scene.addItem(self.point_W)

        super().mouseDoubleClickEvent(event)

    def set_value(self, hand, position):
        if hand == 'D':
            if self.text_D.scene() and self.point_D.scene():
                self._scene.removeItem(self.text_D)  # removeItem() only removes item from the scene but not delete it
                self._scene.removeItem(self.point_D)

            self.text_D.setPos(position[0], position[1])
            self.point_D.setPos(position[0], position[1])
            self._scene.addItem(self.text_D)
            self._scene.addItem(self.point_D)

        elif hand == 'W':
            if self.text_W.scene() and self.point_W.scene():
                self._scene.removeItem(self.text_W)
                self._scene.removeItem(self.point_W)

            self.text_W.setPos(position[0], position[1])
            self.point_W.setPos(position[0], position[1])
            self._scene.addItem(self.text_W)
            self._scene.addItem(self.point_W)


class LexicalNote(QPlainTextEdit):
    focus_out = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def focusOutEvent(self, event):
        # use focusOutEvent as the proxy for finishing editing
        self.focus_out.emit()
        super().focusInEvent(event)


class LexicalInformationPanel(QScrollArea):
    finish_edit = pyqtSignal(QWidget)

    def __init__(self, coder, update, **kwargs):
        super().__init__(**kwargs)

        self.coder = coder
        self.update = update

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)
        main_frame.setLayout(main_layout)

        gloss_label = QLabel('Gloss:', parent=self)
        freq_label = QLabel('Frequency:', parent=self)
        coder_label = QLabel('Coder:', parent=self)
        update_label = QLabel('Last updated:', parent=self)
        note_label = QLabel('Notes:', parent=self)

        self.gloss_edit = QLineEdit(parent=self)
        self.gloss_edit.setPlaceholderText('Enter gloss here... (Cannot be empty)')
        self.gloss_edit.editingFinished.connect(lambda: self.finish_edit.emit(self.gloss_edit))

        self.freq_edit = QLineEdit('1.0', parent=self)
        self.freq_edit.editingFinished.connect(lambda: self.finish_edit.emit(self.freq_edit))

        self.coder_edit = QLineEdit(parent=self)
        self.coder_edit.setText(coder)
        self.coder_edit.editingFinished.connect(lambda: self.finish_edit.emit(self.coder_edit))

        self.update_edit = QLineEdit(parent=self)
        self.update_edit.setPlaceholderText('YYYY-MM-DD')
        self.update_edit.setText(str(update))
        self.update_edit.editingFinished.connect(lambda: self.finish_edit.emit(self.update_edit))

        self.note_edit = LexicalNote(parent=self)
        self.note_edit.setPlaceholderText('Enter note here...')
        self.note_edit.focus_out.connect(lambda: self.finish_edit.emit(self.note_edit))

        main_layout.addWidget(gloss_label)
        main_layout.addWidget(self.gloss_edit)
        main_layout.addWidget(freq_label)
        main_layout.addWidget(self.freq_edit)
        main_layout.addWidget(coder_label)
        main_layout.addWidget(self.coder_edit)
        main_layout.addWidget(update_label)
        main_layout.addWidget(self.update_edit)
        main_layout.addWidget(note_label)
        main_layout.addWidget(self.note_edit)

        self.setWidget(main_frame)

    @check_date_format
    def get_date(self):
        year, month, day = self.update_edit.text().split(sep='-')
        return date(int(year), int(month), int(day))

    @check_empty_gloss
    def get_gloss(self):
        return self.gloss_edit.text()

    def clear(self, coder):
        self.gloss_edit.clear()
        self.freq_edit.setText('1.0')
        self.coder_edit.setText(coder)
        self.update_edit.setText(str(date.today()))
        self.note_edit.clear()

    def set_value(self, lexical_info):
        self.gloss_edit.setText(lexical_info.gloss)
        self.freq_edit.setText(str(lexical_info.frequency))
        self.coder_edit.setText(lexical_info.coder)
        self.update_edit.setText(str(lexical_info.update_date))
        if lexical_info.note:
            self.note_edit.setPlainText(lexical_info.note)

    def get_value(self):
        if self.get_date() and self.get_gloss():
            return {
                'gloss': self.get_gloss(),
                'frequency': float(self.freq_edit.text()),
                'coder': self.coder_edit.text(),
                'date': self.get_date(),
                'note': self.note_edit.toPlainText()
            }


class HandTranscriptionPanel(QScrollArea):
    selected_hand = pyqtSignal(int)

    def __init__(self, predefined_ctx, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QGridLayout()
        main_frame.setLayout(main_layout)

        self.global_info = ConfigGlobal(title='Handshape global options', parent=self)
        main_layout.addWidget(self.global_info, 0, 0, 2, 1)

        self.config1 = Config(1, 'Configuration 1', predefined_ctx, parent=self)
        main_layout.addWidget(self.config1, 0, 1, 1, 2)

        self.config2 = Config(2, 'Configuration 2', predefined_ctx, parent=self)
        main_layout.addWidget(self.config2, 1, 1, 1, 2)

        self.setWidget(main_frame)

    def clear(self):
        self.global_info.clear()
        self.config1.clear()
        self.config2.clear()

    def set_value(self, global_handshape_info, hand_transcription):
        self.global_info.set_value(global_handshape_info)
        self.config1.set_value(hand_transcription.config1)
        self.config2.set_value(hand_transcription.config2)

    def change_hand_selection(self, hand):
        if hand == 1:
            self.button1.setChecked(True)
        elif hand == 2:
            self.button2.setChecked(True)
        elif hand == 3:
            self.button3.setChecked(True)
        elif hand == 4:
            self.button4.setChecked(True)

    def insert_radio_button(self, focused_hand):
        self.selected_hand_group = QButtonGroup(parent=self)
        self.button1, self.button2 = self.config1.insert_radio_button()
        self.button3, self.button4 = self.config2.insert_radio_button()

        self.button1.clicked.connect(lambda: self.selected_hand.emit(1))
        self.button2.clicked.connect(lambda: self.selected_hand.emit(2))
        self.button3.clicked.connect(lambda: self.selected_hand.emit(3))
        self.button4.clicked.connect(lambda: self.selected_hand.emit(4))

        if focused_hand == 1:
            self.button1.setChecked(True)
        elif focused_hand == 2:
            self.button2.setChecked(True)
        elif focused_hand == 3:
            self.button3.setChecked(True)
        elif focused_hand == 4:
            self.button4.setChecked(True)

        self.selected_hand_group.addButton(self.button1, 1)
        self.selected_hand_group.addButton(self.button2, 2)
        self.selected_hand_group.addButton(self.button3, 3)
        self.selected_hand_group.addButton(self.button4, 4)

    def remove_radio_button(self):
        self.config1.remove_radio_button()
        self.config2.remove_radio_button()
        self.selected_hand_group.deleteLater()

    def get_hand_transcription(self, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            return self.config1.hand1.get_hand_transcription_list()
        elif hand == 2:
            return self.config1.hand2.get_hand_transcription_list()
        elif hand == 3:
            return self.config2.hand1.get_hand_transcription_list()
        elif hand == 4:
            return self.config2.hand2.get_hand_transcription_list()

    def set_predefined(self, transcription_list, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            self.config1.hand1.set_predefined(transcription_list)
        elif hand == 2:
            self.config1.hand2.set_predefined(transcription_list)
        elif hand == 3:
            self.config2.hand1.set_predefined(transcription_list)
        elif hand == 4:
            self.config2.hand2.set_predefined(transcription_list)


class HandIllustrationPanel(QScrollArea):
    def __init__(self, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_ctx = app_ctx

        main_frame = QFrame(parent=self)

        self.setFrameStyle(QFrame.StyledPanel)
        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        self.hand_illustration = QLabel()
        self.hand_illustration.setFixedSize(QSize(400, 400))
        self.set_neutral_img()
        main_layout.addWidget(self.hand_illustration)

        self.setWidget(main_frame)

    def set_neutral_img(self):
        neutral_img = QPixmap(self.app_ctx.hand_illustrations['neutral'])
        self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        self.hand_illustration.repaint()

    def set_img(self, new_img):
        self.hand_illustration.setPixmap(
            new_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        self.hand_illustration.repaint()


class LocationGroupLayout(QHBoxLayout):
    def __init__(self, name, location_specifications, app_ctx, **kwargs):
        super().__init__(**kwargs)

        self.layout_name = QLineEdit(name)

        self.contact_button = QCheckBox('Contact?')
        self.contact_button.setTristate(True)
        self.location_viewers = dict()

        self.addWidget(self.layout_name)
        self.addWidget(self.contact_button)
        self.add_loc_viewers(location_specifications, app_ctx)

    def add_loc_viewers(self, location_specifications, app_ctx):
        for i, (loc_identifier, loc_param) in enumerate(location_specifications.items()):
            single_loc_viewer = SingleLocationViewer(loc_identifier, loc_param.location_polygons, 250)
            single_loc_viewer.set_photo(QPixmap(app_ctx.default_location_images[loc_param.image_path] if loc_param.default else loc_param.image_path))
            single_loc_viewer.repaint()
            self.location_viewers[loc_identifier] = single_loc_viewer
            self.insertWidget(i, single_loc_viewer)

        for viewer1, viewer2 in permutations(self.location_viewers.values(), r=2):
            viewer1.location_specified.connect(viewer2.remove_clicked_group)

    def change_hand(self, hand):
        for _, viewer in self.location_viewers.items():
            viewer.change_hand(hand)

    def get_location_value(self):
        location_value_dict = dict()
        hand_dict = defaultdict(list)

        for _, viewer in self.location_viewers.items():
            for hand, point_dict in viewer.get_location_value().items():
                hand_dict[hand].append(point_dict)

        location_value_dict.update(hand_dict)

        location_value_dict['contact'] = self.contact_button.checkState()

        return location_value_dict

    def clear(self, location_specifications, app_ctx):
        self.contact_button.setCheckState(Qt.Unchecked)
        self.location_viewers.clear()

        while self.count() >= 2:
            child = self.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.add_loc_viewers(location_specifications, app_ctx)

    def set_value(self, value):

        self.contact_button.setCheckState(value.contact)
        for viewer in self.location_viewers.values():
            viewer.remove_clicked_group()

        for loc in value.D.points:
            if loc['point']:
                viewer = self.location_viewers[loc['image']]
                viewer.set_value('D', loc['point'])

        for loc in value.W.points:
            if loc['point']:
                viewer = self.location_viewers[loc['image']]
                viewer.set_value('W', loc['point'])


class LocationSpecificationLayout(QVBoxLayout):
    def __init__(self, location_specifications, app_ctx, **kwargs):
        super().__init__(**kwargs)

        self.hand_switch = ToggleSwitch()
        self.hand_switch.setChecked(True)
        self.hand_switch.clicked.connect(self.change_hand)
        self.start_location_group_layout = LocationGroupLayout('start', location_specifications, app_ctx)
        self.end_location_group_layout = LocationGroupLayout('end', location_specifications, app_ctx)
        self.location_point_panel = LocationPointPanel('Location points')

        self.addWidget(self.hand_switch)
        #self.addWidget(self.location_point_panel)
        self.addLayout(self.start_location_group_layout)
        self.addLayout(self.end_location_group_layout)

    def change_hand(self):
        hand = 'D' if self.hand_switch.isChecked() else 'W'
        self.start_location_group_layout.change_hand(hand)
        self.end_location_group_layout.change_hand(hand)

    def get_location_value(self):
        location_value_dict = {
            'start': self.start_location_group_layout.get_location_value(),
            'end': self.end_location_group_layout.get_location_value()
        }

        return location_value_dict

    def clear(self, location_specifications, app_ctx):
        self.hand_switch.setChecked(True)
        self.start_location_group_layout.clear(location_specifications, app_ctx)
        self.end_location_group_layout.clear(location_specifications, app_ctx)

    def set_value(self, value):
        self.start_location_group_layout.set_value(value.start)
        self.end_location_group_layout.set_value(value.end)


class LocationPointTable(QTableWidget):
    def __init__(self, default_points, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.default_points = default_points

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)
        self.setDragDropOverwriteMode(False)
        self.setDropIndicatorShown(True)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.horizontalHeader().setStretchLastSection(True)

        # insert default location points
        self.setRowCount(len(default_points))
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(['Point', 'Note'])

        for i, (name, color, note) in enumerate(default_points):
            name_item = QTableWidgetItem(name)
            name_item.setCheckState(Qt.Checked)
            name_item.setForeground(QBrush(QColor(color)))
            name_item.setData(Qt.UserRole, 'name')

            self.setItem(i, 0, name_item)
            self.setItem(i, 1, QTableWidgetItem(note))

        self.create_context_menu()
        self.itemChanged.connect(self.on_item_changed)

    def create_context_menu(self):
        self.context_menu = QMenu(parent=self)
        remove_action = QAction('Remove location point', parent=self, triggered=lambda: self.removeRow(self.currentRow()))
        self.context_menu.addAction(remove_action)

    def contextMenuEvent(self, event):
        self.context_menu.exec_(event.globalPos())

    def add_location_point(self, name, color, note):
        name_item = QTableWidgetItem(name)
        name_item.setCheckState(Qt.Checked)
        name_item.setForeground(QBrush(QColor(color)))
        name_item.setData(Qt.UserRole, 'name')

        row_insertion_position = self.rowCount()
        self.insertRow(row_insertion_position)

        self.setItem(row_insertion_position, 0, name_item)
        self.setItem(row_insertion_position, 1, QTableWidgetItem(note))

    def on_item_changed(self, item):
        if item.data(Qt.UserRole) == 'name':
            print(item.checkState())

    def dropEvent(self, event):
        if not event.isAccepted() and event.source() == self:
            drop_row = self.drop_on(event)

            rows = sorted(set(item.row() for item in self.selectedItems()))
            rows_to_move = [[QTableWidgetItem(self.item(row_index, column_index)) for column_index in range(self.columnCount())]
                            for row_index in rows]

            for row_index in reversed(rows):
                self.removeRow(row_index)
                if row_index < drop_row:
                    drop_row -= 1

            for row_index, data in enumerate(rows_to_move):
                row_index += drop_row
                self.insertRow(row_index)
                for column_index, column_data in enumerate(data):
                    self.setItem(row_index, column_index, column_data)
            event.accept()

            for row_index in range(len(rows_to_move)):
                self.item(drop_row + row_index, 0).setSelected(True)
                self.item(drop_row + row_index, 1).setSelected(True)
        super().dropEvent(event)

    def drop_on(self, event):
        index = self.indexAt(event.pos())
        if not index.isValid():
            return self.rowCount()

        return index.row() + 1 if self.is_below(event.pos(), index) else index.row()

    def is_below(self, pos, index):
        rect = self.visualRect(index)
        margin = 2
        if pos.y() - rect.top() < margin:
            return False
        elif rect.bottom() - pos.y() < margin:
            return True
        # noinspection PyTypeChecker
        return rect.contains(pos, True) and not (int(self.model().flags(index)) & Qt.ItemIsDropEnabled) and pos.y() >= rect.center().y()


class LocationPointPanel(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.point_table = LocationPointTable(DEFAULT_LOCATION_POINTS, parent=self)
        main_layout.addWidget(self.point_table)

        new_point_layout = QHBoxLayout()
        new_point_layout.addWidget(QLabel('New:', parent=self))

        self.new_point_name_edit = QLineEdit(parent=self)
        self.new_point_name_edit.setPlaceholderText('Name')
        new_point_layout.addWidget(self.new_point_name_edit)

        new_point_color_button = QPushButton('color', parent=self)
        new_point_color_button.clicked.connect(self.set_color)
        new_point_layout.addWidget(new_point_color_button)

        self.new_point_note_edit = QLineEdit(parent=self)
        self.new_point_note_edit.setPlaceholderText('Note...')
        new_point_layout.addWidget(self.new_point_note_edit)

        new_point_add_button = QPushButton('Add', parent=self)
        new_point_add_button.clicked.connect(self.add_location_point)
        new_point_layout.addWidget(new_point_add_button)

        main_layout.addLayout(new_point_layout)

    def set_color(self):
        color = QColorDialog(parent=self).getColor()
        if color.isValid():
            self.new_point_name_edit.setStyleSheet('color: {}'.format(color.name()))
            self.new_point_name_edit.repaint()
            self.new_point_name_edit.setProperty('text_color', color.name())

    def add_location_point(self):
        self.point_table.add_location_point(self.new_point_name_edit.text(),
                                            self.new_point_name_edit.property('text_color'),
                                            self.new_point_note_edit.text())


class ParameterPanel(QScrollArea):
    def __init__(self, location_specifications, app_ctx, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        #TODO: need to fingure out how to do this...
        main_frame.setFixedSize(1000, 1000)

        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        self.location_layout = LocationSpecificationLayout(location_specifications, app_ctx)

        self.orientation_layout = QVBoxLayout()
        orientation_label = QLabel('Coming soon...')
        self.orientation_layout.addWidget(orientation_label)
        self.orientation_section = CollapsibleSection(title='Orientation', parent=self)
        self.orientation_section.setContentLayout(self.orientation_layout)

        main_layout.addWidget(QLabel('Location'))
        main_layout.addLayout(self.location_layout)
        main_layout.addWidget(self.orientation_section)

        self.setWidget(main_frame)

    def clear(self, location_specifications, app_ctx):
        self.location_layout.clear(location_specifications, app_ctx)

    def set_value(self, value):
        self.location_layout.set_value(value)
