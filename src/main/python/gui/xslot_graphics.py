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
    QGraphicsEllipseItem,
    QVBoxLayout
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon,
    QTextOption,
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

    def __init__(self, parentwidget, text="", moduletype=None, sign=None, mainwindow=None, restingbrush=QBrush(Qt.green), hoverbrush=QBrush(Qt.yellow), proportionfill=1):
        super().__init__()
        self.restingbrush = restingbrush
        self.hoverbrush = hoverbrush
        self.setAcceptHoverEvents(True)
        self.parentwidget = parentwidget
        self.text = text
        self.moduletype = moduletype
        self.hover = False
        self.proportionfill = proportionfill
        self.sign = sign
        self.mainwindow = mainwindow

    def hoverEnterEvent(self, event):
        if self.moduletype in ["signtype", "movement", "handshape"]:
            self.setBrush(self.hoverbrush)
            self.hover = True

    def hoverLeaveEvent(self, event):
        if self.moduletype in ["signtype", "movement", "handshape"]:
            self.setBrush(self.restingbrush)
            self.hover = False


    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)
        pen = painter.pen()
        pen.setStyle(Qt.NoPen)
        painter.setPen(pen)

        painter.setBrush(self.hoverbrush if self.hover else self.restingbrush)
        fractionalrect = self.rect()
        fractionalrect.setRight(self.rect().left() + (self.rect().width() * self.proportionfill))
        painter.drawRect(fractionalrect)

        brush = painter.brush()
        brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)
        pen.setStyle(Qt.SolidLine)
        pen.setColor(Qt.black)
        pen.setWidth(5)
        painter.setPen(pen)
        entirerect = self.rect()
        painter.drawRect(entirerect)

        textoption = QTextOption(Qt.AlignCenter)
        # textoption.setAlignment(Qt.AlignCenter)
        font = painter.font()
        font.setPixelSize(35)
        painter.setFont(font)
        painter.drawText(self.rect(), self.text, textoption)


# from gui.movement_selector import MovementSelectorDialog
# from gui.signtype_selector import SigntypeSelectorDialog
# from gui.handshape_selector import HandshapeSelectorDialog
# from lexicon.lexicon_classes import GlobalHandshapeInformation

class XslotRectButton(XslotRect):
    rect_clicked = pyqtSignal(str)

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

    def mousePressEvent(self, event):
        print("rectangle pressed")

    def mouseReleaseEvent(self, event):
        # print("rectangle released")
        # QMessageBox.information(self.parentwidget, 'Rectangle clicked', 'You clicked the '+self.text+' rectangle!')
        self.rect_clicked.emit(self.moduletype)
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


