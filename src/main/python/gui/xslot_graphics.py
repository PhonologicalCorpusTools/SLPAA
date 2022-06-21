from fractions import Fraction
from num2words import num2words
import itertools

from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QLabel,
    QHBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QVBoxLayout,
    QMessageBox,
    QGraphicsEllipseItem
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon,
    QTextOption,
    QFont,
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRectF,
    QAbstractListModel,
    pyqtSignal,
    QSize,
    QEvent
)

from lexicon.lexicon_classes import TimingPoint, TimingInterval
from constant import FRACTION_CHAR


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
        # super().paint(painter, option, widget)

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

    def __init__(self, parentwidget, xslot_whole=0, xslot_part_start=None, xslot_part_end=None, text="", moduletype=None, sign=None, proportionfill=1):
        super().__init__()
        self.inactivebrush = QBrush(Qt.gray)
        self.setAcceptHoverEvents(False)
        self.parentwidget = parentwidget
        self.text = text
        self.moduletype = moduletype
        self.proportionfill = proportionfill
        self.sign = sign
        # self.mainwindow = mainwindow

        self.xslot_whole = xslot_whole  # if 0 it's the whole sign
        self.xslot_part_start = Fraction(0) if xslot_part_start is None else xslot_part_start
        self.xslot_part_end = Fraction(1) if xslot_part_end is None else xslot_part_end

    def currentbrush(self):
        return QBrush(Qt.white)  # self.unselectedbrush

    def currentpen(self):
        return QPen(Qt.black)  # self.unselectedpen

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)

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

    def __init__(self, parentwidget, selected=False, **kwargs):  # xslot_whole=0, xslot_part_start=None, xslot_part_end=None, text="", moduletype=None, sign=None, proportionfill=1, selected=False):
        super().__init__(parentwidget, **kwargs)
        self.setAcceptHoverEvents(True)
        self.hover = False
        self.selected = selected

    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()

    def currentbrush(self):
        if self.hover:
            return QColor(0, 120, 215)  # self.hoverbrush
        else:
            return self.restingbrush()

    def currentpen(self):
        if self.hover:
            return QPen(Qt.black)  # self.hoverpen
        else:
            return self.restingpen()

    def restingbrush(self):
        if self.selected:
            return QBrush(Qt.black)  # self.selectedbrush
        else:
            return QBrush(Qt.white)  # self.unselectedbrush

    def restingpen(self):
        if self.selected:
            return QPen(Qt.white)  # self.selectedpen
        else:
            return QPen(Qt.black)  # self.unselectedpen

    def toggle(self):
        self.selected = not self.selected
        self.update()


class XslotRectLinkingButton(XslotRectButton):

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.toggle()
        self.parentwidget.linkingrect_clicked.emit(self)  # self.xslot_whole, self.xslot_part_start, self.xslot_part_end)


class XslotEllipseModuleButton(QGraphicsEllipseItem):
    def __init__(self, parentwidget, module_uniqueid=0, text="", moduletype=None, sign=None):  # xslot_whole=0, xslot_part=None,
        super().__init__()
        self.parentwidget = parentwidget
        self.text = text
        self.moduletype = moduletype
        self.sign = sign
        # self.mainwindow = mainwindow

        self.setAcceptHoverEvents(True)
        self.hover = False
        self.module_uniqueid = module_uniqueid

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        # print("mouse released on module ellipse")
        self.scene().moduleellipse_clicked.emit(self)

    def hoverEnterEvent(self, event):
        self.hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hover = False
        self.update()

    def currentbrush(self):
        if self.hover:
            return QColor(0, 120, 215)  # self.hoverbrush
        else:
            return QBrush(Qt.white)  # self.unselectedbrush

    def currentpen(self):
        if self.hover:
            return QPen(Qt.black)  # self.hoverpen
        else:
            return QPen(Qt.black)  # self.unselectedpen

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)

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

    # def boundingRect(self):
    #     penWidth = self.pen().width()
    #     return QRectF(-radius - penWidth / 2, -radius - penWidth / 2,
    #                   diameter + penWidth, diameter + penWidth)


class XslotRectModuleButton(XslotRectButton):

    def __init__(self, parentwidget, module_uniqueid=0, **kwargs):
        super().__init__(parentwidget, **kwargs)
        self.module_uniqueid = module_uniqueid

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        # print("mouse released on module rectangle")
        self.scene().modulerect_clicked.emit(self)


