from datetime import date
from fractions import Fraction
from itertools import permutations
from collections import defaultdict
from PyQt5.QtCore import (
    Qt,
    QSize,
    QRectF,
    QPoint,
    pyqtSignal,
    QEvent
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
    QAction,
    QRadioButton,
    QComboBox,
    QCompleter,
    QTreeView,
    QMessageBox
)

from PyQt5.QtGui import (
    QPixmap,
    QColor,
    QPen,
    QBrush,
    QPolygonF,
    QTextOption,
    QFont
)

# from gui.hand_configuration import ConfigGlobal, Config
from gui.signtype_selector import SigntypeSelectorDialog
from gui.signlevelinfo_selector import SignlevelinfoSelectorDialog
from gui.helper_widget import CollapsibleSection, ToggleSwitch
# from gui.decorator import check_date_format, check_empty_gloss
from constant import DEFAULT_LOCATION_POINTS
from gui.movement_selector import MovementSpecificationLayout
from gui.handshape_selector import HandshapeSpecificationLayout
from gui.xslots_selector import XslotSelectorDialog
from lexicon.lexicon_classes import Sign, GlobalHandshapeInformation
from gui.module_selector import ModuleSelectorDialog
from gui.xslot_graphics import XslotRectButton


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

# TODO KV no longer used
# class SignLevelNote(QPlainTextEdit):
#     focus_out = pyqtSignal()
#
#     def __init__(self, **kwargs):
#         super().__init__(**kwargs)
#
#     def focusOutEvent(self, event):
#         # use focusOutEvent as the proxy for finishing editing
#         self.focus_out.emit()
#         super().focusInEvent(event)


