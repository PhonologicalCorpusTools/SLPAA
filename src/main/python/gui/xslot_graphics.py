from fractions import Fraction
from num2words import num2words
import logging

from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QGraphicsScene,
    QMessageBox,
    QGraphicsEllipseItem,
    QGraphicsSceneMouseEvent,
    QMenu,
    QAction
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QTextOption,
)

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QPointF
)

from lexicon.module_classes import TimingPoint, TimingInterval, Signtype, ParameterModule
from constant import FRACTION_CHAR, ModuleTypes


class XslotPointLabel(QGraphicsRectItem):

    def __init__(self, text="", align=Qt.AlignCenter):
        super().__init__()
        self.text = text
        self.align = align

    def setText(self, txt):
        self.text = txt

    def setAlign(self, align):
        self.align = align

    def paint(self, painter, option, widget):
        # turn pen off while filling rectangle
        painter.setBrush(Qt.NoBrush)

        # draw rectangle text
        textoption = QTextOption(self.align)
        # textoption.setAlignment(Qt.AlignCenter)
        font = painter.font()
        font.setPixelSize(18)
        painter.setFont(font)
        painter.drawText(self.rect(), self.text, textoption)


class XslotRect(QGraphicsRectItem):

    def __init__(self, parentwidget, xslot_whole=0, xslot_part_start=None, xslot_part_end=None, text="",
                 moduletype=None, sign=None, proportionfill=1):
        super().__init__()
        self.inactivebrush = QBrush(Qt.gray)
        self.setAcceptHoverEvents(False)
        self.parentwidget = parentwidget
        self.text = text
        self.moduletype = moduletype
        self.proportionfill = proportionfill
        self.sign = sign

        self.xslot_whole = xslot_whole  # if 0 it's the whole sign
        self.xslot_part_start = Fraction(0) if xslot_part_start is None else xslot_part_start
        self.xslot_part_end = Fraction(1) if xslot_part_end is None else xslot_part_end

    def currentbrush(self):
        return QBrush(Qt.white)

    def currentpen(self):
        return QPen(Qt.black)

    def paint(self, painter, option, widget):
        # turn pen off while filling rectangle
        painter.setPen(Qt.NoPen)

        # fill active percentage of rectangle
        painter.setBrush(self.currentbrush())
        fractionalrect = self.rect()
        fractionalrect.setRight(self.rect().left() + (self.rect().width() * self.proportionfill))
        painter.drawRect(fractionalrect)

        # fill inactive percentage of rectangle
        if self.proportionfill < 1:
            painter.setBrush(self.inactivebrush)
            fractionalrect = self.rect()
            fractionalrect.setLeft(self.rect().left() + (self.rect().width() * self.proportionfill))
            painter.drawRect(fractionalrect)

        # turn off brush while outlining rectangle & drawing text
        brush = painter.brush()
        brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)

        # outline rectangle
        painter.setPen(self.currentpen())
        entirerect = self.rect()
        painter.drawRect(entirerect)

        # draw rectangle text
        textoption = QTextOption(Qt.AlignCenter)
        # textoption.setAlignment(Qt.AlignCenter)
        font = painter.font()
        font.setPixelSize(15)
        painter.setFont(font)
        painter.drawText(self.rect(), self.text, textoption)


class XslotRectButton(XslotRect):

    def __init__(self, parentwidget, selected=False, **kwargs):
        super().__init__(parentwidget, **kwargs)
        self.setAcceptHoverEvents(True)
        self.hover = 0  # 0 = no; 1 = yes; 2 = associated/partial
        self._selected = selected

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        if isinstance(selected, bool):
            self._selected = selected
            self.update()

    def hoverEnterEvent(self, event):
        self.hover = 1
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover = 0
        self.update()

    def currentbrush(self):
        if self.hover == 1:
            return QBrush(QColor(0, 120, 215))
        elif self.hover == 2:
            return QBrush(QColor(170, 215, 245))
        else:
            return self.restingbrush()

    def currentpen(self):
        if self.hover > 0:
            return QPen(Qt.black)
        else:
            return self.restingpen()

    def restingbrush(self):
        if self.selected:
            return QBrush(Qt.black)
        else:
            return QBrush(Qt.white)

    def restingpen(self):
        if self.selected:
            return QPen(Qt.white)
        else:
            return QPen(Qt.black)

    def toggle(self):
        self.selected = not self.selected