class XslotSummaryScene(QGraphicsScene):
    modulerect_clicked = pyqtSignal(XslotRectModuleButton)
    moduleellipse_clicked = pyqtSignal(XslotEllipseModuleButton)


class XslotLinkingLayout(QVBoxLayout):

    def __init__(self, xslotstructure, mainwindow, parentwidget, timingintervals=[], **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        self.parentwidget = parentwidget
        self.timingintervals = timingintervals
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        if xslotstruct is None:
            print("no x-slot structure!")

        self.link_intro_label = QLabel(
            "Click on the relevant point(s) or interval(s) to link this module.")  # ("Link this module to the interval/point")
        self.addWidget(self.link_intro_label)

        self.xslotlinkscene = XslotLinkScene(parentwidget=self.parentwidget, mainwindow=self.mainwindow, timingintervals=self.timingintervals)
        self.xslotlinkview = QGraphicsView(self.xslotlinkscene)
        self.xslotlinkview.setFixedHeight(self.xslotlinkscene.scene_height+50)
        # self.xslotlinkview.setFixedSize(self.xslotlinkscene.scene_width+100, self.xslotlinkscene.scene_height+50)
        # self.xslotlinkview.setSceneRect(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height)
        # self.xslotlinkview.fitInView(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height, Qt.KeepAspectRatio)
        # self.xslotvlinkview.setGeometry(0, 0, self.xslotlinkscene.scene_width, self.xslotlinkscene.scene_height)
        self.addWidget(self.xslotlinkview)

    def gettimingintervals(self):
        return self.xslotlinkscene.xslotlinks

    def clear(self):
        self.xslotlinkscene = XslotLinkScene(parentwidget=self.parentwidget, mainwindow=self.mainwindow, timingintervals=self.timingintervals)
        self.xslotlinkview.setScene(self.xslotlinkscene)


class XSlotCheckbox(QGraphicsRectItem):

    def __init__(self, xslot_whole, xslot_part, parentwidget, textsize=30, penwidth=2, checked=False):  # sidelength=20
        super().__init__()
        # self.mainwindow = mainwindow
        self.parentwidget = parentwidget

        # self.sidelength = sidelength
        self.textsize = textsize
        self.penwidth = penwidth
        self.checked = checked

        self.setAcceptHoverEvents(True)
        self.hover = False

        self.xslot_whole = xslot_whole
        self.xslot_part = xslot_part

    def currentpen(self):
        pen = QPen()
        pen.setStyle(Qt.SolidLine)
        pen.setWidth(self.penwidth)
        pen.setColor(QColor(0,120,215) if self.hover else Qt.black)
        return pen

    def hoverEnterEvent(self, event):
        # if self.moduletype in ["signtype", "movement", "handshape"]:
        # self.setBrush(self.hoverbrush)
        # self.setPen(self.hoverpen)
        self.hover = True
        self.update()

    def hoverLeaveEvent(self, event):
        # if self.moduletype in ["signtype", "movement", "handshape"]:
        # self.setBrush(self.restingbrush())
        # self.setPen(self.restingpen())
        self.hover = False
        self.update()

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)

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
        painter.drawText(rect, "☑" if self.checked else "☐", textoption)

    def toggle(self):
        self.checked = not self.checked
        self.update()

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        self.toggle()
        self.parentwidget.checkbox_toggled.emit(self)  # self.xslot_whole, self.xslot_part)