# TODO KV xslot skeleton
class XslotPanel(QScrollArea):

    def __init__(self, mainwindow, sign=None, **kwargs):
        super().__init__(**kwargs)
        self.sign = sign
        self.mainwindow = mainwindow

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()

        self.scene = QGraphicsScene()

        self.greenbrush = QBrush(Qt.green)
        self.bluebrush = QBrush(Qt.blue)
        self.blackpen = QPen(Qt.black)
        self.blackpen.setWidth(5)

        if sign is None:

            ellipse = XslotEllipse(self, text="hello! how are you doing?")
            ellipse.setRect(10, 20, 100, 100)
            ellipse.setPen(self.blackpen)
            ellipse.setBrush(self.greenbrush)
            # print("ellipse bounding rect:", ellipse.boundingRect())
            self.scene.addItem(ellipse)

            # text = MyText("hi", self)
            # text.setPos(10,10)
            # # text.setBrush(greenbrush)
            # scene.addItem(text)

        else:
            self.refreshsign(self.sign)
        self.xslotview = QGraphicsView(self.scene, self)  # XslotGraphicsView(self.scene, self)
        self.xslotview.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.xslotview.setGeometry(0, 0, 1000, 1000)  #640, 480)
        self.setMinimumSize(1000,1000)
        # xslotview.setScene(scene)

    def refreshsign(self, sign):
        self.sign = sign
        sceneitems = self.scene.items()
        for sceneitem in sceneitems:
            self.scene.removeItem(sceneitem)

        current_x = 0
        current_y = 0

        signleveltext = QGraphicsTextItem()
        signleveltext.setPlainText("Sign: " + sign.signlevel_information.gloss)
        signleveltext.setPos(current_x, current_y*75)
        # signlevelrect = XslotRect(self, text="Sign: " + sign.signlevel_information.gloss, moduletype='signlevel', sign=self.sign, mainwindow=self.mainwindow)
        # signlevelrect.setRect(current_x, current_y*75, 640-(2*self.blackpen.width()), 50)
        # signlevelrect.setPen(self.blackpen)
        # signlevelrect.setBrush(self.greenbrush)
        # self.scene.addItem(signlevelrect)
        current_y += 1
        self.scene.addItem(signleveltext)

        if sign.signtype is not None:
            signtyperect = XslotRectButton(self, text="Sign Type: " + ";".join(sign.signtype.specs), moduletype='signtype', sign=self.sign, mainwindow=self.mainwindow)
            signtyperect.setRect(current_x, current_y*75, 640-(2*self.blackpen.width()), 50)
            current_y += 1
            signtyperect.setPen(self.blackpen)
            signtyperect.setBrush(self.greenbrush)
            # print("ellipse bounding rect:", ellipse.boundingRect())
            self.scene.addItem(signtyperect)

        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none' and sign.xslotstructure is not None:
            xslotrects = {}
            numwholes = sign.xslotstructure.number
            # partial = max([p.numerator/p.denominator for p in sign.xslotstructure.partials+[Fraction(0, 1)]])
            partial = float(sign.xslotstructure.additionalfraction)
            roundedup = numwholes + (1 if partial > 0 else 0)
            xslot_width = 640 / (numwholes + roundedup)
            if numwholes + partial > 0:
                for i in range(numwholes):
                    xslotrect = XslotRectButton(self, text="x" + str(i + 1), moduletype='xslot', sign=self.sign, mainwindow=self.mainwindow)
                    xloc = 0 + i * xslot_width - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, current_y * 75, xslot_width, 50)
                    xslotrect.setPen(self.blackpen)
                    xslotrect.setBrush(self.greenbrush)
                    xslotrects["x"+str(i+1)] = xslotrect
                    self.scene.addItem(xslotrect)
                if partial > 0:
                    xslotrect = XslotRectButton(self, text="x" + str(numwholes + 1), moduletype='xslot', sign=self.sign, mainwindow=self.mainwindow, proportionfill=partial)
                    xloc = 0 + numwholes * xslot_width - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, current_y * 75, xslot_width, 50)
                    xslotrect.setPen(self.blackpen)
                    xslotrect.setBrush(self.greenbrush)
                    xslotrects["x"+str(numwholes+1)] = xslotrect
                    self.scene.addItem(xslotrect)

                    # xslotrect = XslotRect(self, text="", moduletype='xslot', sign=self.sign, mainwindow=self.mainwindow)
                    # xloc = 0 + numwholes * xslot_width - (2 * self.blackpen.width()) + xslot_width * partial
                    # xslotrect.setRect(xloc, current_y * 75, xslot_width * (1-partial), 50)
                    # xslotrect.setPen(self.blackpen)
                    # xslotrect.setBrush(self.greenbrush)
                    # xslotrects["x"+str(0)] = xslotrect
                    # self.scene.addItem(xslotrect)
            current_y += 1

        mvmtrects = {}
        num_mvmtmods = len(self.sign.movementmodules)
        if num_mvmtmods > 0:
            if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                for idx, m in enumerate(self.sign.movementmodules.keys()):
                    for hand in [h for h in self.sign.movementmodules[m][1].keys() if self.sign.movementmodules[m][1][h]]:
                        hand_abbr = hand  #[:3] TODO KV
                        mvmtrect = XslotRectButton(self, text=hand_abbr + "." + m, moduletype='movement', sign=self.sign, mainwindow=self.mainwindow)
                        mvmtrect.setRect(current_x, current_y*75, 640 - (2 * self.blackpen.width()), 50)
                        current_y += 1
                        mvmtrect.setPen(self.blackpen)
                        mvmtrect.setBrush(self.greenbrush)
                        mvmtrects[hand_abbr+"."+m] = mvmtrect
                        self.scene.addItem(mvmtrect)
            else:  # 'manual' or 'auto'
                mvmt_width = 640 / num_mvmtmods
                for idx, m in enumerate(self.sign.movementmodules.keys()):
                    for hand in [h for h in self.sign.movementmodules[m][1].keys() if self.sign.movementmodules[m][1][h]]:
                        hand_abbr = hand[:3]
                        mvmtrect = XslotRectButton(self, text=hand_abbr + "." + m, moduletype='movement', sign=self.sign, mainwindow=self.mainwindow)
                        xloc = 0 + idx * mvmt_width - (2*self.blackpen.width())
                        mvmtrect.setRect(xloc, current_y*75, mvmt_width, 50)
                        mvmtrect.setPen(self.blackpen)
                        mvmtrect.setBrush(self.greenbrush)
                        mvmtrects[hand_abbr+"."+m] = mvmtrect
                        self.scene.addItem(mvmtrect)
                current_y += 1

        hsrects = {}
        num_hsmods = len(self.sign.handshapemodules)
        if num_hsmods > 0:
            if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                for idx, hs in enumerate(self.sign.handshapemodules.keys()):
                    hsrect = XslotRectButton(self, text=hs, moduletype='handshape', sign=self.sign, mainwindow=self.mainwindow)
                    hsrect.setRect(current_x, current_y*75, 640 - (2 * self.blackpen.width()), 50)
                    current_y += 1
                    hsrect.setPen(self.blackpen)
                    hsrect.setBrush(self.greenbrush)
                    hsrects[hs] = hsrect
                    self.scene.addItem(hsrect)
            else:  # 'manual' or 'auto'
                hs_width = 640 / num_hsmods
                for idx, hs in enumerate(self.sign.handshapemodules.keys()):
                    hsrect = XslotRectButton(self, text=hs, moduletype='handshape', sign=self.sign, mainwindow=self.mainwindow)
                    xloc = 0 + idx * hs_width - (2*self.blackpen.width())
                    hsrect.setRect(xloc, current_y*75, hs_width, 50)
                    hsrect.setPen(self.blackpen)
                    hsrect.setBrush(self.greenbrush)
                    hsrects[hs] = hsrect
                    self.scene.addItem(hsrect)
                current_y += 1

