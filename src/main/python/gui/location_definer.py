import os
import json
from PyQt5.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFrame,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QListView,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QSlider
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRectF,
    QAbstractListModel,
    pyqtSignal
)

from .helper_widget import EditableTabBar
from constant import LocationParameter, Locations
from constant import SAMPLE_LOCATIONS
from copy import copy, deepcopy
from pprint import pprint


#reference: https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
class LocationPolygon(QGraphicsPolygonItem):
    def __init__(self, polygon, pen_width=5, pen_color='orange', fill_color='#FFD141', fill_alpha=0.5):
        super().__init__()
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

    def highlight(self):
        self.setBrush(self.brush)

    def unhighlight(self):
        self.setBrush(QColor('transparent'))

    def hoverEnterEvent(self, event):
        self.setBrush(self.brush)

    def hoverLeaveEvent(self, event):
        self.setBrush(QColor('transparent'))


class LocationViewer(QGraphicsView):
    def __init__(self, locations, viewer_size, parent=None, pen_width=5, pen_color='orange'):
        """
        :param locations: a dictionary {'name_of_location': [[polygon_points], [polygon_points]]}
        :param parent:
        """
        super().__init__(parent=parent)

        self.viewer_size = viewer_size

        self.pen_width = pen_width
        self.pen_color = pen_color

        #self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(parent=self)
        self._photo = QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

        # self.locations is default locations
        self.locations = {name: {LocationPolygon(QPolygonF([QPoint(x, y) for x, y in points])) for points in polygons} for name, polygons in locations.items()}

        self.is_defining = False
        self.defining_locations = [[]]
        self.defining_polygons = {}

        self.add_polygons()

    def add_polygons(self):
        for loc_polys in self.locations.values():
            for loc_poly in loc_polys:
                self._scene.addItem(loc_poly)

    def remove_all_polygons(self):
        for poly in self.defining_polygons:
            if poly.scene():
                self._scene.removeItem(poly)
                del poly
        for loc_polys in self.locations.values():
            for loc_poly in loc_polys:
                if loc_poly.scene():
                    self._scene.removeItem(loc_poly)
                    del loc_poly

    def remove_polygons(self, polygons):
        for poly in polygons:
            if poly.scene():
                self._scene.removeItem(poly)
                del poly

    def has_photo(self):
        return not self._empty

    def fitInView(self, scale=True):
        rect = QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            self.setSceneRect(rect)
            if self.has_photo():
                unity = self.transform().mapRect(QRectF(0, 0, 1, 1))
                self.scale(1 / unity.width(), 1 / unity.height())
                scenerect = self.transform().mapRect(rect)
                factor = min(self.viewer_size / scenerect.width(), self.viewer_size / scenerect.height())
                self.factor = factor
                # viewrect = self.viewport().rect()
                # factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            #self._zoom = 0

    def set_photo(self, pixmap=None):
        #self._zoom = 0
        if pixmap and not pixmap.isNull():
            self._empty = False
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
        else:
            self._empty = True
            self.setDragMode(QGraphicsView.NoDrag)
            self._photo.setPixmap(QPixmap())
        self.fitInView()

    # def wheelEvent(self, event):
    #     if self.has_photo():
    #         if event.angleDelta().y() > 0:
    #             factor = 1.25
    #             self._zoom += 1
    #         else:
    #             factor = 0.8
    #             self._zoom -= 1
    #
    #         if self._zoom > 0:
    #             self.scale(factor, factor)
    #         elif self._zoom == 0:
    #             self.fitInView()
    #         else:
    #             self._zoom = 0

    def toggleDragMode(self):
        if self.dragMode() == QGraphicsView.ScrollHandDrag:
            self.setDragMode(QGraphicsView.NoDrag)
        elif not self._photo.pixmap().isNull():
            self.setDragMode(QGraphicsView.ScrollHandDrag)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.is_defining:
            self.viewport().setCursor(Qt.CrossCursor)
        else:
            self.viewport().setCursor(Qt.OpenHandCursor)

    def enterEvent(self, event):
        super().enterEvent(event)
        if self.is_defining:
            self.viewport().setCursor(Qt.CrossCursor)
        else:
            self.viewport().setCursor(Qt.OpenHandCursor)

    def mouseDoubleClickEvent(self, event):
        if self.is_defining:
            self.defining_locations[-1].append(self.mapToScene(event.pos()).toPoint())
            self.remove_polygons(self.defining_polygons)
            pen = QPen(QColor(self.pen_color))
            pen.setWidth(self.pen_width)

            self.defining_polygons = {QGraphicsPolygonItem(QPolygonF(poly)) for poly in self.defining_locations}
            for poly in self.defining_polygons:
                poly.setPen(pen)
                self._scene.addItem(poly)

    def get_photo(self):
        return self._photo.pixmap()