class XslotRectLinkingButton(XslotRectButton):

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle()
            self.parentwidget.linkingrect_clicked.emit(self)


class XslotEllipseModuleButton(QGraphicsEllipseItem):

    def __init__(self, parentwidget, module_uniqueid=0, text="", moduletype=None, sign=None, selected=False):
        super().__init__()
        self.parentwidget = parentwidget
        self.text = text
        self.moduletype = moduletype
        self.sign = sign
        self.samemodule_buttons = []

        self.setAcceptHoverEvents(True)
        self.hover = 0  # 0 = no; 1 = yes; 2 = associated/partial
        self._selected = selected
        self.module_uniqueid = module_uniqueid

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        if isinstance(selected, bool):
            self._selected = selected
            self.update()

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.scene().moduleellipse_clicked.emit(self, 1, event)

    def mouseDoubleClickEvent(self, event):
        self.scene().moduleellipse_clicked.emit(self, 2, event)

    def hoverEnterEvent(self, event):
        self.hover = 1
        self.update()
        self.update_partners_hover()

    def update_partners_hover(self):
        for btn in self.samemodule_buttons:
            btn.hover = self.hover
            btn.update()
        for btn in self.associatedmodule_buttons:
            btn.hover = self.hover * 2  # input 1 becomes 2 (partial); input 0 stays 0 (no)
            btn.update()

    def hoverLeaveEvent(self, event):
        self.hover = 0
        self.update()
        self.update_partners_hover()

    def currentbrush(self):
        if self.hover == 1:
            return QBrush(QColor(0, 120, 215))
        elif self.hover == 2:
            return QBrush(QColor(170, 215, 245))
        else:
            return self.restingbrush()

    def currentpen(self):
        if self.hover > 0:
            return QPen(Qt.black)
        else:
            return self.restingpen()

    def restingbrush(self):
        if self.selected:
            return QBrush(Qt.black)
        else:
            return QBrush(Qt.white)

    def restingpen(self):
        if self.selected:
            return QPen(Qt.white)
        else:
            return QPen(Qt.black)

    def toggle(self):
        self.selected = not self.selected

    def paint(self, painter, option, widget):
        # turn pen off while filling ellipse
        painter.setPen(Qt.NoPen)

        # fill ellipse
        painter.setBrush(self.currentbrush())
        painter.drawEllipse(self.rect())

        # turn off brush while outlining ellipse & drawing text
        brush = painter.brush()
        brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)

        # outline ellipse
        painter.setPen(self.currentpen())
        entirerect = self.rect()
        painter.drawEllipse(entirerect)

        # draw ellipse text
        textoption = QTextOption(Qt.AlignCenter)
        # textoption.setAlignment(Qt.AlignCenter)
        font = painter.font()
        font.setPixelSize(15)
        painter.setFont(font)
        painter.drawText(self.rect(), self.text, textoption)


class XslotRectModuleButton(XslotRectButton):

    def __init__(self, parentwidget, module_uniqueid=0, **kwargs):
        super().__init__(parentwidget, **kwargs)
        self.module_uniqueid = module_uniqueid
        self.samemodule_buttons = []
        self.associatedmodule_buttons = []

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.scene().modulerect_clicked.emit(self, 1, event)

    def mouseDoubleClickEvent(self, event):
        self.scene().modulerect_clicked.emit(self, 2, event)

    def hoverEnterEvent(self, event):
        super().hoverEnterEvent(event)
        self.update_partners_hover()

    def hoverLeaveEvent(self, event):
        super().hoverLeaveEvent(event)
        self.update_partners_hover()

    def update_partners_hover(self):
        for btn in self.samemodule_buttons:
            btn.hover = self.hover
            btn.update()
        for btn in self.associatedmodule_buttons:
            btn.hover = self.hover * 2  # input 1 becomes 2 (partial); input 0 stays 0 (no)
            btn.update()