#  TODO KV delete
# class XslotGraphicsView(QGraphicsView):
#     def __init__(self, scene, parent, **kwargs):
#         super().__init__(scene, parent, **kwargs)

#  TODO KV delete
# class MyText(QGraphicsTextItem):
#     def __init__(self, text, parentwidget, restingbrush=QBrush(Qt.blue), hoverbrush=QBrush(Qt.yellow)):
#         super().__init__()
#         self.setPlainText(text)
#         self.restingbrush = restingbrush
#         self.hoverbrush = hoverbrush
#         # self.setAcceptHoverEvents(True)
#         self.parentwidget = parentwidget
#
#     def mouseReleaseEvent(self, event):
#         print("text released")
#         QMessageBox.information(self.parentwidget, 'Text clicked', 'You clicked the text!')
#
#     def mousePressEvent(self, event):
#         print("text pressed")
#
#     # def hoverEnterEvent(self, event):
#     #     self.setBrush(self.hoverbrush)
#     #
#     # def hoverLeaveEvent(self, event):
#     #     self.setBrush(self.restingbrush)
#
#     def boundingRect(self):
#         # penWidth = self.pen().width()
#         return QRectF(5, 5, 50, 10)



class XslotEllipse(QGraphicsEllipseItem):
    def __init__(self, parentwidget, text="", restingbrush=QBrush(Qt.green), hoverbrush=QBrush(Qt.yellow)):
        super().__init__()
        self.restingbrush = restingbrush
        self.hoverbrush = hoverbrush
        self.setAcceptHoverEvents(True)
        self.parentwidget = parentwidget
        self.text = text
        self.hover = False

    def mouseReleaseEvent(self, event):
        print("ellipse released")
        QMessageBox.information(self.parentwidget, 'Ellipse clicked', 'You clicked the ellipse!')

    def mousePressEvent(self, event):
        print("ellipse pressed")

    def hoverEnterEvent(self, event):
        self.setBrush(self.hoverbrush)
        self.hover = True

    def hoverLeaveEvent(self, event):
        self.setBrush(self.restingbrush)
        self.hover = False

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)
        pen = painter.pen()
        pen.setWidth(5)
        pen.setColor(Qt.black)
        painter.setPen(pen)
        painter.setBrush(self.hoverbrush if self.hover else self.restingbrush)
        painter.drawEllipse(self.rect())
        textoption = QTextOption(Qt.AlignCenter)
        # textoption.setAlignment(Qt.AlignCenter)
        painter.drawText(self.rect(), self.text, textoption)

    # def boundingRect(self):
    #     penWidth = self.pen().width()
    #     return QRectF(-radius - penWidth / 2, -radius - penWidth / 2,
    #                   diameter + penWidth, diameter + penWidth)


# # TODO KV xslot mockup
# class XslotImagePanel(QScrollArea):
#
#     def __init__(self, mainwindow, **kwargs):
#         super().__init__(**kwargs)
#
#         self.setFrameStyle(QFrame.StyledPanel)
#         main_frame = QFrame(parent=self)
#
#         main_layout = QVBoxLayout()
#
#         self.pixmap = QPixmap(mainwindow.app_ctx.xslotimage['xslot'])
#         self.lbl = QLabel()
#         self.lbl.setPixmap(self.pixmap)
#         main_layout.addWidget(self.lbl)
#         main_frame.setLayout(main_layout)
#
#         self.setWidget(main_frame)