class LocationListModel(QAbstractListModel):
    def __init__(self, locations=None, parent=None):
        super().__init__(parent=parent)
        self.locations = locations or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.locations[index.row()]

    def rowCount(self, index):
        return len(self.locations)


class LocationDefinitionPanel(QFrame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        main_layout = QGridLayout()
        self.setLayout(main_layout)

        self.location_name = QLineEdit(parent=self)
        self.location_name.setPlaceholderText('New location name...')

        self.set_image_button = QPushButton('Change image', parent=self)
        self.define_button = QPushButton('Draw', parent=self)
        self.add_button = QPushButton('+', parent=self)
        self.save_button = QPushButton('Add polygon', parent=self)
        self.delete_button = QPushButton('Delete polygon', parent=self)

        main_layout.addWidget(self.set_image_button, 0, 0, 1, 3)
        main_layout.addWidget(self.location_name, 1, 0, 1, 1)
        main_layout.addWidget(self.define_button, 1, 1, 1, 1)
        main_layout.addWidget(self.add_button, 1, 2, 1, 1)
        main_layout.addWidget(self.save_button, 2, 0, 1, 3)
        main_layout.addWidget(self.delete_button, 3, 0, 1, 3)

    def change_label(self, label):
        self.define_button.setText(label)


class LocationDefinerPage(QWidget):
    def __init__(self, app_settings, app_ctx, image_basename=None, image_path=None, locations=None, default=True, viewer_size=500, **kwargs):
        super().__init__(**kwargs)

        self.app_settings = app_settings
        if locations is None:
            locations = dict()
        self.is_defining = False
        self.locations = locations
        self.image_base = image_basename
        self.image_path = image_path
        self.default = default

        main_layout = QHBoxLayout()

        self.location_model = LocationListModel(sorted(list(self.locations.keys())), parent=self)
        self.location_list_view = QListView(parent=self)
        self.location_list_view.setModel(self.location_model)
        self.location_list_view.clicked.connect(self.location_clicked)

        self.location_definition_panel = LocationDefinitionPanel(parent=self)
        self.location_definition_panel.define_button.clicked.connect(self.start_polygon)
        self.location_definition_panel.add_button.clicked.connect(self.add_polygon)
        self.location_definition_panel.save_button.clicked.connect(self.save_new_location)
        self.location_definition_panel.delete_button.clicked.connect(self.delete_location)
        self.location_definition_panel.set_image_button.clicked.connect(self.set_image)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.location_list_view)
        left_layout.addWidget(self.location_definition_panel)
        main_layout.addLayout(left_layout)

        self.location_viewer = LocationViewer(self.locations, viewer_size, parent=self)
        self.location_viewer.setFixedSize(viewer_size, viewer_size)
        if image_path:
            self.location_viewer.set_photo(QPixmap(app_ctx.default_location_images[image_path] if default else image_path))

        main_layout.addWidget(self.location_viewer)

        zoom_slider = QSlider(Qt.Vertical, parent=self)
        zoom_slider.setMinimum(1)
        zoom_slider.setMaximum(10)
        zoom_slider.setValue(0)
        zoom_slider.valueChanged.connect(self.zoom)

        main_layout.addWidget(zoom_slider)

        self.setLayout(main_layout)

    def zoom(self, scale):
        if self.location_viewer.has_photo():
            trans_matrix = self.location_viewer.transform()
            trans_matrix.reset()
            trans_matrix = trans_matrix.scale(scale * self.location_viewer.factor, scale * self.location_viewer.factor)
            self.location_viewer.setTransform(trans_matrix)

    def set_image(self):
        file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Open Image'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('Image Files (*.png *.jpg *.bmp)'))
        _, basename = os.path.split(file_name)

        self.image_base = basename

        self.default = False
        self.location_viewer.set_photo(QPixmap(file_name))

        self.location_model.locations = dict()
        self.location_model.layoutChanged.emit()
        self.location_list_view.clearSelection()
        self.location_list_view.repaint()

        # remove the item from self.locations
        self.locations = dict()
        self.location_viewer.remove_all_polygons()
        self.location_viewer.locations = dict()

    def add_polygon(self):
        self.location_viewer.defining_locations.append([])

    def delete_location(self):
        indices = self.location_list_view.selectedIndexes()
        if indices:
            index = indices[0]
            deleted_location = self.location_model.locations[index.row()]
            del self.location_model.locations[index.row()]
            self.location_model.layoutChanged.emit()
            self.location_list_view.clearSelection()
            self.location_list_view.repaint()

            # remove the item from self.locations
            del self.locations[deleted_location]
            self.location_viewer.remove_all_polygons()
            del self.location_viewer.locations[deleted_location]
            self.location_viewer.add_polygons()

    def save_new_location(self):
        # need to change self.locations, LocationListModel.locations, LocationViewer.location
        new_location_name = self.location_definition_panel.location_name.text()
        self.locations[new_location_name] = [[(point.x(), point.y()) for point in poly] for poly in
                                             self.location_viewer.defining_locations]

        self.location_definition_panel.location_name.setText('')
        self.location_definition_panel.location_name.repaint()

        # If it's a duplicated name, need to remove the old location first
        if new_location_name in self.location_viewer.locations:
            self.location_viewer.remove_polygons(self.location_viewer.locations[new_location_name])
        self.location_viewer.locations[new_location_name] = {LocationPolygon(QPolygonF(poly)) for poly in
                                                             self.location_viewer.defining_locations}
        self.location_viewer.defining_locations = [[]]
        self.location_viewer.remove_all_polygons()
        self.location_viewer.add_polygons()

        self.location_model.locations = sorted(list(self.locations.keys()))
        self.location_model.layoutChanged.emit()

    def start_polygon(self):
        if self.is_defining:
            self.is_defining = False
            self.location_definition_panel.change_label('Draw')
            self.location_viewer.is_defining = False
            self.location_definition_panel.save_button.setEnabled(True)
            self.location_definition_panel.delete_button.setEnabled(True)
            self.location_definition_panel.repaint()
        else:
            self.is_defining = True
            self.location_definition_panel.change_label('Done')
            self.location_definition_panel.save_button.setEnabled(False)
            self.location_definition_panel.delete_button.setEnabled(False)
            self.location_definition_panel.repaint()

            self.location_viewer.is_defining = True
            self.location_viewer.defining_locations = [[]]
            self.location_viewer.remove_polygons(self.location_viewer.defining_polygons)

    def location_clicked(self, index):
        name = self.location_model.locations[index.row()]
        for loc_name, loc_polys in self.location_viewer.locations.items():
            if loc_name == name:
                for loc_poly in loc_polys:
                    loc_poly.highlight()
            else:
                for loc_poly in loc_polys:
                    loc_poly.unhighlight()

    def start_click(self):
        self.label.set_defining(self.start.isChecked())
        if self.start.isChecked():
            self.start.setText('Done')

        else:
            self.start.setText('Start')


