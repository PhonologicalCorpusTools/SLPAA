from fractions import Fraction

from PyQt5.QtWidgets import (
    QGraphicsRectItem,
    QGridLayout,
    QRadioButton,
    QButtonGroup,
    QLabel,
    QHBoxLayout,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsEllipseItem,
    QVBoxLayout,
    QGraphicsObject
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon,
    QTextOption,
    QPainterPath,
    QFont
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


class XslotRect(QGraphicsRectItem):

    def __init__(self, parentwidget, text="", moduletype=None, sign=None, proportionfill=1, selected=False):
        super().__init__()
        self.selectedbrush = QBrush(Qt.black)
        self.unselectedbrush = QBrush(Qt.white)
        self.hoverbrush = QBrush(Qt.cyan)
        self.inactivebrush = QBrush(Qt.gray)
        self.selectedpen = QPen(Qt.white)
        self.unselectedpen = QPen(Qt.black)
        self.hoverpen = QPen(Qt.black)
        self.setAcceptHoverEvents(True)
        self.parentwidget = parentwidget
        self.text = text
        self.moduletype = moduletype
        self.hover = False
        self.proportionfill = proportionfill
        self.sign = sign
        self.selected = selected
        # self.mainwindow = mainwindow

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

    def currentbrush(self):
        if self.hover:
            return self.hoverbrush
        else:
            return self.restingbrush()

    def currentpen(self):
        if self.hover:
            return self.hoverpen
        else:
            return self.restingpen()

    def restingbrush(self):
        if self.selected:
            return self.selectedbrush
        else:
            return self.unselectedbrush

    def restingpen(self):
        if self.selected:
            return self.selectedpen
        else:
            return self.unselectedpen

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)

        # turn pen off while filling rectangle
        pen = painter.pen()
        pen.setStyle(Qt.NoPen)
        painter.setPen(pen)

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
        pen.setStyle(Qt.SolidLine)
        pen.setColor(Qt.black)
        pen.setWidth(5)
        painter.setPen(pen)
        entirerect = self.rect()
        painter.drawRect(entirerect)

        # draw rectangle text
        textoption = QTextOption(Qt.AlignCenter)
        # textoption.setAlignment(Qt.AlignCenter)
        font = painter.font()
        font.setPixelSize(35)
        painter.setFont(font)
        pen.setColor
        painter.drawText(self.rect(), self.text, textoption)

    def toggle(self):
        self.selected = not self.selected
        self.update()

# from gui.movement_selector import MovementSelectorDialog
# from gui.signtype_selector import SigntypeSelectorDialog
# from gui.handshape_selector import HandshapeSelectorDialog
# from lexicon.lexicon_classes import GlobalHandshapeInformation

class XslotRectLinkingButton(XslotRect):
    # linkingrect_clicked = pyqtSignal()  # TODO KV
    #
    def mousePressEvent(self, event):
        print("rectangle pressed")

    def mouseReleaseEvent(self, event):
        self.toggle()
        # self.linkingrect_clicked.emit(self.moduletype)

class XslotSummaryScene(QGraphicsScene):
    modulerect_clicked = pyqtSignal(str, str)


