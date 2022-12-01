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
from gui.location_selector import LocationSpecificationLayout as LocationSpecificationLayout2
from gui.handshape_selector import HandConfigSpecificationLayout
from gui.xslots_selector import XslotSelectorDialog
from lexicon.lexicon_classes import Sign, GlobalHandshapeInformation, TimingInterval, TimingPoint
from gui.module_selector import ModuleSelectorDialog
from gui.xslot_graphics import XslotRect, XslotRectModuleButton, XslotSummaryScene, XslotEllipseModuleButton


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


class XslotPanel(QScrollArea):

    def __init__(self, mainwindow, sign=None, **kwargs):
        super().__init__(**kwargs)
        self.sign = sign
        self.mainwindow = mainwindow
        self.settings = self.mainwindow.app_settings

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)
        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        # self.scene = QGraphicsScene()
        self.scene = XslotSummaryScene()
        self.scene.modulerect_clicked.connect(self.handle_modulebutton_clicked)
        self.scene.moduleellipse_clicked.connect(self.handle_modulebutton_clicked)

        self.scene_width = 1100
        self.xslots_width = 1000
        self.indent = self.scene_width - self.xslots_width
        self.default_xslot_height = 40
        self.verticalspacing = 10

        self.x_offset = 0
        self.current_y = 0
        self.onexslot_width = 0

        self.moduleitems = []
        self.gridlinestart = 0
        self.refreshsign()  # self.sign)
        self.xslotview = QGraphicsView(self.scene)  # , self)  # XslotGraphicsView(self.scene, self)
        self.xslotview.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.xslotview.setGeometry(0, 0, 1000, 600)
        main_layout.addWidget(self.xslotview)
        self.setLayout(main_layout)
        # self.xslotview.setEnabled(True)
        self.setMinimumSize(1000, 600)
        # xslotview.setScene(scene)

    def refreshsign(self, sign=None):
        if sign is None and self.mainwindow.current_sign is None:
            self.sign = None
        elif sign is not None:
            self.sign = sign
        elif self.mainwindow.current_sign is not None:
            self.sign = self.mainwindow.current_sign

        for sceneitem in self.scene.items():
            self.scene.removeItem(sceneitem)

        self.moduleitems = []
        self.current_y = 0

        # set the top text, either welcome or the sign gloss + ID

        signleveltext = QGraphicsTextItem()
        signleveltext.setPlainText("Welcome! Add a new sign to get started.")
        if self.sign is not None:
            # signleveltext.setPlainText(self.sign.signlevel_information.gloss + " - " + self.sign.signlevel_information.entryid_string())
            signleveltext.setPlainText(self.sign.signlevel_information.gloss + " - " + self.entryid_string())
        signleveltext.setPos(self.x_offset, self.current_y*(self.default_xslot_height+self.verticalspacing))
        self.current_y += 1
        self.scene.addItem(signleveltext)

        if self.sign is None:
            return

        self.addsigntype()
        self.addxslots()
        self.addhand("H1")
        self.addhand("H2")
        self.addgridlines()

    def entryid_string(self, entryid_int=None):
        numdigits = self.settings['display']['entryid_digits']
        if entryid_int is None:
            entryid_int = self.sign.signlevel_information.entryid
        entryid_string = str(entryid_int)
        entryid_string = "0" * (numdigits - len(entryid_string)) + entryid_string
        return entryid_string

    def addsigntype(self):
        # signtypetext = "Sign Type (TODO): "
        # if self.sign.signtype is None:
        #     signtypetext += "n/a"
        # else:
        if self.sign.signtype is not None:
            signtypetext = "Sign Type: " + self.sign.signtype.getabbreviation()
            # specslist = [triple for triple in self.sign.signtype.specslist]
            # toplevelitems = [st_triple for st_triple in specslist if "." not in st_triple[0]]
            # for topleveltriple in toplevelitems:
            #     specslist.remove(topleveltriple)
            #     includeabbrev = [st_triple for st_triple in specslist if st_triple[0].startswith(topleveltriple[1]) and st_triple[2]]
            #     # signtypepaths = [st[0] for st in includeabbrev]
            #     signtypeabbreviations = [st[1] for st in includeabbrev]
            #     # signtypeabbrevincludes = [st[2] for st in includeabbrev]
            #     signtypetext += topleveltriple[1]
            #     if len(signtypeabbreviations) > 0:
            #         signtypetext += " (" + "; ".join(signtypeabbreviations) + ") "
            signtyperect = XslotRectModuleButton(self, text=signtypetext, moduletype='signtype', sign=self.sign)
            signtyperect.setRect(self.x_offset + self.indent, self.current_y*(self.default_xslot_height+self.verticalspacing), self.xslots_width, self.default_xslot_height)  # 640-(2*self.blackpen.width()), 50)
            self.scene.addItem(signtyperect)
        self.current_y += 1

    def addxslots(self):
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none' and self.sign.xslotstructure is not None and self.sign.specifiedxslots:
            xslotrects = {}
            numwholes = self.sign.xslotstructure.number
            partial = float(self.sign.xslotstructure.additionalfraction)
            roundedup = numwholes + (1 if partial > 0 else 0)
            self.onexslot_width = self.xslots_width / roundedup
            if numwholes + partial > 0:
                for i in range(numwholes):
                    xslotrect = XslotRect(self, text="x" + str(i + 1), moduletype='xslot', sign=self.sign)
                    xloc = self.indent + i * self.onexslot_width  # - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, self.current_y * (self.default_xslot_height+self.verticalspacing), self.onexslot_width, self.default_xslot_height)
                    xslotrects["x"+str(i+1)] = xslotrect
                    self.scene.addItem(xslotrect)
                if partial > 0:
                    xslotrect = XslotRect(self, text="x" + str(numwholes + 1), moduletype='xslot', sign=self.sign, proportionfill=partial)
                    xloc = self.indent + numwholes * self.onexslot_width #  - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, self.current_y * (self.default_xslot_height + self.verticalspacing), self.onexslot_width,
                                      self.default_xslot_height)
                    xslotrects["x"+str(numwholes+1)] = xslotrect
                    self.scene.addItem(xslotrect)
            self.current_y += 1
            self.gridlinestart = self.current_y * (self.default_xslot_height + self.verticalspacing)

    def addhand(self, hand):
        # add hand label
        handtext = QGraphicsTextItem()
        handtext.setPlainText("Hand " + hand[-1])
        if hand == "H2":
            self.current_y += 1.5
        handtext.setPos(self.x_offset, self.current_y * (self.default_xslot_height + self.verticalspacing))
        self.scene.addItem(handtext)

        # self.addmovement(hand=hand)
        self.addparameter(hand=hand, moduletype='movement')
        self.addhandpart(hand=hand)
        # self.addlocation(hand=hand)
        self.addparameter(hand=hand, moduletype='location')
        self.addcontact(hand=hand)
        self.addorientation(hand=hand)
        self.addhandconfig(hand=hand)
    #
    # def addmovement(self, hand):
    #     # TODO KV implement spacing efficiency - for now put intervals on one row and points on another
    #     num_mvmtmods = len(self.sign.movementmodules)
    #     if num_mvmtmods > 0:
    #         if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
    #             # everything just gets listed vertically
    #             for idx, m in enumerate(self.sign.movementmodules.keys()):
    #                 mvmtmod = self.sign.movementmodules[m]
    #                 mvmtmodid = mvmtmod.uniqueid
    #                 if mvmtmod.hands[hand]:
    #                     mvmtrect = XslotRectModuleButton(self, module_uniqueid=mvmtmodid, text=hand+".Mov"+str(idx+1), moduletype='movement', sign=self.sign)
    #                     mvmtabbrev = m.getabbreviation()
    #                     mvmtrect.setToolTip(mvmtabbrev)
    #                     mvmtrect.setRect(self.current_x, self.current_y * (self.default_xslot_height + self.verticalspacing), self.xslots_width, self.default_xslot_height)
    #                     self.current_y += 1
    #                     self.scene.addItem(mvmtrect)
    #         else:  # 'manual' or 'auto'
    #             # associate modules with x-slots
    #             intervals = []
    #             points = []
    #
    #             for midx, m_id in enumerate(self.sign.movementmodules.keys()):
    #                 mvmtmod = self.sign.movementmodules[m_id]
    #                 # mvmtmodid = mvmtmod.uniqueid
    #                 if mvmtmod.hands[hand]:
    #                     for tidx, t in enumerate(mvmtmod.timingintervals):
    #                         if t.ispoint():
    #                             points.append((midx, m_id, tidx, t))
    #                         else:
    #                             intervals.append((midx, m_id, tidx, t))
    #
    #             self.addmovementintervals(hand, intervals)
    #             self.addmovementpoints(hand, points)
    #
    # def addmovementintervals(self, hand, intervals):
    #     for i_idx, (midx, m_id, tidx, t) in enumerate(intervals):
    #         mvmtrect = XslotRectModuleButton(self, module_uniqueid=m_id,
    #                                          text=hand + ".Mov" + str(midx + 1),
    #                                          moduletype='movement',
    #                                          sign=self.sign)
    #         mvmtabbrev = self.sign.movementmodules[m_id].getabbreviation()
    #         mvmtrect.setToolTip(mvmtabbrev)
    #         intervalsalreadydone = [t for (mi, m, ti, t) in intervals[:i_idx]]
    #         anyoverlaps = [t.overlapsinterval(prev_t) for prev_t in intervalsalreadydone]
    #         if True in anyoverlaps:
    #             self.current_y += 1
    #         mvmtrect.setRect(*self.getxywh(t))  # how big is it / where does it go?
    #         self.moduleitems.append(mvmtrect)
    #     self.current_y += 1
    #
    # def addmovementpoints(self, hand, points):
    #     for i_idx, (midx, m_id, tidx, t) in enumerate(points):
    #         mvmtellipse = XslotEllipseModuleButton(self, module_uniqueid=m_id,
    #                                                text=hand + ".Mov" + str(midx + 1),
    #                                                moduletype='movement',
    #                                                sign=self.sign)
    #         mvmtabbrev = self.sign.movementmodules[m_id].getabbreviation()
    #         mvmtellipse.setToolTip(mvmtabbrev)
    #         pointsalreadydone = [t for (mi, m, ti, t) in points[:i_idx]]
    #         anyequivalent = [t.startpoint.equivalent(prev_t.startpoint) for prev_t in pointsalreadydone]
    #         if True in anyequivalent:
    #             self.current_y += 1
    #         mvmtellipse.setRect(*self.getxywh(t))  # how big is it / where does it go?
    #         self.moduleitems.append(mvmtellipse)
    #     self.current_y += 1

    def getxywh(self, timinginterval):
        if timinginterval.ispoint():
            # it's a point; plan an ellipse
            yradius = 40
            pointfrac = timinginterval.startpoint.wholepart - 1 + timinginterval.startpoint.fractionalpart
            x = self.x_offset + self.indent + float(pointfrac)*self.onexslot_width - yradius
            y = self.current_y * (self.default_xslot_height + self.verticalspacing)
            w = 2 * yradius
            h = self.default_xslot_height
        else:
            # it's an interval; plan a rectangle
            if timinginterval == TimingInterval(TimingPoint(0,0),TimingPoint(0,1)):
                # then it's the whole sign
                startfrac = 0
                endfrac = self.sign.xslotstructure.number + self.sign.xslotstructure.additionalfraction
            else:
                # it's a subinterval
                startfrac = timinginterval.startpoint.wholepart - 1 + timinginterval.startpoint.fractionalpart
                endfrac = timinginterval.endpoint.wholepart - 1 + timinginterval.endpoint.fractionalpart
            widthfrac = endfrac - startfrac

            x = self.x_offset + self.indent + float(startfrac)*self.onexslot_width
            y = self.current_y * (self.default_xslot_height + self.verticalspacing)
            w = float(widthfrac) * self.onexslot_width
            h = self.default_xslot_height

        return x, y, w, h

    def addhandpart(self, hand):
        return  # TODO KV implement

    def addlocation(self, hand):
        return  # TODO KV implement

    def addparameter(self, hand, moduletype):
        # TODO KV implement spacing efficiency - for now put intervals on one row and points on another
        moduletypeabbrev = ''
        parammodules = None
        if moduletype == 'location':
            parammodules = self.sign.locationmodules
            moduletypeabbrev = 'Loc'
        elif moduletype == 'movement':
            parammodules = self.sign.movementmodules
            moduletypeabbrev = 'Mov'
        else:
            return
        # TODO KV add the rest of the parameter modules when ready

        num_parammods = len(parammodules)
        if num_parammods > 0:
            if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # everything just gets listed vertically
                for idx, m in enumerate(parammodules.keys()):
                    parammod = parammodules[m]
                    parammodid = parammod.uniqueid
                    if parammod.hands[hand]:
                        paramrect = XslotRectModuleButton(self, module_uniqueid=parammodid,
                                                          text=hand + "." + moduletypeabbrev + str(idx + 1), moduletype=moduletype,
                                                          sign=self.sign)
                        paramabbrev = m.getabbreviation()
                        paramrect.setToolTip(paramabbrev)
                        paramrect.setRect(self.current_x,
                                          self.current_y * (self.default_xslot_height + self.verticalspacing),
                                          self.xslots_width, self.default_xslot_height)
                        self.current_y += 1
                        self.scene.addItem(paramrect)
            else:  # 'manual' or 'auto'
                # associate modules with x-slots
                intervals = []
                points = []

                for midx, m_id in enumerate(parammodules.keys()):
                    parammod = parammodules[m_id]
                    # parammodid = parammod.uniqueid
                    if parammod.hands[hand]:
                        for tidx, t in enumerate(parammod.timingintervals):
                            if t.ispoint():
                                points.append((midx, m_id, tidx, t))
                            else:
                                intervals.append((midx, m_id, tidx, t))

                self.addparameterintervals(hand, intervals, moduletype, moduletypeabbrev, parammodules)
                self.addparameterpoints(hand, points, moduletype, moduletypeabbrev, parammodules)

    def addparameterintervals(self, hand, intervals, moduletype, moduletypeabbrev, parammodules):
        for i_idx, (midx, m_id, tidx, t) in enumerate(intervals):
            paramrect = XslotRectModuleButton(self, module_uniqueid=m_id,
                                              text=hand + "." + moduletypeabbrev + str(midx + 1),
                                              moduletype=moduletype,
                                              sign=self.sign)
            paramabbrev = parammodules[m_id].getabbreviation()
            paramrect.setToolTip(paramabbrev)
            intervalsalreadydone = [t for (mi, m, ti, t) in intervals[:i_idx]]
            anyoverlaps = [t.overlapsinterval(prev_t) for prev_t in intervalsalreadydone]
            if True in anyoverlaps:
                self.current_y += 1
            paramrect.setRect(*self.getxywh(t))  # how big is it / where does it go?
            self.moduleitems.append(paramrect)
        self.current_y += 1

    def addparameterpoints(self, hand, points, moduletype, moduletypeabbrev, parammodules):
        for i_idx, (midx, m_id, tidx, t) in enumerate(points):
            paramellipse = XslotEllipseModuleButton(self, module_uniqueid=m_id,
                                                    text=hand + "." + moduletypeabbrev + str(midx + 1),
                                                    moduletype=moduletype,
                                                    sign=self.sign)
            paramabbrev = parammodules[m_id].getabbreviation()
            paramellipse.setToolTip(paramabbrev)
            pointsalreadydone = [t for (mi, m, ti, t) in points[:i_idx]]
            anyequivalent = [t.startpoint.equivalent(prev_t.startpoint) for prev_t in pointsalreadydone]
            if True in anyequivalent:
                self.current_y += 1
            paramellipse.setRect(*self.getxywh(t))  # how big is it / where does it go?
            self.moduleitems.append(paramellipse)
        self.current_y += 1
    #
    # def addlocation(self, hand):
    #     # TODO KV implement spacing efficiency - for now put intervals on one row and points on another
    #     num_locnmods = len(self.sign.locationmodules)
    #     if num_locnmods > 0:
    #         if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
    #             # everything just gets listed vertically
    #             for idx, m in enumerate(self.sign.locationmodules.keys()):
    #                 locnmod = self.sign.locationmodules[m]
    #                 locnmodid = locnmod.uniqueid
    #                 if locnmod.hands[hand]:
    #                     locnrect = XslotRectModuleButton(self, module_uniqueid=locnmodid, text=hand+".Loc"+str(idx+1), moduletype='location', sign=self.sign)
    #                     locnabbrev = m.getabbreviation()
    #                     locnrect.setToolTip(locnabbrev)
    #                     locnrect.setRect(self.current_x, self.current_y * (self.default_xslot_height + self.verticalspacing), self.xslots_width, self.default_xslot_height)
    #                     self.current_y += 1
    #                     self.scene.addItem(locnrect)
    #         else:  # 'manual' or 'auto'
    #             # associate modules with x-slots
    #             intervals = []
    #             points = []
    #
    #             for midx, m_id in enumerate(self.sign.locationmodules.keys()):
    #                 locnmod = self.sign.locationmodules[m_id]
    #                 # locnmodid = locnmod.uniqueid
    #                 if locnmod.hands[hand]:
    #                     for tidx, t in enumerate(locnmod.timingintervals):
    #                         if t.ispoint():
    #                             points.append((midx, m_id, tidx, t))
    #                         else:
    #                             intervals.append((midx, m_id, tidx, t))
    #
    #             self.addlocationintervals(hand, intervals)
    #             self.addlocationpoints(hand, points)
    #
    # def addlocationintervals(self, hand, intervals):
    #     for i_idx, (midx, m_id, tidx, t) in enumerate(intervals):
    #         locnrect = XslotRectModuleButton(self, module_uniqueid=m_id,
    #                                          text=hand + ".Loc" + str(midx + 1),
    #                                          moduletype='location',
    #                                          sign=self.sign)
    #         locnabbrev = self.sign.locationmodules[m_id].getabbreviation()
    #         locnrect.setToolTip(locnabbrev)
    #         intervalsalreadydone = [t for (mi, m, ti, t) in intervals[:i_idx]]
    #         anyoverlaps = [t.overlapsinterval(prev_t) for prev_t in intervalsalreadydone]
    #         if True in anyoverlaps:
    #             self.current_y += 1
    #         locnrect.setRect(*self.getxywh(t))  # how big is it / where does it go?
    #         self.moduleitems.append(locnrect)
    #     self.current_y += 1
    #
    # def addlocationpoints(self, hand, points):
    #     for i_idx, (midx, m_id, tidx, t) in enumerate(points):
    #         locnellipse = XslotEllipseModuleButton(self, module_uniqueid=m_id,
    #                                                text=hand + ".Loc" + str(midx + 1),
    #                                                moduletype='location',
    #                                                sign=self.sign)
    #         locnabbrev = self.sign.locationmodules[m_id].getabbreviation()
    #         locnellipse.setToolTip(locnabbrev)
    #         pointsalreadydone = [t for (mi, m, ti, t) in points[:i_idx]]
    #         anyequivalent = [t.startpoint.equivalent(prev_t.startpoint) for prev_t in pointsalreadydone]
    #         if True in anyequivalent:
    #             self.current_y += 1
    #         locnellipse.setRect(*self.getxywh(t))  # how big is it / where does it go?
    #         self.moduleitems.append(locnellipse)
    #     self.current_y += 1

    def addcontact(self, hand):
        return  # TODO KV implement

    def addorientation(self, hand):
        return  # TODO KV implement

    # TODO KV can this functionality be shared between modules? eg addhandconfig & addmovement have a *lot* of overlap
    def addhandconfig(self, hand):
        # TODO KV implement spacing efficiency - for now put intervals on one row and points on another
        num_hcfgmods = len(self.sign.handconfigmodules)
        if num_hcfgmods > 0:
            if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # everything just gets listed vertically
                for idx, m in enumerate(self.sign.handconfigmodules.keys()):
                    hcfgmod = self.sign.handconfigmodules[m]
                    hcfgmodid = hcfgmod.uniqueid
                    if hcfgmod.hands[hand]:
                        hcfgrect = XslotRectModuleButton(self, module_uniqueid=hcfgmodid, text=hand+".Config"+str(idx+1), moduletype='handconfig', sign=self.sign)
                        hcfgabbrev = m.getabbreviation()
                        hcfgrect.setToolTip(hcfgabbrev)
                        hcfgrect.setRect(self.current_x, self.current_y * (self.default_xslot_height + self.verticalspacing), self.xslots_width, self.default_xslot_height)
                        self.current_y += 1
                        self.scene.addItem(hcfgrect)
            else:  # 'manual' or 'auto'
                # associate modules with x-slots
                intervals = []
                points = []

                for midx, m_id in enumerate(self.sign.handconfigmodules.keys()):
                    hcfgmod = self.sign.handconfigmodules[m_id]
                    # hcfgmodid = hcfgmod.uniqueid
                    if hcfgmod.hands[hand]:
                        for tidx, t in enumerate(hcfgmod.timingintervals):
                            if t.ispoint():
                                points.append((midx, m_id, tidx, t))
                            else:
                                intervals.append((midx, m_id, tidx, t))

                self.addhandconfigintervals(hand, intervals)
                self.addhandconfigpoints(hand, points)

    def addhandconfigintervals(self, hand, intervals):
        for i_idx, (midx, m_id, tidx, t) in enumerate(intervals):
            hcfgrect = XslotRectModuleButton(self, module_uniqueid=m_id,
                                             text=hand + ".Config" + str(midx + 1),
                                             moduletype='handconfig',
                                             sign=self.sign)
            hcfgabbrev = self.sign.handconfigmodules[m_id].getabbreviation()
            hcfgrect.setToolTip(hcfgabbrev)
            intervalsalreadydone = [t for (mi, m, ti, t) in intervals[:i_idx]]
            anyoverlaps = [t.overlapsinterval(prev_t) for prev_t in intervalsalreadydone]
            if True in anyoverlaps:
                self.current_y += 1
            hcfgrect.setRect(*self.getxywh(t))  # how big is it / where does it go?
            self.moduleitems.append(hcfgrect)
        self.current_y += 1

    def addhandconfigpoints(self, hand, points):
        for i_idx, (midx, m_id, tidx, t) in enumerate(points):
            hcfgellipse = XslotEllipseModuleButton(self, module_uniqueid=m_id,
                                                   text=hand + ".Config" + str(midx + 1),
                                                   moduletype='handconfig',
                                                   sign=self.sign)
            hcfgabbrev = self.sign.handconfigmodules[m_id].getabbreviation()
            hcfgellipse.setToolTip(hcfgabbrev)
            pointsalreadydone = [t for (mi, m, ti, t) in points[:i_idx]]
            anyequivalent = [t.startpoint.equivalent(prev_t.startpoint) for prev_t in pointsalreadydone]
            if True in anyequivalent:
                self.current_y += 1
            hcfgellipse.setRect(*self.getxywh(t))  # how big is it / where does it go?
            self.moduleitems.append(hcfgellipse)
        self.current_y += 1

    def addgridlines(self):
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none' and len(self.moduleitems) > 0:

            pen = QPen(Qt.lightGray)
            pen.setWidth(5)
            pen.setStyle(Qt.DashLine)

            whole_xslots = self.sign.xslotstructure.number
            partial_xslot = self.sign.xslotstructure.additionalfraction

            partialxslots = self.mainwindow.app_settings['signdefaults']['partial_xslots']
            avail_denoms = [Fraction(f).denominator for f in list(partialxslots.keys()) if partialxslots[f]]
            fractionalpoints = []
            for d in avail_denoms:
                for mult in range(d + 1):
                    fractionalpoints.append(Fraction(mult, d))
            fractionalpoints = list(set(fractionalpoints))
            # self.xslot_width = self.scene_width / (self.numwholes + (1 if self.additionalfrac > 0 else 0))

            for whole in range(0, whole_xslots+1):
                for frac in fractionalpoints:
                    curvalue = whole + frac
                    totalvalue = whole_xslots + partial_xslot
                    if curvalue <= totalvalue:
                        xstart = self.x_offset + self.indent + float((whole+frac)*self.onexslot_width)
                        self.scene.addLine(xstart, self.gridlinestart, xstart, self.current_y * (self.default_xslot_height + self.verticalspacing), pen)
            for item in self.moduleitems:
                self.scene.addItem(item)

    def handle_modulebutton_clicked(self, modulebutton):
        # TODO KV
        moduletype = modulebutton.moduletype
        if moduletype == "signtype":
            self.handle_signtype_clicked()
        # elif moduletype == "xslot":
        #     self.handle_xslot_clicked()
        else:
            modulekey = modulebutton.module_uniqueid
            if moduletype == "movement":
                self.handle_movement_clicked(modulekey)
            elif moduletype == 'handconfig':
                self.handle_handconfig_clicked(modulekey)
            elif moduletype == 'location':
                self.handle_location_clicked(modulekey)

    def handle_xslot_clicked(self):
        # TODO KV - open xslot editing window
        pass

    def handle_signtype_clicked(self):
        signtypedialog = SigntypeSelectorDialog(self.mainwindow.current_sign.signtype, mainwindow=self.mainwindow)
        signtypedialog.saved_signtype.connect(self.handle_save_signtype)
        signtypedialog.exec_()

    def handle_save_signtype(self, signtype):
        self.sign.signtype = signtype
        self.refreshsign()  # self.sign)

    def handle_movement_clicked(self, modulekey):
        mvmtmodule = self.sign.movementmodules[modulekey]
        movementtreemodel = mvmtmodule.movementtreemodel
        movement_selector = ModuleSelectorDialog(mainwindow=self.mainwindow,
                                                 hands=mvmtmodule.hands,
                                                 xslotstructure=self.sign.xslotstructure,
                                                 enable_addnew=False,
                                                 modulelayout=MovementSpecificationLayout(movementtreemodel),
                                                 moduleargs=None,
                                                 timingintervals=mvmtmodule.timingintervals,
                                                 includephase=True,
                                                 inphase=mvmtmodule.inphase)
        movement_selector.get_savedmodule_signal().connect(
            lambda movementtree, hands, timingintervals, inphase: self.mainwindow.sign_summary.handle_save_movement(movementtree, hands, timingintervals, inphase, modulekey))
        movement_selector.exec_()

    def handle_location_clicked(self, modulekey):
        locnmodule = self.sign.locationmodules[modulekey]
        locationtreemodel = locnmodule.locationtreemodel
        location_selector = ModuleSelectorDialog(mainwindow=self.mainwindow,
                                                 hands=locnmodule.hands,
                                                 xslotstructure=self.sign.xslotstructure,
                                                 enable_addnew=False,
                                                 modulelayout=LocationSpecificationLayout2(self.mainwindow, locationtreemodel),
                                                 moduleargs=None,
                                                 timingintervals=locnmodule.timingintervals)
        location_selector.get_savedmodule_signal().connect(
            lambda locationtree, majorphonloc, minorphonloc, hands, timingintervals, inphase: self.mainwindow.sign_summary.handle_save_location(locationtree, hands, timingintervals, majorphonloc, minorphonloc, modulekey))
        location_selector.exec_()

    def handle_handconfig_clicked(self, modulekey):
        hcfgmodule = self.sign.handconfigmodules[modulekey]
        handconfiguration = hcfgmodule.handconfiguration
        overalloptions = hcfgmodule.overalloptions
        handcfg_selector = ModuleSelectorDialog(mainwindow=self.mainwindow,
                                                hands=hcfgmodule.hands,
                                                xslotstructure=self.sign.xslotstructure,
                                                enable_addnew=False,
                                                modulelayout=HandConfigSpecificationLayout(self.mainwindow, hcfgmodule),  # (handconfiguration, overalloptions)),
                                                moduleargs=None,
                                                timingintervals=hcfgmodule.timingintervals)
        handcfg_selector.get_savedmodule_signal().connect(
            lambda configdict, hands, timingintervals, inphase: self.mainwindow.sign_summary.handle_save_handconfig(configdict, hands, timingintervals, modulekey))
        handcfg_selector.exec_()

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

        self.handpart_button = QPushButton("Hand part selection")
        self.handpart_button.setProperty("existingmodule", False)
        self.handpart_button.clicked.connect(self.handle_handpartbutton_click)
        self.module_buttons.append(self.handpart_button)

        self.location_button = QPushButton("Location selection")
        self.location_button.clicked.connect(self.handle_locationbutton_click)
        self.module_buttons.append(self.location_button)

        self.contact_button = QPushButton("Contact selection")
        self.contact_button.clicked.connect(self.handle_contactbutton_click)
        self.module_buttons.append(self.contact_button)

        self.orientation_button = QPushButton("Orientation selection")
        self.orientation_button.clicked.connect(self.handle_orientationbutton_click)
        self.module_buttons.append(self.orientation_button)

        self.handshape_button = QPushButton("Hand configuration selection")
        self.handshape_button.setProperty("existingmodule", False)
        self.handshape_button.clicked.connect(self.handle_handshapebutton_click)
        self.module_buttons.append(self.handshape_button)

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
        parametermodulebuttonseligible = self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none' or (self.sign is not None and self.sign.specifiedxslots)
        enableparametermodulebuttons = yesorno and parametermodulebuttonseligible
        enablexslotbutton = yesorno and self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'manual'
        enablesigntypebutton = yesorno and self.sign is not None

        for btn in self.module_buttons:
            btn.setEnabled(enableparametermodulebuttons)
        self.signtype_button.setEnabled(enablesigntypebutton)
        self.xslots_button.setEnabled(enablexslotbutton)

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
        self.sign.specifiedxslots = True
        self.enable_module_buttons(True)
        self.sign_updated.emit(self.sign)

    def handle_signlevelbutton_click(self):
        signlevelinfo_selector = SignlevelinfoSelectorDialog(self.sign.signlevel_information if self.sign else None, self.mainwindow, parent=self)
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
            self.mainwindow.corpus.add_sign(self.sign)
            self.mainwindow.handle_sign_selected(self.sign)

        self.sign_updated.emit(self.sign)
        # self.mainwindow.corpus_view.updated_glosses(self.mainwindow.corpus.get_sign_glosses(), self.sign.signlevel_information.gloss)
        self.mainwindow.corpus_view.updated_signs(self.mainwindow.corpus.signs, self.sign)

    def handle_signtypebutton_click(self):
        signtype_selector = SigntypeSelectorDialog(self.sign.signtype, self.mainwindow, parent=self)
        signtype_selector.saved_signtype.connect(self.handle_save_signtype)
        signtype_selector.exec_()

    def handle_save_signtype(self, signtype):
        self.sign.signtype = signtype
        self.sign_updated.emit(self.sign)

    def handle_movementbutton_click(self):
        movement_selector = ModuleSelectorDialog(mainwindow=self.mainwindow,
                                                 hands=None,
                                                 xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                                 enable_addnew=True,
                                                 modulelayout=MovementSpecificationLayout(),
                                                 moduleargs=None,
                                                 includephase=True,
                                                 inphase=None)
        movement_selector.get_savedmodule_signal().connect(lambda movementtree, hands, timingintervals, inphase: self.handle_save_movement(movementtree, hands, timingintervals, inphase))
        movement_selector.exec_()

    def handle_save_movement(self, movementtree, hands_dict, timingintervals, inphase, existing_key=None):
        if existing_key is None or existing_key not in self.sign.movementmodules.keys():
            self.sign.addmovementmodule(movementtree, hands_dict, timingintervals, inphase)
        else:
            # self.sign.movementmodules[existing_key] = movementtree
            self.sign.updatemovementmodule(existing_key, movementtree, hands_dict, timingintervals, inphase)
        self.sign_updated.emit(self.sign)

    def handle_handshapebutton_click(self):
        handcfg_selector = ModuleSelectorDialog(mainwindow=self.mainwindow,
                                                hands=None,
                                                xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                                enable_addnew=True,
                                                modulelayout=HandConfigSpecificationLayout(self.mainwindow),
                                                moduleargs=None)
        handcfg_selector.get_savedmodule_signal().connect(lambda configdict, hands, timingintervals, inphase: self.handle_save_handconfig(configdict, hands, timingintervals))
        handcfg_selector.exec_()
        #
        # button = self.sender()
        # # TODO KV
        # editing_existing = button.property("existingmodule")
        # existing_key = None
        # moduletoload = None
        # if editing_existing:
        #     existing_key = button.text()
        #     moduletoload = self.sign.handshapemodules[existing_key]
        # # handshape_selector = HandshapeSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload, parent=self)
        # handshape_selector = ModuleSelectorDialog(mainwindow=self.mainwindow, hands=None, xslotstructure=self.mainwindow.current_sign.xslotstructure, enable_addnew=(not editing_existing), modulelayout=HandshapeSpecificationLayout(self.mainwindow, moduletoload), moduleargs=None)
        # handshape_selector.get_savedmodule_signal().connect(lambda hs_global, hs_transcription, hands: self.handle_save_handshape(GlobalHandshapeInformation(hs_global.get_value()), hs_transcription, hands, existing_key))
        # handshape_selector.exec_()

    def handle_save_handconfig(self, configdict, hands_dict, timingintervals, existing_key=None):
        handconfiguration = configdict['hand']
        overalloptions = {k: v for (k, v) in configdict.items() if k != 'hand'}
        if existing_key is None or existing_key not in self.sign.handconfigmodules.keys():
            self.sign.addhandconfigmodule(handconfiguration, overalloptions, hands_dict, timingintervals)
        else:
            self.sign.updatehandconfigmodule(existing_key, handconfiguration, overalloptions, hands_dict, timingintervals)
        self.sign_updated.emit(self.sign)

    def handle_contactbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Contact module functionality not yet linked.')

    def handle_handpartbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Contact module functionality not yet linked.')

    def handle_orientationbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Orientation module functionality not yet linked.')

    def handle_locationbutton_click(self):
        location_selector = ModuleSelectorDialog(mainwindow=self.mainwindow,
                                                 hands=None,
                                                 xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                                 enable_addnew=True,
                                                 modulelayout=LocationSpecificationLayout2(self.mainwindow),
                                                 moduleargs=None)
        location_selector.get_savedmodule_signal().connect(lambda locationtree, majorphonloc, minorphonloc, hands, timingintervals, inphase: self.handle_save_location(locationtree, hands, timingintervals, majorphonloc, minorphonloc))
        location_selector.exec_()

    def handle_save_location(self, locationtree, hands_dict, timingintervals, majorphonloc=False, minorphonloc=False, existing_key=None):
        if existing_key is None or existing_key not in self.sign.locationmodules.keys():
            self.sign.addlocationmodule(locationtree, hands_dict, timingintervals, majorphonloc, minorphonloc)
        else:
            # self.sign.locationmodules[existing_key] = locationtree
            self.sign.updatelocationmodule(existing_key, locationtree, hands_dict, timingintervals, majorphonloc, minorphonloc)
        self.sign_updated.emit(self.sign)

    def handle_handpartbutton_click(self):
        # TODO KV
        QMessageBox.information(self, 'Not Available', 'Hand part module functionality not yet linked.')

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