class LocationDefinerTabWidget(QTabWidget):
    # TODO: need to have unsaved change warning, so that the added/deleted changed can be reflected...
    # TODO: need to make default location associated with the application and another location for the Corpus class
    def __init__(self, system_default_location_specifications, corpus_location_specifications,
                 app_settings, app_ctx, **kwargs):
        """

        :param location_specifications: a Location object
        :param app_ctx:
        :param kwargs:
        """
        super().__init__(**kwargs)

        self.system_default_location_specifications = system_default_location_specifications
        self.corpus_location_specifications = corpus_location_specifications
        self.app_settings = app_settings
        self.app_ctx = app_ctx

        self.setDocumentMode(True)
        self.setMovable(True)
        self.setTabsClosable(True)

        self.tabbar = EditableTabBar(parent=self)
        self.tabbar.plus_clicked.connect(self.add_location_tab)
        self.setTabBar(self.tabbar)

        self.location_definer_pages = list()
        self.number_pages = 0

        self.add_default_location_tabs()

        self.tabCloseRequested.connect(self.close_handler)

    def add_default_location_tabs(self, is_system_default=False):
        locations = deepcopy(self.system_default_location_specifications) if is_system_default else self.corpus_location_specifications

        for loc_identifier, loc_param in locations.items():
            loc_page = LocationDefinerPage(
                self.app_settings,
                self.app_ctx,
                image_path=loc_param.image_path,
                locations=loc_param.location_polygons,
                default=loc_param.default,
                parent=self
            )
            self.addTab(loc_page, loc_param.name)
            self.location_definer_pages.append(loc_page)

        self.number_pages = len(self.location_definer_pages)
        self.addTab(QWidget(), QIcon(self.app_ctx.icons['plus']), 'Add location')

        # hide close button for the '' tab. The location of the close button is OS-dependent.
        if os.name == 'nt':  # For Windows, buttons appear on the right
            self.tabbar.tabButton(self.tabbar.count()-1, QTabBar.RightSide).hide()
        elif os.name == 'posix':  # For Linux and MacOS, they are on the left
            self.tabbar.tabButton(self.tabbar.count()-1, QTabBar.LeftSide).hide()

    def add_location_tab(self, index):
        self.number_pages += 1

        new = LocationDefinerPage(self.app_settings, self.app_ctx, default=False, parent=self)
        self.location_definer_pages.append(new)
        self.insertTab(index, new, 'New location')
        self.setCurrentIndex(index)

    def delete_non_default_images(self):
        for page in self.location_definer_pages:
            if (not page.default) and page.image_path:
                os.remove(page.image_path)

    def remove_all_pages(self):
        self.delete_non_default_images()

        while self.count():
            widget = self.widget(0)

            if widget:
                widget.deleteLater()

            self.removeTab(0)

        self.location_definer_pages.clear()
        self.number_pages = 0

    def import_locations(self, imported_locations):
        self.corpus_location_specifications = imported_locations

        # remove all current location pages
        while self.count():
            widget = self.widget(0)

            if widget:
                widget.deleteLater()

            self.removeTab(0)

        self.location_definer_pages.clear()
        self.number_pages = 0

        self.add_default_location_tabs(is_system_default=False)

    # Ref: https://stackoverflow.com/questions/57013483/dynamically-created-tabs-destroy-object-when-tab-closed
    def close_handler(self, index):
        widget = self.widget(index)

        if widget:
            if not widget.default and widget.image_path:
                os.remove(widget.image_path)

            widget.deleteLater()

        self.removeTab(index)

        self.location_definer_pages.pop(index)
        self.number_pages -= 1
        self.setCurrentIndex(index-1)

    def get_locations(self):
        return Locations(
            {'_'.join(loc_name.lower().split(sep=' ')): LocationParameter(name=loc_name, image_path=page.image_path, location_polygons=page.locations, default=page.default)\
             for loc_name, page in zip(self.tabbar.get_tab_names(), self.location_definer_pages)}
        )