class SignSummaryPanel(QScrollArea):
    sign_updated = pyqtSignal(Sign)

    def __init__(self, sign, mainwindow, **kwargs):
        super().__init__(**kwargs)

        self.mainwindow = mainwindow

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        self._sign = sign
        self.system_default_signtype = mainwindow.system_default_signtype
        self.module_buttons = []

        self.signgloss_label = QLabel("Sign: " + sign.signlevel_information.gloss if sign else "")
        self.signlevel_button = QPushButton("Sign-level information")
        self.signlevel_button.clicked.connect(self.handle_signlevelbutton_click)

        self.signtype_button = QPushButton("Sign type selection")
        self.signtype_button.clicked.connect(self.handle_signtypebutton_click)
        self.module_buttons.append(self.signtype_button)

        # TODO KV
        # if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'manual':  # could also be 'none' or 'auto'
        self.xslots_button = QPushButton("Specify X-slots")
        self.xslots_button.clicked.connect(self.handle_xslotsbutton_click)
        self.module_buttons.append(self.xslots_button)

        self.movement_button = QPushButton("Movement selection")
        self.movement_button.setProperty("existingmodule", False)
        self.movement_button.clicked.connect(self.handle_movementbutton_click)
        self.module_buttons.append(self.movement_button)

        self.location_button = QPushButton("Location selection")
        self.location_button.clicked.connect(self.handle_locationbutton_click)
        self.module_buttons.append(self.location_button)

        self.handshape_button = QPushButton("Handshape selection")
        self.handshape_button.setProperty("existingmodule", False)
        self.handshape_button.clicked.connect(self.handle_handshapebutton_click)
        self.module_buttons.append(self.handshape_button)

        self.orientation_button = QPushButton("Orientation selection")
        self.orientation_button.clicked.connect(self.handle_orientationbutton_click)
        self.module_buttons.append(self.orientation_button)

        self.contact_button = QPushButton("Contact selection")
        self.contact_button.clicked.connect(self.handle_contactbutton_click)
        self.module_buttons.append(self.contact_button)

        main_layout.addWidget(self.signgloss_label)
        main_layout.addWidget(self.signlevel_button)
        for btn in self.module_buttons:
            main_layout.addWidget(btn)
        self.enable_module_buttons(False)
        # main_layout.addWidget(self.signlevel_button)
        # main_layout.addWidget(self.signtype_button)
        # main_layout.addWidget(self.movement_button)
        # main_layout.addWidget(self.handshape_button)
        # main_layout.addWidget(self.orientation_button)
        # main_layout.addWidget(self.location_button)
        # main_layout.addWidget(self.contact_button)

        self.setWidget(main_frame)

    def enable_module_buttons(self, yesorno):
        for btn in self.module_buttons:
            btn.setEnabled(yesorno)
        self.xslots_button.setEnabled(yesorno and self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'manual')

    @property
    def sign(self):
        return self._sign

    @sign.setter
    def sign(self, sign):
        self._sign = sign
        self.signgloss_label.setText("Sign: " + sign.signlevel_information.gloss if sign else "")

    def clear(self):
        self._sign = None
        self.signgloss_label.setText("Sign: ")

    def handle_xslotsbutton_click(self):
        timing_selector = XslotSelectorDialog(self.sign.xslotstructure if self.sign else None, self.mainwindow, parent=self)  #  self.mainwindow.app_settings,
        timing_selector.saved_xslots.connect(self.handle_save_xslots)
        timing_selector.exec_()

    def handle_save_xslots(self, xslots):
        self.sign.xslotstructure = xslots
        self.sign_updated.emit(self.sign)

    def handle_signlevelbutton_click(self):
        signlevelinfo_selector = SignlevelinfoSelectorDialog(self.sign.signlevel_information if self.sign else None, self.mainwindow, self.mainwindow.app_settings, parent=self)
        signlevelinfo_selector.saved_signlevelinfo.connect(self.handle_save_signlevelinfo)
        signlevelinfo_selector.exec_()

    def handle_save_signlevelinfo(self, signlevelinfo):
        if self.sign:
            # an existing sign is highlighted; update it
            self.sign.signlevel_information = signlevelinfo
        else:
            # this is a new sign
            if signlevelinfo.gloss in self.mainwindow.corpus.get_sign_glosses():
                QMessageBox.critical(self, 'Duplicated Gloss',
                                     'Please use a different gloss. Duplicated glosses are not allowed.')
                # TODO KV don't want the signlevel info to close if the gloss is rejected--
                #  make the user choose a new one instead
                return
            newsign = Sign(signlevelinfo)
            self.sign = newsign
            self.mainwindow.corpus.add_sign(newsign)
            self.mainwindow.handle_sign_selected(self.sign.signlevel_information.gloss)

        self.sign_updated.emit(self.sign)
        self.mainwindow.corpus_view.updated_glosses(self.mainwindow.corpus.get_sign_glosses(), self.sign.signlevel_information.gloss)

    def handle_signtypebutton_click(self):
        signtype_selector = SigntypeSelectorDialog(self.sign.signtype, self.mainwindow, parent=self)
        signtype_selector.saved_signtype.connect(self.handle_save_signtype)
        signtype_selector.exec_()

    def handle_save_signtype(self, signtype):
        self.sign.signtype = signtype
        self.sign_updated.emit(self.sign)

    def handle_movementbutton_click(self):
        button = self.sender()
        # TODO KV
        editing_existing = button.property("existingmodule")
        existing_key = None
        moduletoload = None
        if editing_existing:
            existing_key = button.text()
            moduletoload = self.sign.movementmodules[existing_key]
        # movement_selector = MovementSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload, parent=self)
        movement_selector = ModuleSelectorDialog(mainwindow=self.mainwindow, hands=None, x_start=None, x_end=None, enable_addnew=(not editing_existing), modulelayout=MovementSpecificationLayout(moduletoload), moduleargs=None)
        movement_selector.get_savedmodule_signal().connect(lambda movementtree, hands: self.handle_save_movement(movementtree, hands, existing_key))
        movement_selector.exec_()

    def handle_save_movement(self, movementtree, hands_dict, existing_key):
        if existing_key is None or existing_key not in self.sign.movementmodules.keys():
            self.sign.addmovementmodule(movementtree, hands_dict)
        else:
            self.sign.movementmodules[existing_key] = movementtree
        self.sign_updated.emit(self.sign)

    def handle_handshapebutton_click(self):
        button = self.sender()
        # TODO KV
        editing_existing = button.property("existingmodule")
        existing_key = None
        moduletoload = None
        if editing_existing:
            existing_key = button.text()
            moduletoload = self.sign.handshapemodules[existing_key]
        # handshape_selector = HandshapeSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload, parent=self)
        handshape_selector = ModuleSelectorDialog(mainwindow=self.mainwindow, hands=None, x_start=None, x_end=None, enable_addnew=(not editing_existing), modulelayout=HandshapeSpecificationLayout(self.mainwindow.app_ctx.predefined, moduletoload), moduleargs=None)
        handshape_selector.get_savedmodule_signal().connect(lambda hs_global, hs_transcription: self.handle_save_handshape(GlobalHandshapeInformation(hs_global.get_value()), hs_transcription, existing_key))
        handshape_selector.exec_()

    def handle_save_handshape(self, hs_globalinfo, handshapetxn, existing_key):
        if existing_key is None or existing_key not in self.sign.handshapemodules.keys():
            self.sign.addhandshapemodule(hs_globalinfo, handshapetxn)
        else:
            self.sign.handshapemodules[existing_key] = [hs_globalinfo, handshapetxn]
        self.sign_updated.emit(self.sign)
        # self.update_handshapemodulebuttons()

    def handle_contactbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Contact module functionality not yet linked.')

    def handle_orientationbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Orientation module functionality not yet linked.')

    def handle_locationbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Location module functionality not yet linked.')

