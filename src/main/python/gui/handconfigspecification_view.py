from copy import deepcopy
from itertools import chain

from PyQt5.QtCore import (
    Qt,
    QSize,
    pyqtSignal,
    QEvent
)
from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QScrollArea,
    QLineEdit,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QGroupBox,
    QSizePolicy,
    QCompleter,
    QPushButton,
    QCheckBox
)

from PyQt5.QtGui import (
    QPixmap
)

from constant import NULL, X_IN_BOX, PREDEFINED_MAP
from lexicon.predefined_handshape import HandshapeNoMatch
from lexicon.module_classes import AddedInfo, HandConfigurationModule, HandConfigurationHand
from gui.predefined_handshape_dialog import PredefinedHandshapeDialog
from gui.modulespecification_widgets import AddedInfoContextMenu, ModuleSpecificationPanel
from gui.undo_command import TranscriptionUndoCommand
from gui.link_help import show_help

# redefine from imported value
PREDEFINED_MAP = {handshape.canonical: handshape for handshape in PREDEFINED_MAP.values()}


class ConfigSlot(QLineEdit):
    slot_num_on_focus = pyqtSignal(str)
    slot_on_focus = pyqtSignal(str)
    slot_leave = pyqtSignal()
    slot_finish_edit = pyqtSignal(QLineEdit, dict, dict)

    def __init__(self, completer_options, descriptions, **kwargs):
        super().__init__(**kwargs)
        self.addedinfo = AddedInfo()

        # styling
        self.setFixedSize(QSize(20, 20))  # TODO KV
        qss = """   
            QLineEdit {
                background: white;
                color: black;
                text-align: center;
                margin: 0;
                padding: 0;
            }

            QLineEdit:disabled {
                color: gray;
            }

            QLineEdit[AddedInfo=true] {
                font-weight: bold;
                border: 2px dashed black;
            }

            QLineEdit[AddedInfo=false] {
                font-weight: normal;
                border: 1px solid grey;
            }
        """
        self.setStyleSheet(qss)
        self.updateStyle()

        # set completer
        completer = QCompleter(completer_options, parent=self)
        completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        popup = completer.popup()
        popup.setFixedWidth(200)
        completer.setPopup(popup)
        self.setCompleter(completer)

        self.num = descriptions[1]
        self.description = 'Field type: {f_type}; Slot number: {s_num}; Slot type: {s_type}'.format(
            f_type=descriptions[0],
            s_num=descriptions[1],
            s_type=descriptions[2])

        self.current_prop = self.get_value()
        self.textChanged.connect(self.on_text_changed)

        self.editingFinished.connect(self.handle_editing_finished)

    def handle_editing_finished(self):
        self.slot_finish_edit.emit(self, self.current_prop, self.get_value())
        self.current_prop = self.get_value()

    def clear(self):
        if self.num not in {'8', '9', '16', '21', '26', '31'}:
            super().clear()
            self.addedinfo = AddedInfo()
            self.updateStyle()

    def set_value_from_dict(self, d):
        self.setText(d['symbol'])
        self.addedinfo = d['addedinfo']
        self.updateStyle()

    def set_value(self, slot):
        self.setText(slot.symbol)
        self.addedinfo = slot.addedinfo
        self.updateStyle()

    def contextMenuEvent(self, event):
        addedinfo_menu = AddedInfoContextMenu(self.addedinfo)
        addedinfo_menu.info_added.connect(self.updateStyle)
        addedinfo_menu.exec_(event.globalPos())

    def mousePressEvent(self, event):
        if event.type() == QEvent.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                self.completer().complete()
        super().mousePressEvent(event)

    def focusInEvent(self, event):
        self.slot_on_focus.emit(self.description)
        self.slot_num_on_focus.emit(self.num)
        super().focusInEvent(event)

    def on_text_changed(self, text):
        self.setText(text.split(sep=' ')[0])

    def enterEvent(self, event):
        self.slot_on_focus.emit(self.description)
        self.slot_num_on_focus.emit(self.num)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.slot_leave.emit()
        super().leaveEvent(event)

    def get_value(self):
        return {'slot_number': int(self.num), 'symbol': self.text(), 'addedinfo': self.addedinfo}

    def updateStyle(self):
        self.setProperty('AddedInfo', self.addedinfo.hascontent())
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class ConfigField(QWidget):
    slot_num_on_focus = pyqtSignal(str)
    slot_on_focus = pyqtSignal(str)
    slot_leave = pyqtSignal()
    slot_changed = pyqtSignal()
    slot_finish_edit = pyqtSignal(QLineEdit, dict, dict)

    def __init__(self, field_number, parent=None):
        super().__init__(parent=parent)
        self.field_number = field_number

        # styling
        self.setStyleSheet('QWidget{margin: 0; padding: 0;}')

        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(0)
        self.main_layout.addStretch()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        # testing...
        left_bracket = QLabel('[')
        bracketfont = left_bracket.font()
        bracketfont.setPixelSize(20)
        left_bracket.setFont(bracketfont)
        left_bracket.setFixedSize(QSize(10, 30))
        left_bracket.setAlignment(Qt.AlignHCenter)
        left_bracket.setAlignment(Qt.AlignVCenter)
        self.main_layout.addWidget(left_bracket)

        right_bracket = QLabel(']')
        right_bracket.setFont(bracketfont)
        right_number = QLabel(str(self.field_number))
        right_number.setFont(bracketfont)
        right_bracket.setFixedSize(QSize(10, 30))
        right_number.setFixedSize(QSize(20, 30))
        right_bracket.setAlignment(Qt.AlignCenter)
        right_number.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(right_bracket)
        self.main_layout.addWidget(right_number)

        self.generate_slots()

        # styling
        #self.setStyleSheet('QWidget{margin: 0; padding: 0; border:1px solid rgb(0, 255, 0);}')

    def insert_slot(self, slot):
        position = self.main_layout.count() - 2
        self.main_layout.insertWidget(position, slot)

    def clear(self):
        if self.field_number == 2:
            self.slot2.clear()
            self.slot3.clear()
            self.slot4.clear()
            self.slot5.clear()
        elif self.field_number == 3:
            self.slot6.clear()
            self.slot7.clear()
            self.slot8.clear()
            self.slot9.clear()
            self.slot10.clear()
            self.slot11.clear()
            self.slot12.clear()
            self.slot13.clear()
            self.slot14.clear()
            self.slot15.clear()
        elif self.field_number == 4:
            self.slot16.clear()
            self.slot17.clear()
            self.slot18.clear()
            self.slot19.clear()
        elif self.field_number == 5:
            self.slot20.clear()
            self.slot21.clear()
            self.slot22.clear()
            self.slot23.clear()
            self.slot24.clear()
        elif self.field_number == 6:
            self.slot25.clear()
            self.slot26.clear()
            self.slot27.clear()
            self.slot28.clear()
            self.slot29.clear()
        elif self.field_number == 7:
            self.slot30.clear()
            self.slot31.clear()
            self.slot32.clear()
            self.slot33.clear()
            self.slot34.clear()

    def set_value(self, field):
        if self.field_number == 2:
            self.slot2.set_value(field.slot2)
            self.slot3.set_value(field.slot3)
            self.slot4.set_value(field.slot4)
            self.slot5.set_value(field.slot5)
        elif self.field_number == 3:
            self.slot6.set_value(field.slot6)
            self.slot7.set_value(field.slot7)
            self.slot8.set_value(field.slot8)
            self.slot9.set_value(field.slot9)
            self.slot10.set_value(field.slot10)
            self.slot11.set_value(field.slot11)
            self.slot12.set_value(field.slot12)
            self.slot13.set_value(field.slot13)
            self.slot14.set_value(field.slot14)
            self.slot15.set_value(field.slot15)
        elif self.field_number == 4:
            self.slot16.set_value(field.slot16)
            self.slot17.set_value(field.slot17)
            self.slot18.set_value(field.slot18)
            self.slot19.set_value(field.slot19)
        elif self.field_number == 5:
            self.slot20.set_value(field.slot20)
            self.slot21.set_value(field.slot21)
            self.slot22.set_value(field.slot22)
            self.slot23.set_value(field.slot23)
            self.slot24.set_value(field.slot24)
        elif self.field_number == 6:
            self.slot25.set_value(field.slot25)
            self.slot26.set_value(field.slot26)
            self.slot27.set_value(field.slot27)
            self.slot28.set_value(field.slot28)
            self.slot29.set_value(field.slot29)
        elif self.field_number == 7:
            self.slot30.set_value(field.slot30)
            self.slot31.set_value(field.slot31)
            self.slot32.set_value(field.slot32)
            self.slot33.set_value(field.slot33)
            self.slot34.set_value(field.slot34)

    def hasFocus(self):
        return any(slot.hasFocus() for slot in self.__iter__())

    def __iter__(self):
        if self.field_number == 2:
            return [self.slot2, self.slot3, self.slot4, self.slot5].__iter__()
        elif self.field_number == 3:
            return [self.slot6, self.slot7, self.slot8, self.slot9, self.slot10, self.slot11, self.slot12, self.slot13,
                    self.slot14, self.slot15].__iter__()
        elif self.field_number == 4:
            return [self.slot16, self.slot17, self.slot18, self.slot19].__iter__()
        elif self.field_number == 5:
            return [self.slot20, self.slot21, self.slot22, self.slot23, self.slot24].__iter__()
        elif self.field_number == 6:
            return [self.slot25, self.slot26, self.slot27, self.slot28, self.slot29].__iter__()
        elif self.field_number == 7:
            return [self.slot30, self.slot31, self.slot32, self.slot33, self.slot34].__iter__()

    def generate_slots(self):
        if self.field_number == 2:
            self.slot2 = ConfigSlot(['L [lateral]', 'U [unopposed]', 'O [opposed]', '? [unestimatable]'],
                                    ['thumb', '2', 'thumb oppositional positions (CM rotation)'],
                                    parent=self)
            self.slot2.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot2.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot2.slot_leave.connect(self.slot_leave.emit)
            self.slot2.textChanged.connect(self.slot_changed.emit)
            self.slot2.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot2)

            self.slot3 = ConfigSlot(['{ [full abduction]', '< [neutral]', '= [adducted]', '? [unestimatable]'],
                                    ['thumb', '3', 'thumb abduction/adduction (CM adduction)'],
                                    parent=self)
            self.slot3.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot3.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot3.slot_leave.connect(self.slot_leave.emit)
            self.slot3.textChanged.connect(self.slot_changed.emit)
            self.slot3.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot3)

            self.slot4 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['thumb', '4', 'thumb MCP flexion'],
                parent=self)
            self.slot4.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot4.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot4.slot_leave.connect(self.slot_leave.emit)
            self.slot4.textChanged.connect(self.slot_changed.emit)
            self.slot4.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot4)

            self.slot5 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['thumb', '5', 'thumb DIP flexion'],
                parent=self)
            self.slot5.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot5.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot5.slot_leave.connect(self.slot_leave.emit)
            self.slot5.textChanged.connect(self.slot_changed.emit)
            self.slot5.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot5)

        elif self.field_number == 3:
            self.slot6 = ConfigSlot(
                ['- [no contact]', 't [tip]', 'fr [friction surface]', 'b [back surface]', 'r [radial surface]',
                 'u [ulnar surface]', '? [unestimatable]'],
                ['thumb/finger contact', '6', 'thumb surface options'],
                parent=self)
            self.slot6.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot6.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot6.slot_leave.connect(self.slot_leave.emit)
            self.slot6.textChanged.connect(self.slot_changed.emit)
            self.slot6.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot6)

            self.slot7 = ConfigSlot(
                ['- [no contact]', 'd [distal]', 'p [proximal]', 'M [meta-carpal]', '? [unestimatable]'],
                ['thumb/finger contact', '7', 'thumb bone options'],
                parent=self)
            self.slot7.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot7.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot7.slot_leave.connect(self.slot_leave.emit)
            self.slot7.textChanged.connect(self.slot_changed.emit)
            self.slot7.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot7)

            self.slot8 = ConfigSlot(
                [],
                ['thumb/finger contact', '8', ''],
                parent=self)
            self.slot8.setText(NULL)
            self.slot8.setEnabled(False)
            self.slot8.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot8.slot_leave.connect(self.slot_leave.emit)
            self.slot8.textChanged.connect(self.slot_changed.emit)
            self.slot8.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot8)

            self.slot9 = ConfigSlot(
                [],
                ['thumb/finger contact', '9', ''],
                parent=self)
            self.slot9.setText('/')
            self.slot9.setEnabled(False)
            self.slot9.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot9.slot_leave.connect(self.slot_leave.emit)
            self.slot9.textChanged.connect(self.slot_changed.emit)
            self.slot9.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot9)

            self.slot10 = ConfigSlot(
                ['- [no contact]', 't [tip]', 'fr [friction surface]', 'b [back surface]', 'r [radial surface]',
                 'u [ulnar surface]', '? [unestimatable]'],
                ['thumb/finger contact', '10', 'finger surface options'],
                parent=self)
            self.slot10.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot10.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot10.slot_leave.connect(self.slot_leave.emit)
            self.slot10.textChanged.connect(self.slot_changed.emit)
            self.slot10.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot10)

            self.slot11 = ConfigSlot(
                ['- [no contact]', 'd [distal]', 'm [medial]', 'p [proximal]', 'M [meta-carpal]', '? [unestimatable]'],
                ['thumb/finger contact', '11', 'finger bone options'],
                parent=self)
            self.slot11.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot11.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot11.slot_leave.connect(self.slot_leave.emit)
            self.slot11.textChanged.connect(self.slot_changed.emit)
            self.slot11.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot11)

            self.slot12 = ConfigSlot(
                ['- [no contact]', '1 [contact with index finger]', '? [unestimatable]'],
                ['thumb/finger contact', '12', 'index/thumb contact'],
                parent=self)
            self.slot12.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot12.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot12.slot_leave.connect(self.slot_leave.emit)
            self.slot12.textChanged.connect(self.slot_changed.emit)
            self.slot12.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot12)

            self.slot13 = ConfigSlot(
                ['- [no contact]', '2 [contact with middle finger]', '? [unestimatable]'],
                ['thumb/finger contact', '13', 'middle/thumb contact'],
                parent=self)
            self.slot13.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot13.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot13.slot_leave.connect(self.slot_leave.emit)
            self.slot13.textChanged.connect(self.slot_changed.emit)
            self.slot13.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot13)

            self.slot14 = ConfigSlot(
                ['- [no contact]', '3 [contact with ring finger]', '? [unestimatable]'],
                ['thumb/finger contact', '14', 'ring/thumb contact'],
                parent=self)
            self.slot14.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot14.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot14.slot_leave.connect(self.slot_leave.emit)
            self.slot14.textChanged.connect(self.slot_changed.emit)
            self.slot14.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot14)

            self.slot15 = ConfigSlot(
                ['- [no contact]', '4 [contact with pinky finger]', '? [unestimatable]'],
                ['thumb/finger contact', '15', 'pinky/thumb contact'],
                parent=self)
            self.slot15.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot15.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot15.slot_leave.connect(self.slot_leave.emit)
            self.slot15.textChanged.connect(self.slot_changed.emit)
            self.slot15.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot15)

        elif self.field_number == 4:
            self.slot16 = ConfigSlot(
                [],
                ['index finger', '16', ''],
                parent=self)
            self.slot16.setText('1')
            self.slot16.setEnabled(False)
            self.slot16.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot16.slot_leave.connect(self.slot_leave.emit)
            self.slot16.textChanged.connect(self.slot_changed.emit)
            self.slot16.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot16)

            self.slot17 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['index finger', '17', 'index MCP flexion'],
                parent=self)
            self.slot17.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot17.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot17.slot_leave.connect(self.slot_leave.emit)
            self.slot17.textChanged.connect(self.slot_changed.emit)
            self.slot17.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot17)

            self.slot18 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['index finger', '18', 'index PIP flexion'],
                parent=self)
            self.slot18.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot18.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot18.slot_leave.connect(self.slot_leave.emit)
            self.slot18.textChanged.connect(self.slot_changed.emit)
            self.slot18.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot18)

            self.slot19 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['index finger', '19', 'index DIP flexion'],
                parent=self)
            self.slot19.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot19.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot19.slot_leave.connect(self.slot_leave.emit)
            self.slot19.textChanged.connect(self.slot_changed.emit)
            self.slot19.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot19)

        elif self.field_number == 5:
            self.slot20 = ConfigSlot(
                ['{ [full abduction]', '< [neutral]', '= [adducted]', 'x- [slightly crossed with contact]',
                 'x [crossed with contact]', 'x+ [ultracrossed]', X_IN_BOX + ' [crossed without contact]',
                 '? [unestimatable]'],
                ['middle finger', '20', 'index/middle contact'],
                parent=self)
            self.slot20.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot20.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot20.slot_leave.connect(self.slot_leave.emit)
            self.slot20.textChanged.connect(self.slot_changed.emit)
            self.slot20.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot20)

            self.slot21 = ConfigSlot(
                [],
                ['middle finger', '21', ''],
                parent=self)
            self.slot21.setText('2')
            self.slot21.setEnabled(False)
            self.slot21.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot21.slot_leave.connect(self.slot_leave.emit)
            self.slot21.textChanged.connect(self.slot_changed.emit)
            self.slot21.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot21)

            self.slot22 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['middle finger', '22', 'middle MCP flexion'],
                parent=self)
            self.slot22.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot22.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot22.slot_leave.connect(self.slot_leave.emit)
            self.slot22.textChanged.connect(self.slot_changed.emit)
            self.slot22.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot22)

            self.slot23 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['middle finger', '23', 'middle PIP flexion'],
                parent=self)
            self.slot23.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot23.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot23.slot_leave.connect(self.slot_leave.emit)
            self.slot23.textChanged.connect(self.slot_changed.emit)
            self.slot23.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot23)

            self.slot24 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['middle finger', '24', 'middle DIP flexion'],
                parent=self)
            self.slot24.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot24.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot24.slot_leave.connect(self.slot_leave.emit)
            self.slot24.textChanged.connect(self.slot_changed.emit)
            self.slot24.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot24)

        elif self.field_number == 6:
            self.slot25 = ConfigSlot(
                ['{ [full abduction]', '< [neutral]', '= [adducted]', 'x- [slightly crossed with contact]',
                 'x [crossed with contact]', 'x+ [ultracrossed]', X_IN_BOX + ' [crossed without contact]',
                 '? [unestimatable]'],
                ['ring finger', '25', 'middle/ring contact'],
                parent=self)
            self.slot25.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot25.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot25.slot_leave.connect(self.slot_leave.emit)
            self.slot25.textChanged.connect(self.slot_changed.emit)
            self.slot25.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot25)

            self.slot26 = ConfigSlot(
                [],
                ['ring finger', '26', ''],
                parent=self)
            self.slot26.setText('3')
            self.slot26.setEnabled(False)
            self.slot26.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot26.slot_leave.connect(self.slot_leave.emit)
            self.slot26.textChanged.connect(self.slot_changed.emit)
            self.slot26.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot26)

            self.slot27 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['ring finger', '27', 'Ring MCP flexion'],
                parent=self)
            self.slot27.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot27.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot27.slot_leave.connect(self.slot_leave.emit)
            self.slot27.textChanged.connect(self.slot_changed.emit)
            self.slot27.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot27)

            self.slot28 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['ring finger', '28', 'Ring PIP flexion'],
                parent=self)
            self.slot28.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot28.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot28.slot_leave.connect(self.slot_leave.emit)
            self.slot28.textChanged.connect(self.slot_changed.emit)
            self.slot28.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot28)

            self.slot29 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['ring finger', '29', 'Ring DIP flexion'],
                parent=self)
            self.slot29.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot29.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot29.slot_leave.connect(self.slot_leave.emit)
            self.slot29.textChanged.connect(self.slot_changed.emit)
            self.slot29.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot29)

        elif self.field_number == 7:
            self.slot30 = ConfigSlot(
                ['{ [full abduction]', '< [neutral]', '= [adducted]', 'x- [slightly crossed with contact]',
                 'x [crossed with contact]', 'x+ [ultracrossed]', X_IN_BOX + ' [crossed without contact]',
                 '? [unestimatable]'],
                ['pinky finger', '30', 'ring/pinky contact'],
                parent=self)
            self.slot30.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot30.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot30.slot_leave.connect(self.slot_leave.emit)
            self.slot30.textChanged.connect(self.slot_changed.emit)
            self.slot30.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot30)

            self.slot31 = ConfigSlot(
                [],
                ['pinky finger', '31', ''],
                parent=self)
            self.slot31.setText('4')
            self.slot31.setEnabled(False)
            self.slot31.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot31.slot_leave.connect(self.slot_leave.emit)
            self.slot31.textChanged.connect(self.slot_changed.emit)
            self.slot31.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot31)

            self.slot32 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['pinky finger', '32', 'Pinky MCP flexion'],
                parent=self)
            self.slot32.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot32.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot32.slot_leave.connect(self.slot_leave.emit)
            self.slot32.textChanged.connect(self.slot_changed.emit)
            self.slot32.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot32)

            self.slot33 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['pinky finger', '33', 'Pinky PIP flexion'],
                parent=self)
            self.slot33.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot33.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot33.slot_leave.connect(self.slot_leave.emit)
            self.slot33.textChanged.connect(self.slot_changed.emit)
            self.slot33.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot33)

            self.slot34 = ConfigSlot(
                ['H [hyperextended]', 'E [fully extended]', 'e [somewhat extended]', 'i [clearly intermediate]',
                 'F [fully flexed]', 'f [somewhat flexed]', '? [unestimatable]'],
                ['pinky finger', '34', 'Pinky DIP flexion'],
                parent=self)
            self.slot34.slot_on_focus.connect(self.slot_on_focus.emit)
            self.slot34.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
            self.slot34.slot_leave.connect(self.slot_leave.emit)
            self.slot34.textChanged.connect(self.slot_changed.emit)
            self.slot34.slot_finish_edit.connect(self.slot_finish_edit.emit)
            self.insert_slot(self.slot34)

    def get_value(self):
        if self.field_number == 2:
            return {
                'field_number': self.field_number,
                'slots': [
                    self.slot2.get_value(),
                    self.slot3.get_value(),
                    self.slot4.get_value(),
                    self.slot5.get_value()
                ]
            }
        elif self.field_number == 3:
            return {
                'field_number': self.field_number,
                'slots': [
                    self.slot6.get_value(),
                    self.slot7.get_value(),
                    self.slot8.get_value(),
                    self.slot9.get_value(),
                    self.slot10.get_value(),
                    self.slot11.get_value(),
                    self.slot12.get_value(),
                    self.slot13.get_value(),
                    self.slot14.get_value(),
                    self.slot15.get_value()
                ]
            }
        elif self.field_number == 4:
            return {
                'field_number': self.field_number,
                'slots': [
                    self.slot16.get_value(),
                    self.slot17.get_value(),
                    self.slot18.get_value(),
                    self.slot19.get_value()
                ]
            }
        elif self.field_number == 5:
            return {
                'field_number': self.field_number,
                'slots': [
                    self.slot20.get_value(),
                    self.slot21.get_value(),
                    self.slot22.get_value(),
                    self.slot23.get_value(),
                    self.slot24.get_value()
                ]
            }
        elif self.field_number == 6:
            return {
                'field_number': self.field_number,
                'slots': [
                    self.slot25.get_value(),
                    self.slot26.get_value(),
                    self.slot27.get_value(),
                    self.slot28.get_value(),
                    self.slot29.get_value()
                ]
            }
        elif self.field_number == 7:
            return {
                'field_number': self.field_number,
                'slots': [
                    self.slot30.get_value(),
                    self.slot31.get_value(),
                    self.slot32.get_value(),
                    self.slot33.get_value(),
                    self.slot34.get_value()
                ]
            }