class LocationDefinerDialog(QDialog):
    saved_locations = pyqtSignal(Locations)

    def __init__(self, system_default_location_specifications, location_specifications, app_settings, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.system_default_location_specifications = system_default_location_specifications

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.location_tab = LocationDefinerTabWidget(system_default_location_specifications, location_specifications, app_settings, app_ctx, parent=self)
        main_layout.addWidget(self.location_tab)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Close

        self.button_box = QDialogButtonBox(buttons, parent=self)

        import_button = self.button_box.addButton('Import', QDialogButtonBox.ActionRole)
        import_button.setProperty('ActionRole', 'Import')

        export_button = self.button_box.addButton('Export', QDialogButtonBox.ActionRole)
        export_button.setProperty('ActionRole', 'Export')

        # Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

    def save_new_images(self):
        for page in self.location_tab.location_definer_pages:
            if not page.default:
                page.image_path = os.path.join(self.app_settings['storage']['image'], page.basename)
                page.location_viewer.get_photo().save(page.image_path)
                page.basename = None

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Close:
            response = QMessageBox.question(self, 'Warning', 'If you close the window, any unsaved changes will be lost. Continue?')
            if response == QMessageBox.Yes:
                self.accept()

        elif standard == QDialogButtonBox.RestoreDefaults:
            self.location_tab.remove_all_pages()
            self.location_tab.add_default_location_tabs(is_system_default=True)
        elif standard == QDialogButtonBox.Save:
            self.save_new_images()
            self.saved_locations.emit(self.location_tab.get_locations())

            QMessageBox.information(self, 'Locations Saved', 'New locations have been successfully saved!')
        elif standard == QDialogButtonBox.NoButton:
            action_role = button.property('ActionRole')
            if action_role == 'Export':
                file_name, file_type = QFileDialog.getSaveFileName(self,
                                                                   self.tr('Export Locations'),
                                                                   os.path.join(
                                                                       self.app_settings['storage']['recent_folder'],
                                                                       'locations.json'),
                                                                   self.tr('JSON Files (*.json)'))

                if file_name:
                    with open(file_name, 'w') as f:
                        json.dump(self.location_tab.get_locations().get_attr_dict(), f, sort_keys=True, indent=4)

                    QMessageBox.information(self, 'Locations Exported', 'Locations have been successfully exported!')
            elif action_role == 'Import':
                file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Import Locations'),
                                                                   self.app_settings['storage']['recent_folder'],
                                                                   self.tr('JSON Corpus (*.json)'))
                if file_name:
                    with open(file_name, 'r') as f:
                        location_json = json.load(f)
                        imported_locations = Locations(
                            {loc_id: LocationParameter(name=param['name'],
                                                       image_path=param['image_path'],
                                                       location_polygons=param['location_polygons'],
                                                       default=param['default'])
                             for loc_id, param in location_json.items()}
                        )
                        self.location_tab.import_locations(imported_locations)
                        self.saved_locations.emit(self.location_tab.get_locations())