# TODO KV no longer used
# class HandTranscriptionPanel(QScrollArea):
#     selected_hand = pyqtSignal(int)
#
#     def __init__(self, predefined_ctx, **kwargs):
#         super().__init__(**kwargs)
#
#         self.setFrameStyle(QFrame.StyledPanel)
#         main_frame = QFrame(parent=self)
#
#         main_layout = QGridLayout()
#         main_frame.setLayout(main_layout)
#
#         self.global_info = ConfigGlobal(title='Handshape global options', parent=self)
#         main_layout.addWidget(self.global_info, 0, 0, 2, 1)
#
#         self.config1 = Config(1, 'Configuration 1', predefined_ctx, parent=self)
#         main_layout.addWidget(self.config1, 0, 1, 1, 2)
#
#         self.config2 = Config(2, 'Configuration 2', predefined_ctx, parent=self)
#         main_layout.addWidget(self.config2, 1, 1, 1, 2)
#
#         self.setWidget(main_frame)
#
#     def clear(self):
#         self.global_info.clear()
#         self.config1.clear()
#         self.config2.clear()
#
#     def set_value(self, global_handshape_info, hand_transcription):
#         self.global_info.set_value(global_handshape_info)
#         self.config1.set_value(hand_transcription.config1)
#         self.config2.set_value(hand_transcription.config2)
#
#     def change_hand_selection(self, hand):
#         if hand == 1:
#             self.button1.setChecked(True)
#         elif hand == 2:
#             self.button2.setChecked(True)
#         elif hand == 3:
#             self.button3.setChecked(True)
#         elif hand == 4:
#             self.button4.setChecked(True)
#
#     def insert_radio_button(self, focused_hand):
#         self.selected_hand_group = QButtonGroup(parent=self)
#         self.button1, self.button2 = self.config1.insert_radio_button()
#         self.button3, self.button4 = self.config2.insert_radio_button()
#
#         self.button1.clicked.connect(lambda: self.selected_hand.emit(1))
#         self.button2.clicked.connect(lambda: self.selected_hand.emit(2))
#         self.button3.clicked.connect(lambda: self.selected_hand.emit(3))
#         self.button4.clicked.connect(lambda: self.selected_hand.emit(4))
#
#         if focused_hand == 1:
#             self.button1.setChecked(True)
#         elif focused_hand == 2:
#             self.button2.setChecked(True)
#         elif focused_hand == 3:
#             self.button3.setChecked(True)
#         elif focused_hand == 4:
#             self.button4.setChecked(True)
#
#         self.selected_hand_group.addButton(self.button1, 1)
#         self.selected_hand_group.addButton(self.button2, 2)
#         self.selected_hand_group.addButton(self.button3, 3)
#         self.selected_hand_group.addButton(self.button4, 4)
#
#     def remove_radio_button(self):
#         self.config1.remove_radio_button()
#         self.config2.remove_radio_button()
#         self.selected_hand_group.deleteLater()
#
#     def get_hand_transcription(self, hand=None):
#         if hand is None:
#             hand = self.selected_hand_group.checkedId()
#
#         if hand == 1:
#             return self.config1.hand1.get_hand_transcription_list()
#         elif hand == 2:
#             return self.config1.hand2.get_hand_transcription_list()
#         elif hand == 3:
#             return self.config2.hand1.get_hand_transcription_list()
#         elif hand == 4:
#             return self.config2.hand2.get_hand_transcription_list()
#
#     def set_predefined(self, transcription_list, hand=None):
#         if hand is None:
#             hand = self.selected_hand_group.checkedId()
#
#         if hand == 1:
#             self.config1.hand1.set_predefined(transcription_list)
#         elif hand == 2:
#             self.config1.hand2.set_predefined(transcription_list)
#         elif hand == 3:
#             self.config2.hand1.set_predefined(transcription_list)
#         elif hand == 4:
#             self.config2.hand2.set_predefined(transcription_list)


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

