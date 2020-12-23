from PyQt5.QtCore import (
    Qt,
    QSize,
    QRectF,
    QPoint
)

from PyQt5.QtWidgets import (
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
    QGraphicsPixmapItem
)

from PyQt5.QtGui import (
    QPixmap,
    QColor,
    QPen,
    QBrush,
    QPolygonF
)

from .hand_configuration import ConfigGlobal, Config
from .helper_widget import CollapsibleSection
from constant import SAMPLE_LOCATIONS


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
    def __init__(self, locations, viewer_size, pen_width=5, pen_color='orange', **kwargs):
        super().__init__(**kwargs)

        self.viewer_size = viewer_size

        self.pen_width = pen_width
        self.pen_color = pen_color

        self._zoom = 0
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

        self.locations = {name: {LocationPolygon(QPolygonF([QPoint(x, y) for x, y in points])) for points in polygons} for name, polygons in locations.items()}

        self.add_polygons()

    def add_polygons(self):
        for loc_polys in self.locations.values():
            for loc_poly in loc_polys:
                self._scene.addItem(loc_poly)

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
                factor = min(self.viewer_size / scenerect.width(),
                             self.viewer_size / scenerect.height())
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

    def mouseDoubleClickEvent(self, event):
        pass


class LexicalInformationPanel(QScrollArea):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

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
        self.gloss_edit.setPlaceholderText('Enter gloss here...')
        self.freq_edit = QLineEdit('1.0', parent=self)
        self.coder_edit = QLineEdit(parent=self)
        self.update_edit = QLineEdit(parent=self)
        self.note_edit = QPlainTextEdit(parent=self)
        self.note_edit.setPlaceholderText('Enter note here...')

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


class HandTranscriptionPanel(QScrollArea):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QGridLayout()
        main_frame.setLayout(main_layout)

        self.global_option = ConfigGlobal(title='Handshape global options', parent=self)
        main_layout.addWidget(self.global_option, 0, 0, 2, 1)

        self.config1 = Config(1, 'Configuration 1', parent=self)
        main_layout.addWidget(self.config1, 0, 1, 1, 2)

        self.config2 = Config(2, 'Configuration 2', parent=self)
        main_layout.addWidget(self.config2, 1, 1, 1, 2)

        self.setWidget(main_frame)


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
        neutral_img = QPixmap(self.app_ctx.hand_illustrations['neutral'])
        self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        main_layout.addWidget(self.hand_illustration)

        self.setWidget(main_frame)


class LocationSpecificationLayout(QHBoxLayout):
    def __init__(self, location_specifications, app_ctx, **kwargs):
        super().__init__(**kwargs)

        self.contact_button = QCheckBox('Contact?')

        for loc_identifier, loc_param in location_specifications.items():
            single_loc_viewer = SingleLocationViewer(loc_param.location_polygons, 250)
            single_loc_viewer.set_photo(QPixmap(app_ctx.default_location_images[loc_param.image_path] if loc_param.image_path in app_ctx.default_location_images else loc_param.image_path))
            self.addWidget(single_loc_viewer)

        self.addWidget(self.contact_button)



class ParameterPanel(QScrollArea):
    def __init__(self, app_ctx, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        self.location_layout = LocationSpecificationLayout(SAMPLE_LOCATIONS, app_ctx)

        self.orientation_layout = QVBoxLayout()
        orientation_label = QLabel('Coming soon...')
        self.orientation_layout.addWidget(orientation_label)
        self.orientation_section = CollapsibleSection(title='Orientation', parent=self)
        self.orientation_section.setContentLayout(self.orientation_layout)

        main_layout.addWidget(QLabel('label'))
        main_layout.addLayout(self.location_layout)
        main_layout.addWidget(self.orientation_section)
        self.setWidget(main_frame)