class XslotRectModuleButton(XslotRect):
    # modulerect_clicked = pyqtSignal(str)

    # def __init__(self, parentwidget, text="", moduletype=None, sign=None, mainwindow=None, restingbrush=QBrush(Qt.green), hoverbrush=QBrush(Qt.yellow), proportionfill=1):
    #     super().__init__()
    #     self.restingbrush = restingbrush
    #     self.hoverbrush = hoverbrush
    #     self.setAcceptHoverEvents(True)
    #     self.parentwidget = parentwidget
    #     self.text = text
    #     self.moduletype = moduletype
    #     self.hover = False
    #     self.proportionfill = proportionfill
    #     self.sign = sign
    #     self.mainwindow = mainwindow
    # #
    def mousePressEvent(self, event):
        print("rectangle pressed")

    def mouseReleaseEvent(self, event):
        # print("rectangle released")
        # QMessageBox.information(self.parentwidget, 'Rectangle clicked', 'You clicked the '+self.text+' rectangle!')
        self.scene().modulerect_clicked.emit(self.moduletype, self.text)
        #
        # if self.moduletype == "signlevel":
        #     self.handle_signlevelrebutton_click()
        # elif self.moduletype == "xslot":
        #     self.handle_xslotbutton_click()
        # elif self.moduletype == "signtype":
        #     self.handle_signtypebutton_click()
        # elif self.moduletype == "movement":
        #     self.handle_movementbutton_click()
        # elif self.moduletype == "handshape":
        #     self.handle_handshapebutton_click()
    #
    # # TODO KV don't want this duplicated (also in signsummarypanel)
    # def handle_movementbutton_click(self):
    #     # button = self.sender()
    #     # # TODO KV
    #     editing_existing = True  # button.property("existingmodule")
    #     existing_key = self.text
    #     if "." in existing_key:
    #         dot_idx = existing_key.index(".")
    #         existing_key = existing_key[dot_idx+1:]
    #     moduletoload = self.sign.movementmodules[existing_key][0]
    #     hands_dict = self.sign.movementmodules[existing_key][1]
    #     movement_selector = MovementSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload, hands=hands_dict)  # , parent=self)
    #     movement_selector.saved_movement.connect(lambda movementtree, hands: self.handle_save_movement(movementtree, hands, existing_key))
    #     movement_selector.exec_()
    #
    # def handle_save_movement(self, movementtree, hands_dict, existing_key):
    #     if existing_key is None or existing_key not in self.sign.movementmodules.keys():
    #         self.sign.addmovementmodule(movementtree, hands_dict)
    #     else:
    #         self.sign.movementmodules[existing_key] = [movementtree, hands_dict]
    #     # TODO KV
    #     # self.sign_updated.emit(self.sign)
    #
    # # TODO KV don't want this duplicated (also in signsummarypanel)
    # def handle_signtypebutton_click(self):
    #     signtype_selector = SigntypeSelectorDialog(self.sign.signtype, self.mainwindow)  # , parent=self)
    #     signtype_selector.saved_signtype.connect(self.handle_save_signtype)
    #     signtype_selector.exec_()
    #
    # def handle_save_signtype(self, signtype):
    #     self.sign.signtype = signtype
    #     self.sign_updated.emit(self.sign)
    #
    # # TODO KV don't want this duplicated (also in signsummarypanel)
    # def handle_handshapebutton_click(self):
    #     editing_existing = True  # button.property("existingmodule")
    #     existing_key = self.text
    #     moduletoload = self.sign.handshapemodules[existing_key]
    #     handshape_selector = HandshapeSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload)  # , parent=self)
    #     handshape_selector.saved_handshape.connect(lambda hs_global, hs_transcription: self.handle_save_handshape(GlobalHandshapeInformation(hs_global.get_value()), hs_transcription, existing_key))
    #     handshape_selector.exec_()
    #
    # def handle_save_handshape(self, hs_globalinfo, hs_transcription, existing_key):
    #     if existing_key is None or existing_key not in self.sign.handshapemodules.keys():
    #         self.sign.addhandshapemodule(hs_globalinfo, hs_transcription)
    #     else:
    #         self.sign.handshapemodules[existing_key] = [hs_globalinfo, hs_transcription]
    #     # self.sign_updated.emit(self.sign)
    #     # self.update_handshapemodulebuttons()

    # def mousePressEvent(self, event):
    #     print("rectangle pressed")
    #
    # def hoverEnterEvent(self, event):
    #     if self.moduletype in ["signtype", "movement", "handshape"]:
    #         self.setBrush(self.hoverbrush)
    #         self.hover = True
    #
    # def hoverLeaveEvent(self, event):
    #     if self.moduletype in ["signtype", "movement", "handshape"]:
    #         self.setBrush(self.restingbrush)
    #         self.hover = False
    #
    # def paint(self, painter, option, widget):
    #     # super().paint(painter, option, widget)
    #     pen = painter.pen()
    #     pen.setStyle(Qt.NoPen)
    #     painter.setPen(pen)
    #
    #     painter.setBrush(self.hoverbrush if self.hover else self.restingbrush)
    #     fractionalrect = self.rect()
    #     fractionalrect.setRight(self.rect().left() + (self.rect().width() * self.proportionfill))
    #     painter.drawRect(fractionalrect)
    #
    #     brush = painter.brush()
    #     brush.setStyle(Qt.NoBrush)
    #     painter.setBrush(brush)
    #     pen.setStyle(Qt.SolidLine)
    #     pen.setColor(Qt.black)
    #     pen.setWidth(5)
    #     painter.setPen(pen)
    #     entirerect = self.rect()
    #     painter.drawRect(entirerect)
    #
    #     textoption = QTextOption(Qt.AlignCenter)
    #     # textoption.setAlignment(Qt.AlignCenter)
    #     font = painter.font()
    #     font.setPixelSize(35)
    #     painter.setFont(font)
    #     painter.drawText(self.rect(), self.text, textoption)

    # def boundingRect(self):
    #     penWidth = self.pen().width()
    #     return QRectF(-radius - penWidth / 2, -radius - penWidth / 2,
    #                   diameter + penWidth, diameter + penWidth)


