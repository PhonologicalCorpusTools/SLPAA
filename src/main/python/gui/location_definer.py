from PyQt5.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFrame
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRectF
)

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
    def __init__(self, locations, parent=None):
        """
        :param locations: a dictionary {'name_of_location': [[polygon_points], [polygon_points]]}
        :param parent:
        """
        super().__init__(parent=parent)

        self._zoom = 0
        self._empty = True
        self._scene = QGraphicsScene(parent=self)
        self._photo = QGraphicsPixmapItem(parent=self)
        self._scene.addItem(self._photo)
        self.setScene(self._scene)

        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QBrush(QColor(30, 30, 30)))
        self.setFrameShape(QFrame.NoFrame)

        self.locations = {name: {LocationPolygon(QPolygonF([QPoint(x, y) for x, y in points])) for points in polygons} for name, polygons in locations.items()}

        self.is_defining = False
        self.defining_locations = [[]]
        self.defining_polygons = {QGraphicsPolygonItem(QPolygonF())}  # this will be the polygon being drawn
        for poly in self.defining_polygons:
            self._scene.addItem(poly)

        self.add_polygons()

    def add_polygons(self):
        for loc_polys in self.locations.values():
            for loc_poly in loc_polys:
                self._scene.addItem(loc_poly)

    def remove_all_polygons(self):
        for poly in self.defining_polygons:
            self._scene.removeItem(poly)
        for loc_polys in self.locations.values():
            for loc_poly in loc_polys:
                self._scene.removeItem(loc_poly)

    def remove_polygons(self, polygons):
        for poly in polygons:
            self._scene.removeItem(poly)

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
                factor = min(500 / scenerect.width(),
                             500 / scenerect.height())
                # viewrect = self.viewport().rect()
                # factor = min(viewrect.width() / scenerect.width(), viewrect.height() / scenerect.height())
                self.scale(factor, factor)
            self._zoom = 0

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
            pen = QPen(QColor('green'))
            pen.setWidth(5)

            self.defining_polygons = {QGraphicsPolygonItem(QPolygonF(poly)) for poly in self.defining_locations}
            for poly in self.defining_polygons:
                poly.setPen(pen)
                self._scene.addItem(poly)

class LocationDefinitionLabel(QtWidgets.QLabel):
    location = QtCore.pyqtSignal(str, str, list)

    def __init__(self, part, image):
        super().__init__()
        self.part = part
        self.base = QtGui.QPixmap(image).scaledToHeight(250)
        self.setPixmap(self.base)
        self.defining = False
        self.polygon = QtGui.QPolygon()

        self.pen = QtGui.QPen(QtGui.QColor(0, 0, 0))  # set lineColor
        self.pen.setWidth(3)

    def set_defining(self, is_defining):
        self.defining = is_defining
        if self.defining:
            self.polygon = QtGui.QPolygon()

    def mousePressEvent(self, ev):
        if self.defining:
            self.setPixmap(self.base)
            self.painter = QtGui.QPainter(self.pixmap())
            self.painter.setPen(self.pen)
            self.polygon.append(QtCore.QPoint(ev.x(), ev.y()))
            self.painter.drawPolygon(self.polygon)
            self.painter.drawPoints(self.polygon)
            self.painter.end()
            self.update()


class LocationListModel(QtCore.QAbstractListModel):
    def __init__(self, locations=None):
        super().__init__()
        self.locations = locations or []

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self.locations[index.row()]

    def rowCount(self, index):
        return len(self.locations)