class XslotLinkScene(QGraphicsScene):
    checkbox_toggled = pyqtSignal(XSlotCheckbox)
    linkingrect_clicked = pyqtSignal(XslotRectLinkingButton)

    def __init__(self, parentwidget, mainwindow=None, timingintervals=[]):
        super().__init__()

        self.mainwindow = mainwindow
        self.parentwidget = parentwidget
        self.timingintervals = timingintervals
        self.scene_width = 1500
        self.rect_height = 25
        self.checkbox_size = 25
        self.textbox_width = 60
        self.pen_width = 2
        self.scene_height = 0
        self.x_offset = 10

        xslotstruct = self.mainwindow.current_sign.xslotstructure
        self.numwholes = xslotstruct.number
        self.additionalfrac = xslotstruct.additionalfraction
        partialxslots = self.mainwindow.app_settings['signdefaults']['partial_xslots']
        self.avail_denoms = [Fraction(f).denominator for f in list(partialxslots.keys()) if partialxslots[f]]
        self.fractionalpoints = []
        for d in self.avail_denoms:
            for mult in range(d+1):
                self.fractionalpoints.append(Fraction(mult, d))
        self.fractionalpoints = list(set(self.fractionalpoints))
        self.xslot_width = self.scene_width / (self.numwholes + (1 if self.additionalfrac > 0 else 0))

        self.xslotlinks = []

        # TODO KV do we need this modularity now that there's only one row of them?
        self.point_checkboxes = {}
        self.populate_checkboxes(self.point_checkboxes)
        self.add_checkboxes(self.point_checkboxes, yloc=0)

        self.add_rectangles(yloc=3*self.checkbox_size)

        self.checkbox_toggled.connect(self.handle_point_toggled)
        self.linkingrect_clicked.connect(self.handle_interval_toggled)

    def handle_point_toggled(self, xslotcheckbox):

        whole = xslotcheckbox.xslot_whole
        frac = xslotcheckbox.xslot_part
        pointinterval = TimingInterval(TimingPoint(whole, frac), TimingPoint(whole, frac))

        if xslotcheckbox.checked and self.check_no_xslot_overlap(pointinterval, xslotcheckbox):
            self.xslotlinks.append(pointinterval)
        elif (not xslotcheckbox.checked) and pointinterval in self.xslotlinks:
            self.xslotlinks.remove(pointinterval)

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
                                                    "You have selected " + newly_selected + " adjacent to " + already_selected + ". Would you like to collapse the point into the interval?")
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
                                    "The attempted selection overlaps with an existing selection. Please first de-select the initial selection if you wish to continue.")
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

    def populate_checkboxes(self, checkboxes):

        for whole in range(1, self.numwholes+1):
            for part in self.fractionalpoints:
                checkthebox = False
                if TimingInterval(TimingPoint(whole, part), TimingPoint(whole, part)) in self.timingintervals:
                    checkthebox = True
                cb = XSlotCheckbox(whole, part, parentwidget=self, textsize=self.checkbox_size, checked=checkthebox)
                checkboxes[(whole, part)] = cb
        whole = self.numwholes+1
        for part in [fp for fp in self.fractionalpoints if fp <= self.additionalfrac and (fp > 0 or self.additionalfrac > 0)]:
            checkthebox = False
            if TimingInterval(TimingPoint(whole, part), TimingPoint(whole, part)) in self.timingintervals:
                checkthebox = True
            cb = XSlotCheckbox(whole, part, parentwidget=self, textsize=self.checkbox_size, checked=checkthebox)
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
                textbox.setText("[ x" + str(k[0]))
                textbox.setAlign(Qt.AlignLeft)
                xloc_box += 0.1 * self.checkbox_size
                xloc_text = xloc_box
            elif cb.xslot_part == 1:
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
                    if temptint in self.timingintervals:
                        selecttheinterval = True
                    xslotrect = XslotRectLinkingButton(self, xslot_whole=whole, xslot_part_start=part_start, xslot_part_end=part_end, text=text, moduletype='xslot', selected=selecttheinterval)
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
            if TimingInterval(TimingPoint(0, 0), TimingPoint(0, 1)) in self.timingintervals:
                selecttheinterval = True
            xslotrect = XslotRectLinkingButton(self, text="whole sign", moduletype='xslot', selected=selecttheinterval)
            xslotrect.setRect(self.x_offset, yloc, float(self.xslot_width*(self.numwholes+self.additionalfrac)), self.rect_height)
            self.addItem(xslotrect)

    def add_rectangles(self, yloc):

        # TODO do some more validity checking (are there even xslots?) before just going for it

        # for the fractional (and whole x-slot) rows
        denoms = list(set([f.denominator for f in self.fractionalpoints]))
        for idx, denom in enumerate(sorted(denoms, reverse=True)):
            yloc_row = yloc + idx*self.rect_height
            self.add_rectangle_row(yloc_row, Fraction(1, denom))

        # for the whole-sign row
        yloc_row = yloc_row + self.rect_height
        self.add_rectangle_row(yloc_row, None)