class XslotLinkingLayoutNew(QVBoxLayout):

    def __init__(self, xslotstructure, mainwindow, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        if xslotstruct is None:
            print("no x-slot structure!")

        self.link_intro_label = QLabel(
            "Click on the relevant point(s) or interval(s) to link this module.")  # ("Link this module to the interval/point")
        self.addWidget(self.link_intro_label)

        self.linkinglayout = QGridLayout()
        # don't waste space
        self.linkinglayout.setVerticalSpacing(0)
        self.linkinglayout.setContentsMargins(0, 0, 0, 0)

        self.xslotlinkscene = XslotLinkScene(mainwindow=self.mainwindow)
        self.xslotvlinkview = QGraphicsView()  # self.xslotlinkscene)
        self.xslotvlinkview.setGeometry(0, 0, 2000, 300)
        self.addWidget(self.xslotvlinkview)

        self.addLayout(self.linkinglayout)

class XslotLinkingLayout(QVBoxLayout):

    def __init__(self, start=None, end=None, mainwindow=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        if xslotstruct is None:
            print("no x-slot structure!")

        self.link_intro_label = QLabel("Click on the relevant point(s) or interval(s) to link this module.")  #("Link this module to the interval/point")
        self.addWidget(self.link_intro_label)

        self.linkinglayout = QGridLayout()
        # don't waste space
        self.linkinglayout.setVerticalSpacing(0)
        self.linkinglayout.setContentsMargins(0, 0, 0, 0)

        self.link_from_label = QLabel("from")
        self.link_to_label = QLabel("to")

        self.greenbrush = QBrush(Qt.green)
        self.bluebrush = QBrush(Qt.blue)
        self.blackpen = QPen(Qt.black)
        self.blackpen.setWidth(5)

        self.xslotlinkscene = XslotLinkScene(mainwindow=self.mainwindow)
        self.xslotvlinkview = QGraphicsView(self.xslotlinkscene)
        self.xslotvlinkview.setGeometry(0, 0, 2000, 300)
        self.addWidget(self.xslotvlinkview)


        #
        # self.link_from_scene = QGraphicsScene()
        # # TODO circle graphics
        #
        # self.link_from_view = QGraphicsView(self.scene, self)  # XslotGraphicsView(self.scene, self)
        # # self.link_from_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # self.link_from_view.setGeometry(0, 0, 1000, 100)
        # # self.setMinimumSize(1000,1000)






        # self.link_xslots_img = None  # TODO bar graphics
        # self.link_to_radios = None  # TODO circle graphics
        #
        # self.linkinglayout.addWidget(self.link_from_label, 0, 0, 1, 1, Qt.AlignRight)
        # self.linkinglayout.addWidget(self.link_from_radios, 0, 1, 1, 1, Qt.AlignLeft)
        # self.linkinglayout.addWidget(self.link_xslots_img, 1, 1, 1, 1, Qt.AlignLeft)
        # self.linkinglayout.addWidget(self.link_to_label, 2, 0, 1, 1, Qt.AlignRight)
        # self.linkinglayout.addWidget(self.link_to_radios, 2, 1, 1, 1, Qt.AlignLeft)

        self.addLayout(self.linkinglayout)

        # self.link_start_spin = QSpinBox()
        # xslotstruct = self.mainwindow.current_sign.xslotstructure
        # self.link_start_spin.setRange(1, xslotstruct.number + (len(xslotstruct.partials) > 0))
        # if start > 0:
        #     self.link_start_spin.setValue(start)
        # self.link_end_label = QLabel("to x")
        # self.link_end_spin = QSpinBox()
        # self.link_end_spin.setRange(1, xslotstruct.number + (len(xslotstruct.partials) > 0))
        # if end > 0:
        #     self.link_start_spin.setValue(end)
        #
        # self.addWidget(self.link_start_label)
        # self.addWidget(self.link_start_spin)
        # self.addWidget(self.link_end_label)
        # self.addWidget(self.link_end_spin)

    # def handle_rect_clicked(self, moduletype):
    #
    #     if moduletype == "signlevel":
    #         self.handle_signlevelbutton_click()
    #     elif moduletype == "xslot":
    #         self.handle_xslotbutton_click()
    #     elif moduletype == "signtype":
    #         self.handle_signtypebutton_click()
    #     elif moduletype == "movement":
    #         self.handle_movementbutton_click()
    #     elif moduletype == "handshape":
    #         self.handle_handshapebutton_click()

    # TODO KV don't want this duplicated (also in signsummarypanel)
    # def handle_movementbutton_click(self):
    #     # button = self.sender()
    #     # # TODO KV
    #     editing_existing = True  # button.property("existingmodule")
    #     existing_key = self.text
    #     if "." in existing_key:
    #         dot_idx = existing_key.index(".")
    #         existing_key = existing_key[dot_idx+1:]
    #     moduletoload = self.sign.movementmodules[existing_key][0]
    #     hands_dict = self.sign.movementmodules[existing_key][1]
    #     movement_selector = MovementSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload, hands=hands_dict)  # , parent=self)
    #     movement_selector.saved_movement.connect(lambda movementtree, hands: self.handle_save_movement(movementtree, hands, existing_key))
    #     movement_selector.exec_()

    # def handle_save_movement(self, movementtree, hands_dict, existing_key):
    #     if existing_key is None or existing_key not in self.sign.movementmodules.keys():
    #         self.sign.addmovementmodule(movementtree, hands_dict)
    #     else:
    #         self.sign.movementmodules[existing_key] = [movementtree, hands_dict]
    #     # TODO KV
    #     # self.sign_updated.emit(self.sign)
    #
    # # TODO KV don't want this duplicated (also in signsummarypanel)
    # def handle_signtypebutton_click(self):
    #     signtype_selector = SigntypeSelectorDialog(self.sign.signtype, self.mainwindow)  # , parent=self)
    #     signtype_selector.saved_signtype.connect(self.handle_save_signtype)
    #     signtype_selector.exec_()
    #
    # def handle_save_signtype(self, signtype):
    #     self.sign.signtype = signtype
    #     self.sign_updated.emit(self.sign)
    #
    # # TODO KV don't want this duplicated (also in signsummarypanel)
    # def handle_handshapebutton_click(self):
    #     editing_existing = True  # button.property("existingmodule")
    #     existing_key = self.text
    #     moduletoload = self.sign.handshapemodules[existing_key]
    #     handshape_selector = HandshapeSelectorDialog(mainwindow=self.mainwindow, enable_addnew=(not editing_existing), moduletoload=moduletoload)  # , parent=self)
    #     handshape_selector.saved_handshape.connect(lambda hs_global, hs_transcription: self.handle_save_handshape(GlobalHandshapeInformation(hs_global.get_value()), hs_transcription, existing_key))
    #     handshape_selector.exec_()
    #
    # def handle_save_handshape(self, hs_globalinfo, hs_transcription, existing_key):
    #     if existing_key is None or existing_key not in self.sign.handshapemodules.keys():
    #         self.sign.addhandshapemodule(hs_globalinfo, hs_transcription)
    #     else:
    #         self.sign.handshapemodules[existing_key] = [hs_globalinfo, hs_transcription]
    #     # self.sign_updated.emit(self.sign)
    #     # self.update_handshapemodulebuttons()



class XslotLinkScene(QGraphicsScene):
    def __init__(self, mainwindow=None):
        super().__init__()

        self.mainwindow = mainwindow
        self.scene_width = 2000
        self.rect_height = 50
        self.radio_radius = 10

        self.greenbrush = QBrush(Qt.green)
        self.bluebrush = QBrush(Qt.blue)
        self.blackpen = QPen(Qt.black)
        self.blackpen.setWidth(5)

        xslotstruct = self.mainwindow.current_sign.xslotstructure
        self.numwholes = xslotstruct.number
        self.additionalfrac = xslotstruct.additionalfraction
        self.fractionalpoints = xslotstruct.fractionalpoints
        self.fractionalpoints.extend([Fraction(0,1), Fraction(1,1)])
        self.xslot_width = self.scene_width / (self.numwholes + (1 if self.additionalfrac > 0 else 0))

        self.from_radios = {}
        self.populate_radios(self.from_radios)
        self.add_radios("From", self.from_radios, yloc=0)  # TODO figure out yloc

        self.add_rectangles(yloc=100)  # TODO figure out yloc

        self.to_radios = {}
        self.populate_radios(self.to_radios)
        self.add_radios("To", self.to_radios, yloc=200)  # TODO figure out yloc

    def populate_radios(self, radios):

        for whole in range(self.numwholes):
            for part in self.fractionalpoints:
                radio = XslotRadioCircle(whole+1, part)
                radios[(whole+1, part)] = radio
        for part in [fp for fp in self.fractionalpoints if fp <= self.additionalfrac]:
            radio = XslotRadioCircle(self.numwholes+1, part)
            radios[(self.numwholes+1, part)] = radio

    def add_radios(self, label, radios, yloc):
        for k in radios.keys():
            radio = radios[k]
            xloc = (radio.xslot_whole-1 + radio.xslot_part) * self.xslot_width
            if radio.xslot_part == 0:
                xloc -= self.radio_radius
            elif radio.xslot_part == 1:
                xloc += self.radio_radius
            radio.setRect(xloc, yloc, self.radio_radius*2.5, self.radio_radius*2.5)  # TODO clarify height and width
            self.addItem(radio)

    def add_rectangles(self, yloc):

        # TODO do some more validity checking (are there even xslots?) before just going for it

        xslotrects = {}
        if self.numwholes + self.additionalfrac > 0:
            for i in range(self.numwholes):
                xslotrect = XslotRect(self, text="x" + str(i + 1), moduletype='xslot')
                xloc = 0 + i * self.xslot_width - (2 * self.blackpen.width())
                xslotrect.setRect(xloc, yloc, self.xslot_width, 50)
                xslotrect.setPen(self.blackpen)
                xslotrect.setBrush(self.greenbrush)
                xslotrects["x" + str(i + 1)] = xslotrect
                # xslotrect.rect_clicked.connect(lambda moduletype: self.handle_rect_clicked(moduletype))
                self.addItem(xslotrect)
            if self.additionalfrac > 0:
                xslotrect = XslotRectModuleButton(self, text="x" + str(self.numwholes + 1), moduletype='xslot', proportionfill=self.additionalfrac)
                xloc = 0 + self.numwholes * self.xslot_width - (2 * self.blackpen.width())
                xslotrect.setRect(xloc, yloc, self.xslot_width, 50)  # * self.additionalfrac, 50)
                xslotrect.setPen(self.blackpen)
                xslotrect.setBrush(self.greenbrush)
                xslotrects["x" + str(self.numwholes + 1)] = xslotrect
                # xslotrect.rect_clicked.connect(lambda moduletype: self.handle_rect_clicked(moduletype))
                self.addItem(xslotrect)


class XslotRadioCircle(QGraphicsEllipseItem):
    radiocircle_toggled = pyqtSignal((str, str))

    def __init__(self, xslot_whole, xslot_part, radius=20, penwidth=5, mainwindow=None):
        super().__init__()

        self.pencolour = Qt.darkGray
        self.uncheckedbrush = Qt.white
        self.checkedbrush = Qt.black
        self.penwidth = penwidth
        self.radius = radius
        self.checked = False

        self.xslot_whole = xslot_whole
        self.xslot_part = xslot_part

    def mouseReleaseEvent(self, event):
        # print("rectangle released")
        # QMessageBox.information(self.parentwidget, 'Rectangle clicked', 'You clicked the '+self.text+' rectangle!')
        self.toggle()

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)
        pen = painter.pen()
        pen.setColor(self.pencolour)
        pen.setWidth(self.penwidth)
        painter.setPen(pen)

        brush = painter.brush()
        # if self.checked:
        #     # brush.setStyle(Qt.SolidPattern)
        #     brush.setColor(self.checkedbrush)
        # else:
        #     # brush.setStyle(Qt.NoBrush)
        #     brush.setColor(self.uncheckedbrush)
        brush.setColor(self.checkedbrush if self.checked else self.uncheckedbrush)
        painter.setBrush(brush)

        painter.drawEllipse(self.rect())

    def toggle(self):
        self.checked = not self.checked
        self.update()
        self.radiocircle_toggled.emit((self.xslot_whole, self.xslot_part))