# menu associated with a module button/buttons in the sign summary panel, offering copy/paste/delete functions
class ModuleButtonContextMenu(QMenu):
    action_selected = pyqtSignal(str)  # "copy", "paste", "delete", "copy timing", or "paste timing"

    # individual menu items are enabled/disabled based on whether any module buttons are selected (for copy or delete)
    #   and whether there's anything on the clipboard (for paste)
    def __init__(self, selected_modules=None, clipboardlist=None, whichactions=None, hastiming=True, **kwargs):
        super().__init__(**kwargs)
        selected_modules = selected_modules or []
        clipboardlist = clipboardlist or []
        if whichactions is None:
            # seemed potentially messy to include "edit" so I didn't
            whichactions = ["copy", "paste", "delete", "copy timing", "paste timing"]

        if "copy" in whichactions:
            self.copy_action = QAction("Copy module(s)")  # : " + str([btn.text for btn in selected_buttons]))
            self.copy_action.setEnabled(len(selected_modules) > 0 and islistofmodules(selected_modules))
            self.copy_action.triggered.connect(lambda checked: self.action_selected.emit("copy"))
            self.addAction(self.copy_action)

        if "paste" in whichactions:
            self.paste_action = QAction("Paste module(s)")
            self.paste_action.setEnabled(len(clipboardlist) > 0 and islistofmodules(clipboardlist))
            self.paste_action.triggered.connect(lambda checked: self.action_selected.emit("paste"))
            self.addAction(self.paste_action)

        if "delete" in whichactions:
            self.delete_action = QAction("Delete module(s)")
            self.delete_action.setEnabled(len(selected_modules) > 0 and islistofmodules(selected_modules))
            self.delete_action.triggered.connect(lambda checked: self.action_selected.emit("delete"))
            self.addAction(self.delete_action)

        if hastiming:
            if "copy timing" in whichactions:
                self.copytiming_action = QAction("Copy module timing")  # can only be done for one module at a time
                self.copytiming_action.setEnabled(len(selected_modules) == 1 and selected_modules[0].moduletype != ModuleTypes.SIGNTYPE)
                self.copytiming_action.triggered.connect(lambda checked: self.action_selected.emit("copy timing"))
                self.addAction(self.copytiming_action)

            if "paste timing" in whichactions:
                self.pastetiming_action = QAction("Paste module timing")  # could be for more than one module at a time, but can't paste to Signtype
                self.pastetiming_action.setEnabled(islistoftimingintervals(clipboardlist) and len([mod for mod in selected_modules if mod.moduletype != ModuleTypes.SIGNTYPE]) > 0)
                self.pastetiming_action.triggered.connect(lambda checked: self.action_selected.emit("paste timing"))
                self.addAction(self.pastetiming_action)


# This context menu allows users to copy or paste module timing information by right-clicking in the X-slot linking view
#   in a module editing dialog
class XslotLinkSceneContextMenu(ModuleButtonContextMenu):

    # individual menu items are enabled/disabled based on whether there's anything on the clipboard (for paste timing)
    def __init__(self, clipboardlist=None, **kwargs):  # , selected_timingintervals_list=None
        super().__init__(clipboardlist=clipboardlist, hastiming=True, whichactions=["copy timing", "paste timing"], **kwargs)

        # in the parent class this depends on whether any modules are selected, but from the xslot linking view itself
        #   it should always be possible to copy
        self.copytiming_action.setEnabled(True)

        # paste is only available in the xslot linking view if the contents of the clipboard are a list of timing intervals
        self.pastetiming_action.setEnabled(len(clipboardlist) > 0 and islistoftimingintervals(clipboardlist))


