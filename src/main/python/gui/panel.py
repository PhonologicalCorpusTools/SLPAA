from fractions import Fraction
from itertools import permutations
from collections import defaultdict
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPoint,
    pyqtSignal,
    QSettings
)

from PyQt5.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QCheckBox,
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QGraphicsEllipseItem,
    QGraphicsTextItem,
    QGroupBox,
    QPushButton,
    QColorDialog,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QMenu,
    QAction,
    QMessageBox
)

from PyQt5.QtGui import (
    QPixmap,
    QColor,
    QPen,
    QBrush,
    QPolygonF,
)

# from gui.hand_configuration import ConfigGlobal, Config
from gui.signtypespecification_view import SigntypeSelectorDialog
from gui.signlevelinfospecification_view import SignlevelinfoSelectorDialog
from gui.helper_widget import CollapsibleSection, ToggleSwitch
from constant import DEFAULT_LOCATION_POINTS, HAND, ARM, LEG, ARTICULATOR_ABBREVS
from gui.xslotspecification_view import XslotSelectorDialog
from lexicon.module_classes import TimingPoint, TimingInterval, ModuleTypes
from lexicon.lexicon_classes import Sign
from gui.modulespecification_dialog import ModuleSelectorDialog
from gui.xslot_graphics import XslotRect, XslotRectModuleButton, SignSummaryScene, XslotEllipseModuleButton


# TODO KV there are two classes with this name-- are they exactly the same?
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