class LocationDefinitionPanel(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        main_layout = QtWidgets.QGridLayout()
        self.setLayout(main_layout)

        self.location_name = QtWidgets.QLineEdit(parent=self)
        self.location_name.setPlaceholderText('New location name...')
        self.define_button = QtWidgets.QPushButton('Draw', parent=self)
        self.add_button = QtWidgets.QPushButton('+', parent=self)
        self.save_button = QtWidgets.QPushButton('Save', parent=self)
        self.delete_button = QtWidgets.QPushButton('Delete', parent=self)
        self.set_image_button = QtWidgets.QPushButton('Set image', parent=self)

        main_layout.addWidget(self.set_image_button, 0, 0, 1, 3)
        main_layout.addWidget(self.location_name, 1, 0, 1, 1)
        main_layout.addWidget(self.define_button, 1, 1, 1, 1)
        main_layout.addWidget(self.add_button, 1, 2, 1, 1)
        main_layout.addWidget(self.save_button, 2, 0, 1, 3)
        main_layout.addWidget(self.delete_button, 3, 0, 1, 3)

    def change_label(self, label):
        self.define_button.setText(label)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()

        self.is_defining = False
        self.locations = {'abdomen': [[(883, 685),
                                       (882, 750),
                                       (867, 781),
                                       (874, 801),
                                       (850, 835),
                                       (867, 846),
                                       (887, 836),
                                       (1007, 862),
                                       (1075, 854),
                                       (1110, 851),
                                       (1178, 848),
                                       (1195, 836),
                                       (1188, 819),
                                       (1192, 804),
                                       (1174, 765),
                                       (1178, 680),
                                       (1033, 672)]],
                          'chest': [[(870, 515),
                                     (874, 584),
                                     (879, 658),
                                     (884, 682),
                                     (1033, 670),
                                     (1179, 675),
                                     (1181, 598),
                                     (1188, 578),
                                     (1190, 523),
                                     (1025, 494)]],
                          'forearm': [[(760, 660),
                                       (744, 685),
                                       (709, 732),
                                       (682, 774),
                                       (631, 876),
                                       (659, 884),
                                       (678, 905),
                                       (680, 917),
                                       (695, 896),
                                       (743, 846),
                                       (773, 816),
                                       (806, 781),
                                       (830, 747)],
                                      [(1235, 771),
                                       (1267, 814),
                                       (1357, 926),
                                       (1412, 904),
                                       (1375, 831),
                                       (1348, 789),
                                       (1322, 751),
                                       (1283, 687)]],
                          'leg': [[(841, 998),
                                   (836, 1029),
                                   (836, 1148),
                                   (844, 1282),
                                   (836, 1344),
                                   (827, 1389),
                                   (864, 1428),
                                   (937, 1436),
                                   (966, 1346),
                                   (992, 1271),
                                   (1007, 1189),
                                   (1023, 1072)],
                                  [(1023, 1076),
                                   (1028, 1168),
                                   (1038, 1271),
                                   (1043, 1305),
                                   (1050, 1364),
                                   (1064, 1409),
                                   (1114, 1416),
                                   (1172, 1413),
                                   (1169, 1307),
                                   (1182, 1224),
                                   (1196, 1168),
                                   (1209, 1074),
                                   (1213, 1039)]],
                          'neck': [[(974, 365),
                                    (973, 393),
                                    (964, 394),
                                    (962, 404),
                                    (958, 413),
                                    (954, 422),
                                    (1007, 431),
                                    (1054, 433),
                                    (1081, 433),
                                    (1096, 421),
                                    (1090, 413),
                                    (1094, 407),
                                    (1086, 398),
                                    (1080, 398),
                                    (1078, 374),
                                    (1055, 390),
                                    (1023, 388),
                                    (1001, 381)]],
                          'shoulder': [[(954, 424),
                                        (941, 432),
                                        (871, 451),
                                        (869, 512),
                                        (1023, 493),
                                        (1190, 520),
                                        (1190, 477),
                                        (1111, 450),
                                        (1091, 437),
                                        (1026, 434)]],
                          'sternum': [[(1007, 581), (1000, 661), (1072, 663), (1072, 589)]],
                          'trunk': [[(870, 452),
                                     (874, 581),
                                     (883, 680),
                                     (883, 749),
                                     (864, 781),
                                     (875, 803),
                                     (848, 836),
                                     (867, 843),
                                     (846, 1000),
                                     (836, 1036),
                                     (972, 1052),
                                     (1021, 1070),
                                     (1209, 1039),
                                     (1184, 854),
                                     (1196, 838),
                                     (1188, 819),
                                     (1193, 803),
                                     (1172, 761),
                                     (1180, 683),
                                     (1182, 647),
                                     (1178, 600),
                                     (1186, 577),
                                     (1191, 564),
                                     (1188, 479),
                                     (1028, 458)]],
                          'upper arm': [[(878, 651),
                                         (831, 747),
                                         (795, 707),
                                         (761, 659),
                                         (785, 608),
                                         (800, 558),
                                         (818, 510),
                                         (844, 468),
                                         (870, 450),
                                         (869, 514),
                                         (869, 548),
                                         (874, 577)],
                                        [(1179, 682),
                                         (1217, 738),
                                         (1234, 770),
                                         (1282, 685),
                                         (1270, 658),
                                         (1259, 622),
                                         (1252, 591),
                                         (1240, 555),
                                         (1225, 520),
                                         (1208, 492),
                                         (1191, 477),
                                         (1191, 564),
                                         (1186, 582),
                                         (1179, 600)]]}

        central_widget = QtWidgets.QWidget()
        central_layout = QtWidgets.QHBoxLayout()
        #central_layout = QtWidgets.QVBoxLayout()
        central_widget.setLayout(central_layout)

        self.location_model = LocationListModel(sorted(list(self.locations.keys())))
        self.location_list_view = QtWidgets.QListView(parent=self)
        self.location_list_view.setModel(self.location_model)
        #self.location_list_view.setCurrentIndex(self.location_model.index(0))

        self.location_list_view.clicked.connect(self.location_clicked)

        self.location_definition_panel = LocationDefinitionPanel(parent=self)
        self.location_definition_panel.define_button.clicked.connect(self.start_polygon)
        self.location_definition_panel.add_button.clicked.connect(self.add_polygon)
        self.location_definition_panel.save_button.clicked.connect(self.save_new_location)
        self.location_definition_panel.delete_button.clicked.connect(self.remove_location)
        self.location_definition_panel.set_image_button.clicked.connect(self.set_image)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addWidget(self.location_list_view)
        left_layout.addWidget(self.location_definition_panel)
        central_layout.addLayout(left_layout)

        self.location_viewer = LocationViewer(self.locations, self)
        self.location_viewer.setFixedSize(500, 500)
        self.location_viewer.set_photo(QtGui.QPixmap('Body_Front_Labelled.jpg'))

        central_layout.addWidget(self.location_viewer)


        # self.label = LocationDefinitionLabel('upper', 'upper_cloth.jpg')
        # central_layout.addWidget(self.label)
        # self.base = QtGui.QPixmap('upper_cloth.jpg').scaledToHeight(250)
        # self.label.setPixmap(self.base)
        #
        # self.start = QtWidgets.QPushButton('Start')
        # self.start.setCheckable(True)
        # self.start.clicked.connect(self.start_click)
        # central_layout.addWidget(self.start)

        self.setCentralWidget(central_widget)

    def set_image(self):
        file_name, file_type = QtWidgets.QFileDialog.getOpenFileName(self,
                                                         self.tr("Open Image"), "",
                                                         self.tr("Image Files (*.png *.jpg *.bmp)"))
        self.location_viewer.set_photo(QtGui.QPixmap(file_name))

        self.location_model.locations = dict()
        self.location_model.layoutChanged.emit()
        self.location_list_view.clearSelection()
        self.location_list_view.repaint()

        # remove the item from self.locations
        self.locations = dict()
        self.location_viewer.remove_all_polygons()
        self.location_viewer.locations = dict()
        self.location_viewer.add_polygons()

    def add_polygon(self):
        self.location_viewer.defining.append([])

    def remove_location(self):
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
        #self.locations[new_location_name] = [(point.x(), point.y()) for point in self.location_viewer.defining]
        self.locations[new_location_name] = [[(point.x(), point.y()) for point in poly] for poly in self.location_viewer.defining]

        self.location_definition_panel.location_name.setText('')
        self.location_definition_panel.location_name.repaint()

        # If it's a duplicated name, need to remove the old location first
        if new_location_name in self.location_viewer.locations:
            self.location_viewer.remove_polygons(self.location_viewer.locations[new_location_name])
        #self.location_viewer.locations[new_location_name] = Polygon(QtGui.QPolygonF(self.location_viewer.defining))
        self.location_viewer.locations[new_location_name] = {Polygon(QtGui.QPolygonF(poly)) for poly in self.location_viewer.defining}
        self.location_viewer.defining = [[]]
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
            self.location_viewer.defining = [[]]
            self.location_viewer.remove_polygons(self.location_viewer.defining_polygon)

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

    # def mousePressEvent(self, e):
    #     if self.start.isChecked():
    #         self.label.setPixmap(self.base)
    #
    #         self.painter = QtGui.QPainter(self.label.pixmap())
    #         self.painter.setPen(self.pen)
    #         self.polygon.append(QtCore.QPoint(e.x(), e.y()))
    #         self.painter.drawPolygon(self.polygon)
    #         self.painter.end()
    #         self.label.update()

app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec_()