class XslotLinkingLayout(QVBoxLayout):

    def __init__(self, start=None, end=None, mainwindow=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        if xslotstruct is None:
            print("no x-slot structure!")

        self.link_intro_label = QLabel("Link this module to the interval/point")
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


        self.link_from_buttongroup = QButtonGroup()
        self.radios = {}
        for xslot in range(1, xslotstruct.number+1):
            self.radios[xslot] = {}
            for fraction_of_12 in [0, 3, 4, 6, 8, 9, 12]:
                thisbutton = QRadioButton()
                thisbutton.setProperty("xslot", xslot)
                thisbutton.setProperty("fraction", fraction_of_12)
                self.link_from_buttongroup.addButton(thisbutton)
                self.radios[xslot][fraction_of_12] = thisbutton
        xslot = xslotstruct.number + 1
        self.radios[xslot] = {}
        fracs_of_12 = [0] + [float(p)*12 for p in xslotstruct.fractionalpoints]
        for frac_of_12 in fracs_of_12:
            thisbutton = QRadioButton()
            thisbutton.setProperty("xslot", xslot)
            thisbutton.setProperty("fraction", frac_of_12)
            self.link_from_buttongroup.addButton(thisbutton)
            self.radios[xslot][frac_of_12] = thisbutton

        self.linkinglayout.addWidget(self.link_from_label, 0, 0, 1, 1)
        row = 0
        xslot = 1
        while xslot in self.radios.keys():
            for frac_of_12 in self.radios[xslot].keys():
                if frac_of_12 == 0 and xslot-1 not in self.radios.keys():
                    print("adding radio button for xslot", xslot, "position", frac_of_12, "to gridlayout column", 1+(xslot-1)*12)
                    self.linkinglayout.addWidget(self.radios[xslot][0], row, 1+(xslot-1)*12, 1, 1)
                elif frac_of_12 == 0 and xslot-1 in self.radios.keys():
                    radiopairlayout = QHBoxLayout()
                    print("adding radio buttons for xslots", xslot-1, "position 12 and xslot", xslot, "position 0 to gridlayout column", 1+(xslot-1)*12)
                    radiopairlayout.addWidget(self.radios[xslot-1][12])
                    radiopairlayout.addWidget(self.radios[xslot][0])
                    self.linkinglayout.addLayout(radiopairlayout, row, 1+(xslot-1)*12, 1, 1)
                elif frac_of_12 == 12 and xslot+1 not in self.radios.keys():
                    print("adding radio button for xslot", xslot, "position", frac_of_12, "to gridlayout column", 1+(xslot*12))
                    self.linkinglayout.addWidget(self.radios[xslot][12], row, 1+(xslot*12), 1, 1)
                elif frac_of_12 == 12 and xslot+1 in self.radios.keys():
                    # this will get rolled into the 0 spot in the next xslot
                    pass
                else:
                    print("adding radio button for xslot", xslot, "position", frac_of_12, "to gridlayout column", 1+(xslot-1)*12)
                    self.linkinglayout.addWidget(self.radios[xslot][frac_of_12], row, 1+(xslot-1)*12 + frac_of_12, 1, 1)
            xslot += 1

        sign = self.mainwindow.current_sign
        self.link_xslots_scene = QGraphicsScene()
        if self.mainwindow.app_settings['signdefaults']['xslot_generation'] != 'none' and sign.xslotstructure is not None:
            xslotrects = {}
            numwholes = sign.xslotstructure.number
            # partial = max([p.numerator/p.denominator for p in sign.xslotstructure.partials+[Fraction(0, 1)]])
            partial = float(sign.xslotstructure.additionalfraction)

            xslot_width = 1980 / (numwholes + (1 if partial > 0 else 0))
            if numwholes + partial > 0:
                for i in range(numwholes):
                    xslotrect = XslotRect(self, text="x" + str(i + 1), moduletype='xslot', sign=sign, mainwindow=self.mainwindow)
                    xloc = 0 + i * xslot_width - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, 0, xslot_width, 50)
                    xslotrect.setPen(self.blackpen)
                    xslotrect.setBrush(self.greenbrush)
                    xslotrects["x"+str(i+1)] = xslotrect
                    # xslotrect.rect_clicked.connect(lambda moduletype: self.handle_rect_clicked(moduletype))
                    self.link_xslots_scene.addItem(xslotrect)
                if partial > 0:
                    xslotrect = XslotRectButton(self, text="x" + str(numwholes + 1), moduletype='xslot', sign=sign, mainwindow=self.mainwindow, proportionfill=partial)
                    xloc = 0 + numwholes * xslot_width - (2 * self.blackpen.width())
                    xslotrect.setRect(xloc, 0, xslot_width * partial, 50)
                    xslotrect.setPen(self.blackpen)
                    xslotrect.setBrush(self.greenbrush)
                    xslotrects["x"+str(numwholes+1)] = xslotrect
                    # xslotrect.rect_clicked.connect(lambda moduletype: self.handle_rect_clicked(moduletype))
                    self.link_xslots_scene.addItem(xslotrect)

            self.link_xslots_view = QGraphicsView(self.link_xslots_scene)  # XslotGraphicsView(self.scene, self)
            # # self.link_from_view.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            self.link_xslots_view.setGeometry(0, 0, 2000, 50)
            # # self.setMinimumSize(1000,1000)
            self.linkinglayout.addWidget(self.link_xslots_view, 1, 1, 1, (numwholes + partial)*12+1)



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
        self.radio_radius = 20

        self.from_radios = {}
        self.to_radios = {}

        self.populate_radios(self.from_radios)
        self.populate_radios(self.to_radios)

    def populate_radios(self, radios):
        xslotstruct = self.mainwindow.current_sign.xslotstructure
        numwholes = xslotstruct.number
        additionalfrac = xslotstruct.additionalfraction
        partials = xslotstruct.fractionalpoints

        for whole in range(numwholes):
            if 




class XslotRadioCircle(QGraphicsEllipseItem):
    radiocircle_toggled = pyqtSignal((str, str))

    def __init__(self, xslot_whole, xslot_part, radius=20, penwidth=5, mainwindow=None):
        super().__init__()

        self.pencolour = Qt.darkGray
        self.brushcolour = Qt.black
        self.penwidth = penwidth
        self.radius = radius
        self.checked = False

        self.xslot_whole = xslot_whole
        self.xslot_part = xslot_part

    def paint(self, painter, option, widget):
        # super().paint(painter, option, widget)
        pen = painter.pen()
        pen.setColor(self.pencolour)
        pen.setWidth(self.penwidth)
        painter.setPen(pen)

        brush = painter.brush()
        if self.checked:
            brush.setStyle(Qt.SolidPattern)
            brush.setColor(self.brushcolour)
        else:
            brush.setStyle(Qt.NoBrush)
        painter.setBrush(brush)

        painter.drawEllipse(self.radius)

    def mouseReleaseEvent(self, event):
        # print("rectangle released")
        # QMessageBox.information(self.parentwidget, 'Rectangle clicked', 'You clicked the '+self.text+' rectangle!')
        self.toggle()

    def toggle(self):
        self.checked = not self.checked
        self.update()
        self.radiocircle_toggled.emit((self.xslot_whole, self.xslot_part))