class ConfigHand(QWidget):
    slot_num_on_focus = pyqtSignal(str)
    slot_on_focus = pyqtSignal(str)
    slot_leave = pyqtSignal()
    slot_finish_edit = pyqtSignal(QLineEdit, dict, dict)

    def __init__(self, predefined_ctx, parent=None):
        super().__init__(parent=parent)
        # self.hand_number = hand_number
        self.predefined_ctx = predefined_ctx
        self.setStyleSheet('QWidget{margin: 0; padding: 0}')

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.addStretch()
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self.generate_fields()  # generate slots 2 to 7 that gets placed next to the 'load predefined' btn

        self.preview_clearbtn_layout = QHBoxLayout()  # layout for predefined image, predefined label, and clear btn
        self.predefined_image = QLabel()
        self.predefined_image.setToolTip('Predefined handshape image matching the current transcription')
        self.predefined_image.setFixedSize(100, 100)
        handshape_image = QPixmap(self.predefined_ctx['empty'])
        self.predefined_image.setPixmap(
            handshape_image.scaled(self.predefined_image.width(), self.predefined_image.height(), Qt.KeepAspectRatio)
        )
        self.preview_clearbtn_layout.addWidget(self.predefined_image)

        self.predefined_label = QLabel('empty')
        self.predefined_label.setFixedSize(150, 20)
        self.predefined_label.setStyleSheet('background-color: darkgray;'
                                            'border-style: outset;'
                                            'border-color: black;'
                                            'border-width: 1px;')
        self.preview_clearbtn_layout.addWidget(self.predefined_label)

        clear_button = QPushButton('Clear', parent=self)
        clear_button.setFixedWidth(75)
        clear_button.setContentsMargins(0, 0, 0, 0)
        clear_button.clicked.connect(self.clear)
        self.preview_clearbtn_layout.addWidget(clear_button)
        self.main_layout.addLayout(self.preview_clearbtn_layout)

    def hasFocus(self):
        return any(field.hasFocus() for field in self.__iter__())

    def __iter__(self):
        return chain(iter(self.field2), iter(self.field3), iter(self.field4), iter(self.field5), iter(self.field6),
                     iter(self.field7))

    def get_hand_transcription_list(self):
        return [slot.text() for slot in self.__iter__()]

    def get_hand_transcription_string(self):
        return ''.join([slot.text() for slot in self.__iter__()])

    def set_value(self, hand):
        self.field2.set_value(hand.field2)
        self.field3.set_value(hand.field3)
        self.field4.set_value(hand.field4)
        self.field5.set_value(hand.field5)
        self.field6.set_value(hand.field6)
        self.field7.set_value(hand.field7)

    def clear(self):
        self.field2.clear()
        self.field3.clear()
        self.field4.clear()
        self.field5.clear()
        self.field6.clear()
        self.field7.clear()

    def update_predefined_image_text(self):
        transcription = tuple(self.get_hand_transcription_list())
        image = QPixmap(self.predefined_ctx[PREDEFINED_MAP.get(transcription, HandshapeNoMatch()).filename])
        name = PREDEFINED_MAP.get(transcription, HandshapeNoMatch()).name

        self.predefined_label.setText(name)
        self.predefined_label.setToolTip('Matched handshape: ' + name)
        self.predefined_image.setPixmap(
            image.scaled(self.predefined_image.width(), self.predefined_image.height(), Qt.KeepAspectRatio)
        )
        self.repaint()

    def generate_fields(self):
        field23_layout = QHBoxLayout()    # layout for fields 2-3. to be added to main_layout
        field4567_layout = QHBoxLayout()  # layout for fields 4-7. to be added to main_layout

        self.field2 = ConfigField(2, parent=self)
        self.field2.slot_on_focus.connect(self.slot_on_focus.emit)
        self.field2.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.field2.slot_leave.connect(self.slot_leave.emit)
        self.field2.slot_changed.connect(self.update_predefined_image_text)
        self.field2.slot_finish_edit.connect(self.slot_finish_edit.emit)
        field23_layout.addWidget(self.field2)

        self.field3 = ConfigField(3, parent=self)
        self.field3.slot_on_focus.connect(self.slot_on_focus.emit)
        self.field3.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.field3.slot_leave.connect(self.slot_leave.emit)
        self.field3.slot_changed.connect(self.update_predefined_image_text)
        self.field3.slot_finish_edit.connect(self.slot_finish_edit.emit)
        field23_layout.addWidget(self.field3)

        self.field4 = ConfigField(4, parent=self)
        self.field4.slot_on_focus.connect(self.slot_on_focus.emit)
        self.field4.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.field4.slot_leave.connect(self.slot_leave.emit)
        self.field4.slot_changed.connect(self.update_predefined_image_text)
        self.field4.slot_finish_edit.connect(self.slot_finish_edit.emit)
        field4567_layout.addWidget(self.field4)

        self.field5 = ConfigField(5, parent=self)
        self.field5.slot_on_focus.connect(self.slot_on_focus.emit)
        self.field5.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.field5.slot_leave.connect(self.slot_leave.emit)
        self.field5.slot_changed.connect(self.update_predefined_image_text)
        self.field5.slot_finish_edit.connect(self.slot_finish_edit.emit)
        field4567_layout.addWidget(self.field5)

        self.field6 = ConfigField(6, parent=self)
        self.field6.slot_on_focus.connect(self.slot_on_focus.emit)
        self.field6.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.field6.slot_leave.connect(self.slot_leave.emit)
        self.field6.slot_changed.connect(self.update_predefined_image_text)
        self.field6.slot_finish_edit.connect(self.slot_finish_edit.emit)
        field4567_layout.addWidget(self.field6)

        self.field7 = ConfigField(7, parent=self)
        self.field7.slot_on_focus.connect(self.slot_on_focus.emit)
        self.field7.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.field7.slot_leave.connect(self.slot_leave.emit)
        self.field7.slot_changed.connect(self.update_predefined_image_text)
        self.field7.slot_finish_edit.connect(self.slot_finish_edit.emit)
        field4567_layout.addWidget(self.field7)

        self.main_layout.addLayout(field23_layout)
        self.main_layout.addLayout(field4567_layout)

    def set_predefined(self, transcription_list):
        for symbol, slot in zip(transcription_list, self.__iter__()):
            slot.setText(symbol)

    def get_value(self):

        return [
                self.field2.get_value(),
                self.field3.get_value(),
                self.field4.get_value(),
                self.field5.get_value(),
                self.field6.get_value(),
                self.field7.get_value()
            ]