class SignSummaryPanel(QScrollArea):

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
        self.scene = SignSummaryScene()
        self.scene.modulerect_clicked.connect(self.handle_summarymodulebtn_clicked)
        self.scene.moduleellipse_clicked.connect(self.handle_summarymodulebtn_clicked)

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
        self.xslotview = QGraphicsView(self.scene)
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
            if self.mainwindow.current_sign is not None:
                self.sign = self.mainwindow.current_sign

            self.relmodnums = self.sign.getmodulenumbersdict(ModuleTypes.RELATION)
            self.relmods_hands_arms = []
            self.relmods_other = []
            for rmod in self.sign.getmoduledict(ModuleTypes.RELATION).values():
                if rmod.usesarticulator(HAND) or rmod.usesarticulator(ARM):
                    self.relmods_hands_arms.append(rmod)
                else:
                    self.relmods_other.append(rmod)

        for sceneitem in self.scene.items():
            self.scene.removeItem(sceneitem)

        self.moduleitems = []
        self.current_y = 0

        # set the top text, either welcome or the sign gloss + ID
        signleveltext = QGraphicsTextItem()
        signleveltext.setPlainText("Welcome! Add a new sign to get started.")
        if self.sign is not None:
            signleveltext.setPlainText(" / ".join(self.sign.signlevel_information.gloss)
                                       + " - " + self.sign.signlevel_information.entryid.display_string())
        signleveltext.setPos(self.x_offset, self.current_y)
        self.current_y += 30
        self.scene.addItem(signleveltext)

        if self.sign is None:
            return

        self.addsigntype()
        self.addxslots()
        self.addhand(1)
        self.addhand(2)
        self.addnonhand()
        self.addgridlines()

    def addsigntype(self):
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
            signtyperect.setRect(self.x_offset + self.indent, self.current_y, self.xslots_width,
                                 self.default_xslot_height)
            self.scene.addItem(signtyperect)

    def addxslots(self):
        xslotrects = {}
        numwholes = self.sign.xslotstructure.number
        partial = float(self.sign.xslotstructure.additionalfraction)
        roundedup = numwholes + (1 if partial > 0 else 0)
        self.onexslot_width = self.xslots_width / roundedup

        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none' and self.sign.xslotstructure is not None and self.sign.specifiedxslots:
            self.current_y += self.default_xslot_height + self.verticalspacing
            if numwholes + partial > 0:
                for i in range(numwholes):
                    xslotrect = XslotRect(self, text="x" + str(i + 1), moduletype='xslot', sign=self.sign)
                    xloc = self.indent + i * self.onexslot_width  # - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, self.current_y, self.onexslot_width, self.default_xslot_height)
                    xslotrects["x"+str(i+1)] = xslotrect
                    self.scene.addItem(xslotrect)
                if partial > 0:
                    xslotrect = XslotRect(self, text="x" + str(numwholes + 1), moduletype='xslot', sign=self.sign, proportionfill=partial)
                    xloc = self.indent + numwholes * self.onexslot_width #  - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, self.current_y, self.onexslot_width, self.default_xslot_height)
                    xslotrects["x"+str(numwholes+1)] = xslotrect
                    self.scene.addItem(xslotrect)
            self.gridlinestart = self.current_y + self.default_xslot_height + self.verticalspacing

    def addnonhand(self):
        # add "other" label
        othertext = QGraphicsTextItem()
        othertext.setPlainText("Other")
        self.current_y += self.default_xslot_height * 1.5
        othertext.setPos(self.x_offset, self.current_y)
        self.scene.addItem(othertext)

        for mtype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION, ModuleTypes.HANDCONFIG, ModuleTypes.ORIENTATION]:
            self.addmodules_other(moduletype=mtype)
        self.addnonmanual()

    def addhand(self, articulatornum):
        # add hand label
        handtext = QGraphicsTextItem()
        handtext.setPlainText(HAND + " " + str(articulatornum))
        self.current_y += self.default_xslot_height * 1.5
        handtext.setPos(self.x_offset, self.current_y)
        self.scene.addItem(handtext)

        for mtype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION, ModuleTypes.HANDCONFIG, ModuleTypes.ORIENTATION]:
            self.addmodules_hands_arms(artnum=articulatornum, moduletype=mtype)

    def getxywh(self, timinginterval):
        if timinginterval is None:
            # x-slots aren't a thing; plan a rectangle whose width doesn't mean anything, timing-wise
            # the rectangle will be for the whole sign (treat it like a whole-sign x-slot)
            startfrac = 0
            endfrac = self.sign.xslotstructure.number + self.sign.xslotstructure.additionalfraction
            widthfrac = endfrac - startfrac

            x = self.x_offset + self.indent + float(startfrac)*self.onexslot_width
            y = self.current_y
            w = float(widthfrac) * self.onexslot_width
            h = self.default_xslot_height
        elif timinginterval.ispoint():
            # it's a point; plan an ellipse
            yradius = 40
            pointfrac = timinginterval.startpoint.wholepart - 1 + timinginterval.startpoint.fractionalpart
            x = self.x_offset + self.indent + float(pointfrac)*self.onexslot_width - yradius
            y = self.current_y
            w = 2 * yradius
            h = self.default_xslot_height
        elif not timinginterval.ispoint():
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
            y = self.current_y
            w = float(widthfrac) * self.onexslot_width
            h = self.default_xslot_height

        return x, y, w, h

    def addnonmanual(self):
        return  # TODO KV implement

    def addmodules_other(self, moduletype):  # artnum,
        # TODO KV implement spacing efficiency - for now put intervals on one row and points on another
        if moduletype == ModuleTypes.RELATION:
            modules = self.relmods_other
        else:
            modules = [mod for mod in self.sign.getmoduledict(moduletype).values() if
                       mod.articulators is not None and
                       (mod.articulators[0] == LEG and True in mod.articulators[1].values())]
        modulenumbers = self.sign.getmodulenumbersdict(moduletype)
        moduletypeabbrev = ModuleTypes.abbreviations[moduletype]

        mods_count = len(modules)
        if mods_count > 0:
            if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # everything just gets listed vertically

                for mod in modules:
                    m_id = mod.uniqueid
                    self.current_y += self.default_xslot_height + self.verticalspacing
                    paramrect = XslotRectModuleButton(self, module_uniqueid=m_id,
                                                      text=moduletypeabbrev + str(modulenumbers[m_id]),
                                                      moduletype=moduletype,
                                                      sign=self.sign)
                    paramabbrev = mod.getabbreviation()
                    paramrect.setToolTip(paramabbrev)
                    paramrect.setRect(*self.getxywh(None))  # how big is it / where does it go?
                    self.moduleitems.append(paramrect)
                    self.scene.addItem(paramrect)
            else:  # 'manual' or 'auto'
                # associate modules with x-slots
                intervals = []
                points = []

                for mod in modules:
                    m_id = mod.uniqueid
                    condensed_timingintervals = self.condense_timingintervals(mod.timingintervals)
                    for t in condensed_timingintervals:
                        if t.ispoint():
                            points.append((modulenumbers[m_id], m_id, t))
                        else:
                            intervals.append((modulenumbers[m_id], m_id, t))

                if len(intervals) > 0:
                    self.addmoduleintervals(None, None, intervals, moduletype, moduletypeabbrev, modules)
                if len(points) > 0:
                    self.addmodulepoints(None, None, points, moduletype, moduletypeabbrev, modules)
            self.assign_hover_partners()

    def addmodules_hands_arms(self, artnum, moduletype):
        isrel = moduletype == ModuleTypes.RELATION
        # TODO KV implement spacing efficiency - for now put intervals on one row and points on another
        if isrel:
            modules = [mod for mod in self.relmods_hands_arms if
                       mod.usesarticulator(HAND, artnum) or mod.usesarticulator(ARM, artnum)]
        else:
            modules = [mod for mod in self.sign.getmoduledict(moduletype).values() if
                       mod.articulators is not None and
                       (mod.articulators[0] in [HAND, ARM] and mod.articulators[1][artnum])]
        modulenumbers = self.sign.getmodulenumbersdict(moduletype)
        moduletypeabbrev = ModuleTypes.abbreviations[moduletype]

        mods_count = len(modules)
        if mods_count > 0:
            if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none':
                # everything just gets listed vertically

                for mod in modules:
                    m_id = mod.uniqueid
                    self.current_y += self.default_xslot_height + self.verticalspacing
                    if isrel:
                        if mod.usesarticulator(HAND, artnum):
                            articulator = HAND
                            articulator_dict = mod.hands_in_use()
                        elif mod.usesarticulator(ARM, artnum):
                            articulator = ARM
                            articulator_dict = mod.arms_in_use()
                    else:
                        articulator = mod.articulators[0]
                        articulator_dict = mod.articulators[1]

                    if articulator_dict[artnum]:
                        paramrect = XslotRectModuleButton(self, module_uniqueid=m_id,  # parammodid,
                                                          text=ARTICULATOR_ABBREVS[articulator] + str(artnum) + "." + moduletypeabbrev + str(modulenumbers[m_id]), moduletype=moduletype,
                                                          sign=self.sign)
                        paramabbrev = mod.getabbreviation()
                        paramrect.setToolTip(paramabbrev)
                        paramrect.setRect(*self.getxywh(None))  # how big is it / where does it go?
                        self.moduleitems.append(paramrect)
                        self.scene.addItem(paramrect)
            else:  # 'manual' or 'auto'
                # associate modules with x-slots
                intervals = {}
                points = {}

                for mod in modules:
                    m_id = mod.uniqueid
                    if isrel:
                        if mod.usesarticulator(HAND, artnum):
                            articulator = HAND
                            articulator_dict = mod.hands_in_use()
                        elif mod.usesarticulator(ARM, artnum):
                            articulator = ARM
                            articulator_dict = mod.arms_in_use()
                    else:
                        articulator = mod.articulators[0]
                        articulator_dict = mod.articulators[1]

                    if articulator_dict[artnum]:
                        condensed_timingintervals = self.condense_timingintervals(mod.timingintervals)
                        for t in condensed_timingintervals:
                            if t.ispoint():
                                if articulator not in points.keys():
                                    points[articulator] = []
                                points[articulator].append((modulenumbers[m_id], m_id, t))
                            else:
                                if articulator not in intervals.keys():
                                    intervals[articulator] = []
                                intervals[articulator].append((modulenumbers[m_id], m_id, t))

                for articulator in [HAND, ARM]:  # , LEG]:
                    if articulator in intervals and len(intervals[articulator]) > 0:
                        self.addmoduleintervals(articulator, artnum, intervals[articulator], moduletype, moduletypeabbrev, modules)
                    if articulator in points and len(points[articulator]) > 0:
                        self.addmodulepoints(articulator, artnum, points[articulator], moduletype, moduletypeabbrev, modules)
            self.assign_hover_partners()

    def condense_timingintervals(self, intervals):
        condensed_intervals = []
        # add one at a time
        for tint in intervals:
            self.add_timinginterval_tocondensed(tint, condensed_intervals)
        return condensed_intervals

    def add_timinginterval_tocondensed(self, timinginterval, condensed_intervals):
        # TODO KV - look for possible simplifications
        if timinginterval.ispoint():
            # the one we're adding is a point; don't condense it with anything
            condensed_intervals.append(timinginterval)
        else:
            # the one we're adding is an interval; see if there's another interval(s) to combine it with
            needtocombine = False
            idx = 0
            while not needtocombine and idx < len(condensed_intervals):
                existinginterval = condensed_intervals[idx]
                if existinginterval.ispoint():
                    # skip this one; we don't condense points with anything
                    pass
                elif existinginterval.endpoint.equivalent(timinginterval.startpoint):
                    # the new interval starts right where the existing one ends; combine them and re-add
                    # (in case there's another interval that the newly-combined one would also link up with)
                    needtocombine = True
                    condensed_intervals.remove(existinginterval)
                    self.add_timinginterval_tocondensed(TimingInterval(existinginterval.startpoint, timinginterval.endpoint), condensed_intervals)
                elif existinginterval.startpoint.equivalent(timinginterval.endpoint):
                    # the existing interval starts right where the new one ends; combine them and re-add
                    # (in case there's another interval that the newly-combined one would also link up with)
                    needtocombine = True
                    condensed_intervals.remove(existinginterval)
                    self.add_timinginterval_tocondensed(TimingInterval(timinginterval.startpoint, existinginterval.endpoint), condensed_intervals)
                idx += 1
            if not needtocombine:
                condensed_intervals.append(timinginterval)

        return condensed_intervals

    def addmoduleintervals(self, articulator, artnum, intervals, moduletype, moduletypeabbrev, modules):
        if len(intervals) > 0:
            self.current_y += self.default_xslot_height + self.verticalspacing
        for i_idx, (modnum, m_id, t) in enumerate(intervals):
            paramrect = XslotRectModuleButton(self, module_uniqueid=m_id,
                                              text=((ARTICULATOR_ABBREVS[articulator] + str(artnum) + ".") if articulator is not None else "") + moduletypeabbrev + str(modnum),
                                              moduletype=moduletype,
                                              sign=self.sign)
            paramabbrev = [mod for mod in modules if mod.uniqueid == m_id][0].getabbreviation()
            paramrect.setToolTip(paramabbrev)
            intervalsalreadydone = [t for (mn, m, t) in intervals[:i_idx]]
            anyoverlaps = [t.overlapsinterval(prev_t) for prev_t in intervalsalreadydone]
            if True in anyoverlaps:
                self.current_y += self.default_xslot_height + self.verticalspacing
            paramrect.setRect(*self.getxywh(t))  # how big is it / where does it go?
            self.moduleitems.append(paramrect)

    # I don't know that I'm a big fan of having every single module button know about every other module button
    # from the same module instance, but at this point it seemed the most effective way to sync the hover behaviour
    def assign_hover_partners(self):
        for modbtn in self.moduleitems:
            hoverpartners_same = [b for b in self.moduleitems if b != modbtn and b.module_uniqueid == modbtn.module_uniqueid]
            hoverpartners_associated = []
            for b in self.moduleitems:
                if b != modbtn:
                    if b.moduletype == ModuleTypes.RELATION and modbtn.moduletype in [ModuleTypes.LOCATION, ModuleTypes.MOVEMENT]:
                        relmod = self.sign.getmoduledict(ModuleTypes.RELATION)[b.module_uniqueid]
                        if relmod.relationy.existingmodule and modbtn.module_uniqueid in relmod.relationy.linkedmoduleids:
                            hoverpartners_associated.append(b)
                    elif modbtn.moduletype == ModuleTypes.RELATION and b.moduletype in [ModuleTypes.LOCATION, ModuleTypes.MOVEMENT]:
                        relmod = self.sign.getmoduledict(ModuleTypes.RELATION)[modbtn.module_uniqueid]
                        if relmod.relationy.existingmodule and b.module_uniqueid in relmod.relationy.linkedmoduleids:
                            hoverpartners_associated.append(b)

            modbtn.samemodule_buttons = hoverpartners_same
            modbtn.associatedmodule_buttons = hoverpartners_associated

    def remove_dotandprefix(self, text):
        modifiedtext = text
        if "." in text:
            dotindex = text.index(".")
            modifiedtext = text[dotindex+1:]
        return modifiedtext

    def addmodulepoints(self, articulator, artnum, points, moduletype, moduletypeabbrev, modules):
        if len(points) > 0:
            self.current_y += self.default_xslot_height + self.verticalspacing

        for i_idx, (modnum, m_id, t) in enumerate(points):
            paramellipse = XslotEllipseModuleButton(self, module_uniqueid=m_id,
                                                    text=((ARTICULATOR_ABBREVS[articulator] + str(artnum) + ".") if articulator is not None else "") + moduletypeabbrev + str(modnum),
                                                    moduletype=moduletype,
                                                    sign=self.sign)
            paramabbrev = [mod for mod in modules if mod.uniqueid == m_id][0].getabbreviation()
            paramellipse.setToolTip(paramabbrev)
            pointsalreadydone = [t for (mn, m, t) in points[:i_idx]]
            anyequivalent = [t.startpoint.equivalent(prev_t.startpoint) for prev_t in pointsalreadydone]
            if True in anyequivalent:
                self.current_y += self.default_xslot_height + self.verticalspacing
            paramellipse.setRect(*self.getxywh(t))  # how big is it / where does it go?
            self.moduleitems.append(paramellipse)

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

            for whole in range(0, whole_xslots+1):
                for frac in fractionalpoints:
                    curvalue = whole + frac
                    totalvalue = whole_xslots + partial_xslot
                    if curvalue <= totalvalue:
                        xstart = self.x_offset + self.indent + float((whole+frac)*self.onexslot_width)
                        self.scene.addLine(xstart, self.gridlinestart, xstart, self.current_y + self.default_xslot_height + self.verticalspacing, pen)
            for item in self.moduleitems:
                self.scene.addItem(item)

    def handle_summarymodulebtn_clicked(self, modulebutton):
        # TODO KV
        moduletype = modulebutton.moduletype
        if moduletype == 'signtype':
            self.handle_signtype_clicked()
        # elif moduletype == "xslot":
        #     self.handle_xslot_clicked()
        else:
            modulekey = modulebutton.module_uniqueid
            self.open_module_dialog(modulekey, moduletype)

    def handle_xslot_clicked(self):
        # TODO KV - open xslot editing window
        pass

    def handle_signtype_clicked(self):
        signtypedialog = SigntypeSelectorDialog(self.mainwindow.current_sign.signtype, parent=self)
        signtypedialog.saved_signtype.connect(self.handle_save_signtype)
        signtypedialog.exec_()

    def handle_save_signtype(self, signtype):
        self.sign.signtype = signtype
        self.refreshsign()

    def open_module_dialog(self, modulekey, moduletype):
        modules_list = self.sign.getmoduledict(moduletype)
        module_to_edit = modules_list[modulekey]
        includearticulators = [HAND, ARM, LEG] if moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION] \
            else ([] if moduletype == ModuleTypes.RELATION else [HAND])
        includephase = 2 if moduletype == ModuleTypes.MOVEMENT else (
            1 if moduletype == ModuleTypes.LOCATION else
            0  # default
        )
        module_selector = ModuleSelectorDialog(moduletype=moduletype,
                                               xslotstructure=self.sign.xslotstructure,
                                               moduletoload=module_to_edit,
                                               includephase=includephase,
                                               incl_articulators=includearticulators,
                                               incl_articulator_subopts=includephase,
                                               parent=self
                                               )
        module_selector.module_saved.connect(
            lambda module_to_save, savedtype:
            self.mainwindow.signlevel_panel.handle_save_module(module_to_save=module_to_save,
                                                               moduletype=savedtype,
                                                               existing_key=modulekey)
        )
        module_selector.module_deleted.connect(
            lambda: self.mainwindow.signlevel_panel.handle_delete_module(existingkey=modulekey, moduletype=moduletype)
        )
        module_selector.exec_()