# TODO KV no longer used
# class ParameterPanel(QScrollArea):
#     def __init__(self, location_specifications, app_ctx, **kwargs):  # TODO KV movement_specifications,
#         super().__init__(**kwargs)
#
#         self.setFrameStyle(QFrame.StyledPanel)
#         main_frame = QFrame(parent=self)
#
#         #TODO: need to figure out how to do this...
#         main_frame.setFixedSize(1000, 1000)
#
#         main_layout = QVBoxLayout()
#         main_frame.setLayout(main_layout)
#
#         self.location_layout = LocationSpecificationLayout(location_specifications, app_ctx)
#         self.location_section = CollapsibleSection(title='Location', parent=self)
#         self.location_section.setContentLayout(self.location_layout)
#
#         self.orientation_layout = QVBoxLayout()
#         orientation_label = QLabel('Coming soon...')
#         self.orientation_layout.addWidget(orientation_label)
#         self.orientation_section = CollapsibleSection(title='Orientation', parent=self)
#         self.orientation_section.setContentLayout(self.orientation_layout)
#
#         # main_layout.addWidget(QLabel('Location'))
#         # main_layout.addLayout(self.location_layout)
#         main_layout.addWidget(self.location_section)
#         main_layout.addWidget(self.orientation_section)
#
#         self.setWidget(main_frame)
#
#     def clear(self, location_specifications, app_ctx):  # TODO KV movement_specifications,
#         self.location_layout.clear(location_specifications, app_ctx)
#         # self.movement_layout.clear(movement_specifications, app_ctx) # TODO KV
#
#     def set_value(self, value):
#         self.location_layout.set_value(value)
#         # self.movement_layout.set_value(value)