# checks whether the given list contains only TimingIntervals
def islistoftimingintervals(itemslist):
    istimingintervals = [isinstance(item, TimingInterval) for item in itemslist]
    return False not in istimingintervals


# checks whether the given list contains only modules (either ParameterModule or Signtype)
def islistofmodules(itemslist):
    ismodules = [(isinstance(item, Signtype) or isinstance(item, ParameterModule)) for item in itemslist]
    return False not in ismodules


class SignSummaryScene(QGraphicsScene):
    # button that was clicked, single vs double click, mouseevent
    modulerect_clicked = pyqtSignal(XslotRectModuleButton, int, QGraphicsSceneMouseEvent)
    moduleellipse_clicked = pyqtSignal(XslotEllipseModuleButton, int, QGraphicsSceneMouseEvent)
    scenebg_clicked = pyqtSignal(int, QGraphicsSceneMouseEvent)
    clear_selections = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_menu_pos = QPointF(0, 0)

    def mouseReleaseEvent(self, event):
        itemsatclick = self.items(QPointF(event.scenePos().x(), event.scenePos().y()))
        modulebuttonsatclick = [sceneitem for sceneitem in itemsatclick if isinstance(sceneitem, XslotRectModuleButton) or isinstance(sceneitem, XslotEllipseModuleButton)]
        if len(modulebuttonsatclick) > 0:
            # don't do anything here; the menu at this click point will be spawned by the module button instead
            super().mouseReleaseEvent(event)
        else:
            self.clear_selections.emit()
            # we've checked all the items at the click point and none of them are module buttons,
            #   so show the menu via the scene background
            self.scenebg_clicked.emit(1, event)

    # def mousePressEvent(self, event):
    #     super().mousePressEvent(event)


class XSlotCheckbox(QGraphicsRectItem):

    def __init__(self, xslot_whole, xslot_part, parentwidget, textsize=30, penwidth=2, selected=False):  # sidelength=20
        super().__init__()
        self.parentwidget = parentwidget

        self.textsize = textsize
        self.penwidth = penwidth
        self._selected = selected

        self.setAcceptHoverEvents(True)
        self.hover = False

        self.xslot_whole = xslot_whole
        self.xslot_part = xslot_part

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, selected):
        if isinstance(selected, bool):
            self._selected = selected
            self.update()

    def currentpen(self):
        pen = QPen()
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(self.penwidth)
        pen.setColor(QColor(0, 120, 215) if self.hover else Qt.black)
        return pen

    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()

    def paint(self, painter, option, widget):
        # turn off brush - we're just drawing text
        brush = painter.brush()
        brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)

        painter.setPen(self.currentpen())
        rect = self.rect()
        rect.setHeight(rect.height()+5)

        textoption = QTextOption(Qt.AlignCenter)
        font = painter.font()
        font.setPixelSize(self.textsize)
        painter.setFont(font)
        # draw check or empty box
        painter.drawText(rect, "☑" if self.selected else "☐", textoption)

    def toggle(self):
        self.selected = not self.selected
        self.update()

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.toggle()
        self.parentwidget.checkbox_toggled.emit(self)