class SignLevelMenuPanel(QScrollArea):
    sign_updated = pyqtSignal(Sign)

    def __init__(self, sign, mainwindow, **kwargs):
        super().__init__(**kwargs)

        self.mainwindow = mainwindow

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        self._sign = sign
        self.modulebuttons_untimed = []
        self.modulebuttons_timed = []

        self.signgloss_label = QLabel("Sign: " + sign.signlevel_information.gloss if sign else "")
        self.signlevel_button = QPushButton("Sign-level information")
        self.signlevel_button.clicked.connect(self.handle_signlevelbutton_click)

        self.signtype_button = QPushButton("Sign type information")
        self.signtype_button.clicked.connect(self.handle_signtypebutton_click)
        self.modulebuttons_untimed.append(self.signtype_button)

        # TODO KV
        # if self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'manual':  # could also be 'none' or 'auto'
        self.xslots_button = QPushButton("X-slot information")
        self.xslots_button.clicked.connect(self.handle_xslotsbutton_click)
        self.modulebuttons_untimed.append(self.xslots_button)

        self.movement_button = QPushButton("Add movement module")
        self.movement_button.setProperty("existingmodule", False)
        self.movement_button.clicked.connect(lambda: self.handle_menumodulebtn_clicked(ModuleTypes.MOVEMENT))
        self.modulebuttons_timed.append(self.movement_button)

        self.location_button = QPushButton("Add location module")
        self.location_button.setProperty("existingmodule", False)
        self.location_button.clicked.connect(lambda: self.handle_menumodulebtn_clicked(ModuleTypes.LOCATION))
        self.modulebuttons_timed.append(self.location_button)

        self.relation_button = QPushButton("Add relation module")
        self.relation_button.setProperty("existingmodule", False)
        self.relation_button.clicked.connect(lambda: self.handle_menumodulebtn_clicked(ModuleTypes.RELATION))
        self.modulebuttons_timed.append(self.relation_button)

        self.orientation_button = QPushButton("Add orientation module")
        self.orientation_button.setProperty("existingmodule", False)
        self.orientation_button.clicked.connect(lambda: self.handle_menumodulebtn_clicked(ModuleTypes.ORIENTATION))
        self.modulebuttons_timed.append(self.orientation_button)

        self.handshape_button = QPushButton("Add hand configuration module")
        self.handshape_button.setProperty("existingmodule", False)
        self.handshape_button.clicked.connect(lambda: self.handle_menumodulebtn_clicked(ModuleTypes.HANDCONFIG))
        self.modulebuttons_timed.append(self.handshape_button)

        self.nonmanual_button = QPushButton("Add non-manual module")
        self.nonmanual_button.setProperty("existingmodule", False)
        self.nonmanual_button.clicked.connect(lambda: self.handle_menumodulebtn_clicked_na(ModuleTypes.NONMANUAL))
        self.modulebuttons_timed.append(self.nonmanual_button)

        main_layout.addWidget(self.signgloss_label)
        main_layout.addWidget(self.signlevel_button)
        for btn in self.modulebuttons_untimed:
            main_layout.addWidget(btn)
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)
        for btn in self.modulebuttons_timed:
            main_layout.addWidget(btn)
        self.enable_module_buttons(False)

        self.setWidget(main_frame)

    def enable_module_buttons(self, yesorno):
        parametermodulebuttonseligible = self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'none' or (self.sign is not None and self.sign.specifiedxslots)
        enableparametermodulebuttons = yesorno and parametermodulebuttonseligible
        enablexslotbutton = yesorno and self.mainwindow.app_settings['signdefaults']['xslot_generation'] == 'manual'
        enablesigntypebutton = yesorno and self.sign is not None

        for btn in self.modulebuttons_untimed + self.modulebuttons_timed:
            btn.setEnabled(enableparametermodulebuttons)
        self.signtype_button.setEnabled(enablesigntypebutton)
        self.xslots_button.setEnabled(enablexslotbutton)

    @property
    def sign(self):
        return self._sign

    @sign.setter
    def sign(self, sign):
        self._sign = sign
        self.signgloss_label.setText("Sign: " + "/".join(sign.signlevel_information.gloss) if sign else "")

    def clear(self):
        self._sign = None
        self.signgloss_label.setText("Sign: ")

    def handle_xslotsbutton_click(self):
        timing_selector = XslotSelectorDialog(self.sign.xslotstructure if self.sign else None, parent=self)
        timing_selector.saved_xslots.connect(self.handle_save_xslots)
        timing_selector.exec_()

    def handle_save_xslots(self, xslots):
        self.sign.xslotstructure = xslots
        self.sign.specifiedxslots = True
        self.enable_module_buttons(True)
        self.sign_updated.emit(self.sign)

    def handle_signlevelbutton_click(self):
        signlevelinfo_selector = SignlevelinfoSelectorDialog(self.sign.signlevel_information if self.sign else None, parent=self)
        signlevelinfo_selector.saved_signlevelinfo.connect(self.handle_save_signlevelinfo)
        dialogresult = signlevelinfo_selector.exec_()
        return dialogresult

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

        self.sign_updated.emit(self.sign)
        self.mainwindow.corpus_display.updated_signs(self.mainwindow.corpus.signs, self.sign)

    def handle_signtypebutton_click(self):
        signtype_selector = SigntypeSelectorDialog(self.sign.signtype, parent=self)
        signtype_selector.saved_signtype.connect(self.handle_save_signtype)
        signtype_selector.exec_()

    def handle_save_signtype(self, signtype):
        self.sign.signtype = signtype
        self.sign_updated.emit(self.sign)

    def handle_menumodulebtn_clicked(self, moduletype):
        includearticulators = [HAND, ARM, LEG] if moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION] \
            else ([] if moduletype == ModuleTypes.RELATION else [HAND])
        includephase = 2 if moduletype == ModuleTypes.MOVEMENT else (
            1 if moduletype == ModuleTypes.LOCATION else
            0  # default
        )
        module_selector = ModuleSelectorDialog(moduletype=moduletype,
                                               xslotstructure=self.mainwindow.current_sign.xslotstructure,
                                               moduletoload=None,
                                               includephase=includephase,
                                               incl_articulators=includearticulators,
                                               incl_articulator_subopts=includephase,
                                               parent=self)
        module_selector.module_saved.connect(lambda moduletosave, savedtype: self.handle_save_module(moduletosave, moduletype=savedtype))
        module_selector.exec_()

    def handle_delete_module(self, existingkey, moduletype):
        if existingkey is None or existingkey not in self.sign.getmoduledict(moduletype).keys():
            print("TODO KV key error: attempting to delete a " +
                  moduletype + " module whose key is not in the list of existing modules")
        else:
            self.sign.removemodule(existingkey, moduletype)
        self.sign_updated.emit(self.sign)

    def handle_save_module(self, module_to_save, moduletype, existing_key=None):
        if existing_key is None or existing_key not in self.sign.getmoduledict(moduletype):
            self.sign.addmodule(module_to_save, moduletype)
        else:
            self.sign.updatemodule(existing_key, module_to_save, moduletype)
        self.sign_updated.emit(self.sign)

    def handle_menumodulebtn_clicked_na(self, moduletype):
        QMessageBox.information(self,
                                "Not available",
                                moduletype[0].upper()+moduletype[1:] + " module functionality not yet linked.")


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


class LocationSpecificationLayout_Old(QVBoxLayout):
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