class Config(QGroupBox):
    slot_num_on_focus = pyqtSignal(str)
    slot_on_focus = pyqtSignal(str)
    slot_leave = pyqtSignal()
    slot_finish_edit = pyqtSignal(QLineEdit, dict, dict)

    def __init__(self, predefined_ctx, **kwargs):
        super().__init__(title='Hand Configuration', **kwargs)
        self.predefined_ctx = predefined_ctx
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        # self.setStyleSheet('QGroupBox{margin: 0; padding: 0}')

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.addStretch()
        # self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        self._addedinfo = AddedInfo()
        self.add_slot1()
        self.generate_hands()

    def add_slot1(self):
        slot1_box = QGroupBox(parent=self)
        slot1_layout = QHBoxLayout()
        slot1_layout.setSpacing(5)

        left_bracket = QLabel('[')
        bracketfont = left_bracket.font()
        bracketfont.setPixelSize(20)
        left_bracket.setFont(bracketfont)
        left_bracket.setFixedSize(QSize(10, 30))
        left_bracket.setAlignment(Qt.AlignCenter)
        slot1_layout.addWidget(left_bracket)

        self.slot1 = ForearmCheckBox('Forearm', parent=self)
        slot1_layout.addWidget(self.slot1)

        right_bracket = QLabel(']1')
        right_bracket.setFont(bracketfont)
        right_bracket.setFixedSize(QSize(22, 30))
        right_bracket.setAlignment(Qt.AlignCenter)
        slot1_layout.addWidget(right_bracket)

        slot1_layout.addStretch()

        slot1_box.setLayout(slot1_layout)
        self.main_layout.addWidget(slot1_box)

    def generate_hands(self):
        self.hand = ConfigHand(self.predefined_ctx, parent=self)  # 1,
        self.hand.slot_on_focus.connect(self.slot_on_focus.emit)
        self.hand.slot_num_on_focus.connect(self.slot_num_on_focus.emit)
        self.hand.slot_leave.connect(self.slot_leave.emit)
        self.hand.slot_finish_edit.connect(self.slot_finish_edit.emit)

        self.predefined_button = QPushButton("Load predefined handshape".replace(" ", "\n"))
        self.predefined_button.clicked.connect(self.load_predefined)
        predefined_help_btn = QPushButton(" Help ".replace(" ", "\n"))
        predefined_help_btn.clicked.connect(lambda: show_help("predefined_handshapes"))
        hand_box = QGroupBox(parent=self)
        hand_layout = QHBoxLayout()
        hand_layout.setSpacing(5)
        hand_box.setLayout(hand_layout)

        predefined_layout = QVBoxLayout()
        predefined_layout.addWidget(self.predefined_button)
        predefined_layout.addWidget(predefined_help_btn)
        predefined_layout.addStretch()

        hand_layout.addLayout(predefined_layout)
        hand_layout.addWidget(self.hand)
        self.main_layout.addWidget(hand_box)

    def load_predefined(self):
        predefined_handshape_dialog = PredefinedHandshapeDialog(self.predefined_ctx, parent=self)
        predefined_handshape_dialog.transcription.connect(self.handle_set_predefined)
        predefined_handshape_dialog.exec_()

    def handle_set_predefined(self, transcription_list):
        self.hand.set_predefined(transcription_list)

    def set_value(self, handconfigmodule):
        self.hand.set_value(HandConfigurationHand(handconfigmodule.handconfiguration))
        self.slot1.setChecked(handconfigmodule.overalloptions['forearm'])
        self.slot1.addedinfo = handconfigmodule.overalloptions['forearm_addedinfo']
        self._addedinfo = handconfigmodule.overalloptions['overall_addedinfo']

    def clear(self):
        self.hand.clear()
        self.slot1.setChecked(False)
        self.slot1.addedinfo = AddedInfo()
        self._addedinfo = AddedInfo()

    def get_value(self):
        return {
            'forearm': self.slot1.isChecked(),
            'forearm_addedinfo': self.slot1.addedinfo,
            'hand': self.hand.get_value(),  # this is a list of field values
            'overall_addedinfo': self._addedinfo
        }