class XslotLinkScene(QGraphicsScene):
    checkbox_toggled = pyqtSignal(XSlotCheckbox)
    linkingrect_clicked = pyqtSignal(XslotRectLinkingButton)
    selection_changed = pyqtSignal(bool,  # has >= 1 point
                                   bool)  # has >= 1 interval
    scene_Rclicked = pyqtSignal(QGraphicsSceneMouseEvent)

    def __init__(self, parentwidget, timingintervals=None, **kwargs):
        super().__init__(**kwargs)
        self.parentwidget = parentwidget
        self.mainwindow = self.parentwidget.mainwindow

        self.scene_width = 1500
        self.rect_height = 25
        self.checkbox_size = 25
        self.textbox_width = 60
        self.pen_width = 2
        self.scene_height = 0
        self.x_offset = 10

        xslotstruct = self.parentwidget.xslotstruct
        self.numwholes = xslotstruct.number
        self.additionalfrac = xslotstruct.additionalfraction
        if self.parentwidget.partialxslots is None:
            partialxslots = self.mainwindow.app_settings['signdefaults']['partial_xslots']
        else:
            partialxslots = self.parentwidget.partialxslots
        self.avail_denoms = [Fraction(f).denominator for f in list(partialxslots.keys()) if partialxslots[f]]
        self.fractionalpoints = []
        for d in self.avail_denoms:
            for mult in range(d+1):
                self.fractionalpoints.append(Fraction(mult, d))
        self.fractionalpoints = list(set(self.fractionalpoints))
        self.xslot_width = self.scene_width / (self.numwholes + (1 if self.additionalfrac > 0 else 0))

        self.xslotlinks = [] if timingintervals is None else timingintervals

        # TODO KV do we need this modularity now that there's only one row of them?
        self.point_checkboxes = {}
        self.populate_checkboxes(self.point_checkboxes)
        if len(self.point_checkboxes) == 0:
            self.populate_start_end_checkboxes(self.point_checkboxes)
        self.add_checkboxes(self.point_checkboxes, yloc=0)

        self.add_rectangles(yloc=3*self.checkbox_size)

        self.checkbox_toggled.connect(self.handle_point_toggled)
        self.linkingrect_clicked.connect(self.handle_interval_toggled)

    def setxslotlinks(self, xslotlinks):
        if xslotlinks is not None:
            self.xslotlinks = xslotlinks
            self.add_populate_checkboxes_rectangles()

    def add_populate_checkboxes_rectangles(self):
        # TODO KV do we need this modularity now that there's only one row of them?
        self.point_checkboxes = {}
        self.populate_checkboxes(self.point_checkboxes)
        if len(self.point_checkboxes) == 0:
            self.populate_start_end_checkboxes(self.point_checkboxes)
        self.add_checkboxes(self.point_checkboxes, yloc=0)

        self.add_rectangles(yloc=3*self.checkbox_size)

        self.emit_selection_changed()

    def handle_point_toggled(self, xslotcheckbox):

        whole = xslotcheckbox.xslot_whole
        frac = xslotcheckbox.xslot_part
        pointinterval = TimingInterval(TimingPoint(whole, frac), TimingPoint(whole, frac))

        if xslotcheckbox.selected and self.check_no_xslot_overlap(pointinterval, xslotcheckbox):
            self.xslotlinks.append(pointinterval)
        elif (not xslotcheckbox.selected) and pointinterval in self.xslotlinks:
            self.xslotlinks.remove(pointinterval)

        self.emit_selection_changed()

    def check_no_xslot_overlap(self, timinginterval, xslotgraphicsitem):
        success = True
        collapse_check = False

        for xinterval in self.xslotlinks:

            if timinginterval.startpoint.wholepart == 0 or xinterval.startpoint.wholepart == 0:
                # at least one of them is the whole sign; guaranteed to be overlap
                success = False
                break
            elif timinginterval.before(xinterval) or timinginterval.after(xinterval):
                if timinginterval.ispoint() != xinterval.ispoint() and timinginterval.adjacent(xinterval):
                    newly_selected = "a point" if timinginterval.ispoint() else "an interval"
                    already_selected = "an existing " + ("interval" if timinginterval.ispoint() else "point")
                    response = QMessageBox.question(self.parentwidget, 'Adjacent point',
                                                    "You have selected " + newly_selected + " adjacent to " +
                                                    already_selected +
                                                    ". Would you like to collapse the point into the interval?")
                    if response == QMessageBox.Yes:
                        if timinginterval.ispoint():
                            xslotgraphicsitem.toggle()
                            return False
                        elif xinterval.ispoint():
                            self.point_checkboxes[(xinterval.startpoint.wholepart, xinterval.startpoint.fractionalpart)].toggle()
                            self.xslotlinks.remove(xinterval)
                    else:
                        return True
                continue
            else:
                # there is some overlap
                success = False
                break

        if not success:
            QMessageBox.information(self.parentwidget, "X-slot clash",
                                    "The attempted selection overlaps with an existing selection. "
                                    + "Please first de-select the initial selection if you wish to continue.")
            xslotgraphicsitem.toggle()

        return success

    def handle_interval_toggled(self, xslotintervalrect):

        whole = xslotintervalrect.xslot_whole
        startfrac = xslotintervalrect.xslot_part_start
        endfrac = xslotintervalrect.xslot_part_end
        interval = TimingInterval(TimingPoint(whole, startfrac), TimingPoint(whole, endfrac))

        if xslotintervalrect.selected and self.check_no_xslot_overlap(interval, xslotintervalrect):
            self.xslotlinks.append(interval)
        elif (not xslotintervalrect.selected) and interval in self.xslotlinks:
            self.xslotlinks.remove(interval)

        self.emit_selection_changed()

    def emit_selection_changed(self):
        haspoint = False
        hasinterval = False

        idx = 0
        while idx < len(self.xslotlinks) and (not haspoint or not hasinterval):
            link = self.xslotlinks[idx]
            if link.ispoint():
                haspoint = True
            else:
                hasinterval = True
            idx += 1

        self.selection_changed.emit(haspoint, hasinterval)
    
    def populate_start_end_checkboxes(self, start_end):
        start = XSlotCheckbox(1, 0, parentwidget=self, textsize=self.checkbox_size, selected=False)
        end = XSlotCheckbox(1, 1, parentwidget=self, textsize=self.checkbox_size, selected=False)
        start_end[(1,0)] = start
        start_end[(1,1)] = end

    def populate_checkboxes(self, checkboxes):
        for whole in range(1, self.numwholes+1):
            for part in self.fractionalpoints:
                checkthebox = False
                if TimingInterval(TimingPoint(whole, part), TimingPoint(whole, part)) in self.xslotlinks:
                    checkthebox = True
                cb = XSlotCheckbox(whole, part, parentwidget=self, textsize=self.checkbox_size, selected=checkthebox)
                checkboxes[(whole, part)] = cb
        whole = self.numwholes+1
        for part in [fp for fp in self.fractionalpoints if fp <= self.additionalfrac and (fp > 0 or self.additionalfrac > 0)]:
            checkthebox = False
            if TimingInterval(TimingPoint(whole, part), TimingPoint(whole, part)) in self.xslotlinks:
                checkthebox = True
            cb = XSlotCheckbox(whole, part, parentwidget=self, textsize=self.checkbox_size, selected=checkthebox)
            checkboxes[(whole, part)] = cb

    def add_checkboxes(self, checkboxes, yloc):
        yloc_text = yloc
        yloc_box = yloc + self.checkbox_size
        for k in checkboxes.keys():
            cb = checkboxes[k]
            textbox = XslotPointLabel()
            xloc_box = (cb.xslot_whole-1 + cb.xslot_part) * self.xslot_width + self.x_offset
            xloc_text = xloc_box
            if cb.xslot_part == 0:
                if len(checkboxes) == 2: # only start and end points are required (no fractional xslots)
                    textbox.setText("Start")
                else:
                    textbox.setText("[ x" + str(k[0]))
                textbox.setAlign(Qt.AlignLeft)
                xloc_box += 0.1 * self.checkbox_size
                xloc_text = xloc_box
            elif cb.xslot_part == 1:
                if len(checkboxes) == 2: # only start and end points are required (no fractional xslots)
                    textbox.setText("End")
                else:
                    textbox.setText("x"+str(k[0])+" ]")
                
                textbox.setAlign(Qt.AlignRight)
                xloc_text = xloc_box - (0.1*self.checkbox_size) - self.textbox_width
                xloc_box -= 1.1 * self.checkbox_size
            else:
                textbox.setText(str(k[1]))
                textbox.setAlign(Qt.AlignCenter)
                xloc_text = xloc_box - self.textbox_width/2
                xloc_box -= 0.5 * self.checkbox_size
            textbox.setRect(xloc_text, yloc_text, self.textbox_width, self.checkbox_size)
            self.addItem(textbox)
            cb.setRect(xloc_box, yloc_box, self.checkbox_size, self.checkbox_size)  # TODO clarify height and width
            self.addItem(cb)

    # frac_size determines the width of the rectangles in this row
    #   (is it the quarter-xslot row? the half-xslot row? etc)
    #   if frac_size is none, then we're doing the whole-sign row
    def add_rectangle_row(self, yloc, frac_size):
        if self.scene_height < yloc:
            self.scene_height = yloc
        if frac_size is not None:
            # make a row of rectangles, each frac_size of an xslot,
            #   up to & including the endpoint of the final (part of an) xslot
            denom = frac_size.denominator
            total = self.numwholes + self.additionalfrac

            whole_i = 0
            met_total = False
            num_rects = 0

            while whole_i < self.numwholes+1:
                frac_j = 0
                while frac_j < denom and not met_total:
                    # make a rectangle for this fraction of the xslot
                    text = "x"+str(whole_i+1)
                    if frac_size != 1:
                        text = num2words(frac_j+1, lang="en", to="ordinal_num") + " " + FRACTION_CHAR[frac_size] + " " + text

                    whole = whole_i+1
                    part_start = Fraction(frac_j, denom)
                    part_end = Fraction(frac_j+1, denom)
                    selecttheinterval = False
                    temptint = TimingInterval(TimingPoint(whole, part_start), TimingPoint(whole, part_end))
                    if temptint in self.xslotlinks:
                        selecttheinterval = True

                    xslotrect = XslotRectLinkingButton(self,
                                                       xslot_whole=whole,
                                                       xslot_part_start=part_start,
                                                       xslot_part_end=part_end,
                                                       text=text,
                                                       moduletype='xslot',
                                                       selected=selecttheinterval)
                    xloc = 0 + (whole_i + (frac_j/denom)) * self.xslot_width + self.x_offset  # - (self.pen_width * num_rects)
                    xslotrect.setRect(xloc, yloc, float(self.xslot_width * frac_size), self.rect_height)
                    self.addItem(xslotrect)
                    met_total = whole_i + ((frac_j+2)/denom) > total
                    frac_j += 1
                    num_rects += 1
                whole_i += 1
        else:
            # make a rectangle for the whole sign (all x-slots)
            selecttheinterval = False
            startpoint = TimingPoint(1, 0)
            if self.additionalfrac != 0:
                endpoint = TimingPoint(self.numwholes, self.additionalfrac)
            else:
                endpoint = TimingPoint(self.numwholes, 1)
            if TimingInterval(TimingPoint(0, 0), TimingPoint(0, 1)) in self.xslotlinks:
                selecttheinterval = True
            xslotrect = XslotRectLinkingButton(self, text="whole sign", moduletype='xslot', selected=selecttheinterval)
            xslotrect.setRect(self.x_offset, yloc, float(self.xslot_width*(self.numwholes+self.additionalfrac)), self.rect_height)
            self.addItem(xslotrect)

    def add_rectangles(self, yloc):

        # TODO do some more validity checking (are there even xslots?) before just going for it

        # for the fractional (and whole x-slot) rows
        yloc_row = 2*self.rect_height
        denoms = list(set([f.denominator for f in self.fractionalpoints]))
        for idx, denom in enumerate(sorted(denoms, reverse=True)):
            yloc_row = yloc + idx*self.rect_height
            self.add_rectangle_row(yloc_row, Fraction(1, denom))

        # for the whole-sign row
        yloc_row = yloc_row + self.rect_height
        self.add_rectangle_row(yloc_row, None)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)

        ctrlmodifier = event.modifiers() & Qt.ControlModifier
        mousebutton = event.button()

        if mousebutton == Qt.RightButton and not ctrlmodifier:
            # provide a context menu to paste timing from the module currently on the clipboard
            self.scene_Rclicked.emit(event)