class ForearmCheckBox(QCheckBox):

    def __init__(self, title, **kwargs):
        super().__init__(title, **kwargs)
        self._addedinfo = AddedInfo()

        # styling
        qss = """   
            QCheckBox[AddedInfo=true] {
                font: bold;
                /*border: 2px dashed black;*/
            }

            QCheckBox[AddedInfo=false] {
                font: normal;
                /*border: 1px solid grey;*/
            }
        """
        self.setStyleSheet(qss)
        self.updateStyle()

    @property
    def addedinfo(self):
        return self._addedinfo

    @addedinfo.setter
    def addedinfo(self, addedinfo):
        self._addedinfo = addedinfo if addedinfo is not None else AddedInfo()
        self.updateStyle()

    def contextMenuEvent(self, event):
        addedinfo_menu = AddedInfoContextMenu(self._addedinfo)
        addedinfo_menu.info_added.connect(self.updateStyle)
        addedinfo_menu.exec_(event.globalPos())

    def updateStyle(self, addedinfo=None):
        if addedinfo is not None:
            self._addedinfo = addedinfo
        self.setProperty('AddedInfo', self._addedinfo.hascontent())
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()


class HandConfigSpecificationPanel(ModuleSpecificationPanel):

    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow

        self.panel = HandTranscriptionPanel(self.mainwindow.app_ctx.predefined)
        self.panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding) 
        self.illustration = HandIllustrationPanel(self.mainwindow.app_ctx, parent=self)
        self.illustration.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)  # (QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.panel.config.slot_on_focus.connect(self.panel.update_details_label)
        self.panel.config.slot_num_on_focus.connect(self.illustration.update_hand_illustration)
        self.panel.config.slot_leave.connect(self.panel.update_details_label)
        self.panel.config.slot_leave.connect(self.illustration.set_neutral_img)
        self.panel.config.slot_finish_edit.connect(self.handle_slot_edit)
        layout = self.create_layout()

        self.load_existing_module(moduletoload)
        
        self.setLayout(layout)
    
    def load_existing_module(self, moduletoload):
        if moduletoload:
            self.panel.set_value(deepcopy(moduletoload))
            self.existingkey = moduletoload.uniqueid

    
    def create_layout(self):
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.panel)
        main_layout.addWidget(self.illustration)
        return main_layout


    def handle_slot_edit(self, slot, old_prop, new_prop):
        undo_command = TranscriptionUndoCommand(slot, old_prop, new_prop)
        self.mainwindow.undostack.push(undo_command)

    def getsavedmodule(self, articulators, timingintervals, phonlocs, addedinfo, inphase):
        configdict = self.panel.config.get_value()
        handconfiguration = configdict['hand']
        overalloptions = {k: v for (k, v) in configdict.items() if k != 'hand'}

        hcfg = HandConfigurationModule(handconfiguration=handconfiguration,
                                       overalloptions=overalloptions,
                                       articulators=articulators,
                                       timingintervals=timingintervals,
                                       phonlocs=phonlocs,
                                       addedinfo=addedinfo)
        if self.existingkey is not None:
            hcfg.uniqueid = self.existingkey
        else:
            self.existingkey = hcfg.uniqueid
        return hcfg

    def refresh(self):
        self.clear()

    def clear(self):
        self.panel.clear()
        self.illustration.set_neutral_img()

    def desiredwidth(self):
        return 2000

    def desiredheight(self):
        return 400


class HandTranscriptionPanel(QScrollArea):
    selected_hand = pyqtSignal(int)

    def __init__(self, predefined_ctx, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        config_layout = QVBoxLayout()

        self.config = Config(predefined_ctx, parent=self)
        config_layout.addWidget(self.config)

        self.details_label = QLabel()
        config_layout.addWidget(self.details_label)

        main_layout.addLayout(config_layout)

        self.setWidget(main_frame)

    def sizeHint(self):
        return QSize(900, 400)

    def update_details_label(self, text=""):
        self.details_label.setText(text)

    def clear(self):
        self.config.clear()

    def set_value(self, handconfigmodule):
        self.config.set_value(handconfigmodule)

    def get_hand_transcription(self, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            return self.config.hand.get_hand_transcription_list()
        elif hand == 2:
            return self.config.hand2.get_hand_transcription_list()

    def set_predefined(self, transcription_list, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            self.config.hand.set_predefined(transcription_list)
        elif hand == 2:
            self.config.hand2.set_predefined(transcription_list)


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

    def update_hand_illustration(self, num):
        hand_img = QPixmap(self.app_ctx.hand_illustrations['slot' + str(num)])
        self.set_img(hand_img)

    def set_neutral_img(self):
        neutral_img = QPixmap(self.app_ctx.hand_illustrations['neutral'])
        self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        self.hand_illustration.repaint()

    def set_img(self, new_img):
        self.hand_illustration.setPixmap(
            new_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        self.hand_illustration.repaint()
