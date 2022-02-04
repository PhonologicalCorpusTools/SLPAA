import os
import json
from PyQt5.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFrame,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QListView,
    QVBoxLayout,
    QBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QSlider,
    QTreeView,
    QComboBox,
    QLabel,
    QCompleter,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView,
    QStyleOptionFrame,
    QErrorMessage,
    QButtonGroup,
    QRadioButton,
    QCheckBox,
    QGroupBox,
    QSpacerItem,
    QSizePolicy
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon
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

from .helper_widget import EditableTabBar
from copy import copy, deepcopy
from pprint import pprint


class SigntypeSpecificationLayout(QVBoxLayout):
    def __init__(self, app_ctx, **kwargs):
        super().__init__(**kwargs)

        # buttons and groups for highest level
        self.handstype_buttongroup = QButtonGroup(parent=self)
        self.handstype_unspec_radio = QRadioButton('Unspecified')
        self.handstype_unspec_radio.setProperty('handstype', 0)
        self.handstype_1h_radio = QRadioButton('1 hand')
        self.handstype_1h_radio.setProperty('handstype', 1)
        self.handstype_2h_radio = QRadioButton('2 hands')
        self.handstype_2h_radio.setProperty('handstype', 4)
        self.handstype_buttongroup.addButton(self.handstype_unspec_radio)
        self.handstype_buttongroup.addButton(self.handstype_1h_radio)
        self.handstype_buttongroup.addButton(self.handstype_2h_radio)

        # buttons and groups for 1-handed signs
        self.handstype_1h_buttongroup = QButtonGroup(parent=self)
        self.handstype_1hmove_radio = QRadioButton('The hand moves')
        self.handstype_1hmove_radio.setProperty('handstype', 2)
        self.handstype_1hnomove_radio = QRadioButton('The hand doesn\'t move')
        self.handstype_1hnomove_radio.setProperty('handstype', 3)
        self.handstype_1h_buttongroup.addButton(self.handstype_1hmove_radio)
        self.handstype_1h_buttongroup.addButton(self.handstype_1hnomove_radio)

        # buttons and groups for 2-handed handshape relation
        self.handstype_handshapereln_buttongroup = QButtonGroup(parent=self)
        self.handstype_2hsameshapes_radio = QRadioButton('H1 and H2 use same set(s) of handshapes')
        self.handstype_2hsameshapes_radio.setProperty('handstype', 5)
        self.handstype_2hdiffshapes_radio = QRadioButton('H1 and H2 use different set(s) of handshapes')
        self.handstype_2hdiffshapes_radio.setProperty('handstype', 6)
        self.handstype_handshapereln_buttongroup.addButton(self.handstype_2hsameshapes_radio)
        self.handstype_handshapereln_buttongroup.addButton(self.handstype_2hdiffshapes_radio)

        # buttons and groups for 2-handed contact relation
        self.handstype_contactreln_buttongroup = QButtonGroup(parent=self)
        self.handstype_2hcontactyes_radio = QRadioButton('H1 and H2 maintain contact throughout sign')
        self.handstype_2hcontactyes_radio.setProperty('handstype', 7)
        self.handstype_2hcontactno_radio = QRadioButton('H1 and H2 do not maintain contact')
        self.handstype_2hcontactno_radio.setProperty('handstype', 8)
        self.handstype_contactreln_buttongroup.addButton(self.handstype_2hcontactyes_radio)
        self.handstype_contactreln_buttongroup.addButton(self.handstype_2hcontactno_radio)

        # buttons and groups for 2-handed movement relation
        self.handstype_mvmtreln_buttongroup = QButtonGroup(parent=self)
        self.handstype_2hmvmtneither_radio = QRadioButton('Neither hand moves')
        self.handstype_2hmvmtneither_radio.setProperty('handstype', 9)
        self.handstype_2hmvmtone_radio = QRadioButton('Only 1 hand moves')
        self.handstype_2hmvmtone_radio.setProperty('handstype', 10)
        self.handstype_2hmvmtboth_radio = QRadioButton('Both hands move')
        self.handstype_2hmvmtboth_radio.setProperty('handstype', 13)
        self.handstype_mvmtreln_buttongroup.addButton(self.handstype_2hmvmtneither_radio)
        self.handstype_mvmtreln_buttongroup.addButton(self.handstype_2hmvmtone_radio)
        self.handstype_mvmtreln_buttongroup.addButton(self.handstype_2hmvmtboth_radio)

        # buttons and groups for movement relations in 2-handed signs where only one hand moves
        self.handstype_mvmtonehandreln_buttongroup = QButtonGroup(parent=self)
        self.handstype_2hmvmtoneH1_radio = QRadioButton('Only H1 moves')
        self.handstype_2hmvmtoneH1_radio.setProperty('handstype', 11)
        self.handstype_2hmvmtoneH2_radio = QRadioButton('Only H2 moves')
        self.handstype_2hmvmtoneH2_radio.setProperty('handstype', 12)
        self.handstype_mvmtonehandreln_buttongroup.addButton(self.handstype_2hmvmtoneH1_radio)
        self.handstype_mvmtonehandreln_buttongroup.addButton(self.handstype_2hmvmtoneH2_radio)

        # buttons and groups for movement relations in 2-handed signs where both hands move
        self.handstype_mvmtbothhandreln_buttongroup = QButtonGroup(parent=self)
        self.handstype_2hmvmtbothdiff_radio = QRadioButton('H1 and H2 move differently')
        self.handstype_2hmvmtbothdiff_radio.setProperty('handstype', 14)
        self.handstype_2hmvmtbothsame_radio = QRadioButton('H1 and H2 move similarly')
        self.handstype_2hmvmtbothsame_radio.setProperty('handstype', 15)
        self.handstype_mvmtbothhandreln_buttongroup.addButton(self.handstype_2hmvmtbothdiff_radio)
        self.handstype_mvmtbothhandreln_buttongroup.addButton(self.handstype_2hmvmtbothsame_radio)

        # buttons and groups for movement timing relations in 2-handed signs
        self.handstype_mvmttimingreln_buttongroup = QButtonGroup(parent=self)
        self.handstype_2hmvmtseq_radio = QRadioButton('Sequential')
        self.handstype_2hmvmtseq_radio.setProperty('handstype', 16)
        self.handstype_2hmvmtsimult_radio = QRadioButton('Simultaneous')
        self.handstype_2hmvmtsimult_radio.setProperty('handstype', 17)
        self.handstype_mvmttimingreln_buttongroup.addButton(self.handstype_2hmvmtseq_radio)
        self.handstype_mvmttimingreln_buttongroup.addButton(self.handstype_2hmvmtsimult_radio)

        # buttons and groups for mirroring relations in 2-handed signs
        self.handstype_mvmtmirroredreln_buttongroup = QButtonGroup(parent=self)
        self.handstype_mirroredall_radio = QRadioButton('Everything is mirrored / in phase')
        self.handstype_mirroredall_radio.setProperty('handstype', 18)
        self.handstype_mirroredexcept_radio = QRadioButton('Everything is mirrored / in phase except:')
        self.handstype_mirroredexcept_radio.setProperty('handstype', 19)
        self.handstype_mvmtmirroredreln_buttongroup.addButton(self.handstype_mirroredall_radio)
        self.handstype_mvmtmirroredreln_buttongroup.addButton(self.handstype_mirroredexcept_radio)
        self.handstype_2hmvmtexceptloc_check = QCheckBox('Location')
        self.handstype_2hmvmtexceptloc_check.setProperty('handstype', 20)
        self.handstype_2hmvmtexceptshape_check = QCheckBox('Handshape')
        self.handstype_2hmvmtexceptshape_check.setProperty('handstype', 21)
        self.handstype_2hmvmtexceptorientn_check = QCheckBox('Orientation')
        self.handstype_2hmvmtexceptorientn_check.setProperty('handstype', 22)

        # begin layout for sign type (highest level)
        self.signtype_layout = QVBoxLayout()
        self.signtype_layout.addWidget(self.handstype_unspec_radio)
        self.signtype_layout.addWidget(self.handstype_1h_radio)

        ## begin layout for 1-handed sign options
        self.onehand_spacedlayout = QHBoxLayout()
        self.onehand_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.onehand_layout = QVBoxLayout()
        self.onehand_layout.addWidget(self.handstype_1hmove_radio)
        self.onehand_layout.addWidget(self.handstype_1hnomove_radio)
        self.onehand_spacedlayout.addLayout(self.onehand_layout)
        self.signtype_layout.addLayout(self.onehand_spacedlayout)
        self.handstype_1h_radio.toggled.connect(lambda checked: self.enableChildWidgets(checked, self.onehand_layout))
        ## end layout for 1-handed sign options

        self.signtype_layout.addWidget(self.handstype_2h_radio)

        ## begin layout for 2-handed sign options
        self.twohand_spacedlayout = QHBoxLayout()
        self.twohand_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.twohand_col1_layout = QVBoxLayout()

        ### begin layout for 2-handed handshape relation
        self.handshape_layout = QVBoxLayout()
        self.handshape_layout.addWidget(self.handstype_2hsameshapes_radio)
        self.handshape_layout.addWidget(self.handstype_2hdiffshapes_radio)
        self.handshape_box = QGroupBox('Handshape relation')
        self.handshape_box.setLayout(self.handshape_layout)
        self.twohand_col1_layout.addWidget(self.handshape_box)
        ### end layout for 2-handed handshape relation

        ### begin layout for 2-handed contact relation
        self.contact_layout = QVBoxLayout()
        self.contact_layout.addWidget(self.handstype_2hcontactyes_radio)
        self.contact_layout.addWidget(self.handstype_2hcontactno_radio)
        self.contact_box = QGroupBox('Contact relation')
        self.contact_box.setLayout(self.contact_layout)
        self.twohand_col1_layout.addWidget(self.contact_box)
        ### end layout for 2-handed contact relation

        self.twohand_col1_layout.addStretch(1)

        ### begin layout for 2-handed movement relation
        self.movement_layout = QVBoxLayout()
        self.movement_layout.addWidget(self.handstype_2hmvmtneither_radio)
        self.movement_layout.addWidget(self.handstype_2hmvmtone_radio)

        #### begin layout for 2-handed movement relation in which only one hand moves
        self.movement_1h_spacedlayout = QHBoxLayout()
        self.movement_1h_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_1h_layout = QVBoxLayout()
        self.movement_1h_layout.addWidget(self.handstype_2hmvmtoneH1_radio)
        self.movement_1h_layout.addWidget(self.handstype_2hmvmtoneH2_radio)
        self.movement_1h_spacedlayout.addLayout(self.movement_1h_layout)
        self.movement_layout.addLayout(self.movement_1h_spacedlayout)
        self.handstype_2hmvmtone_radio.toggled.connect(lambda checked: self.enableChildWidgets(checked, self.movement_1h_layout))
        #### end layout for 2-handed movement relation in which only one hand moves

        self.movement_layout.addWidget(self.handstype_2hmvmtboth_radio)

        #### begin layout for 2-handed movement relation in which both hands move
        self.movement_2h_spacedlayout = QHBoxLayout()
        self.movement_2h_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.movement_2h_layout = QVBoxLayout()
        self.movement_2h_layout.addWidget(self.handstype_2hmvmtbothdiff_radio)
        self.movement_2h_layout.addWidget(self.handstype_2hmvmtbothsame_radio)

        ##### begin layout for 2-handed movement timing relation
        self.timing_layout = QVBoxLayout()
        self.timing_layout.addWidget(self.handstype_2hmvmtseq_radio)
        self.timing_layout.addWidget(self.handstype_2hmvmtsimult_radio)

        ###### begin layout for simultaneous movement
        self.simultaneous_spacedlayout = QHBoxLayout()
        self.simultaneous_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.simultaneous_layout = QVBoxLayout()
        self.simultaneous_layout.addWidget(self.handstype_mirroredall_radio)
        self.simultaneous_layout.addWidget(self.handstype_mirroredexcept_radio)

        ####### begin layout for mirrored movement exceptions
        self.mirroredexcept_spacedlayout = QHBoxLayout()
        self.mirroredexcept_spacedlayout.addSpacerItem(QSpacerItem(30, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.mirroredexcept_layout = QVBoxLayout()
        self.mirroredexcept_layout.addWidget(self.handstype_2hmvmtexceptloc_check)
        self.mirroredexcept_layout.addWidget(self.handstype_2hmvmtexceptshape_check)
        self.mirroredexcept_layout.addWidget(self.handstype_2hmvmtexceptorientn_check)
        self.mirroredexcept_spacedlayout.addLayout(self.mirroredexcept_layout)
        self.simultaneous_layout.addLayout(self.mirroredexcept_spacedlayout)
        self.handstype_mirroredexcept_radio.toggled.connect(lambda checked: self.enableChildWidgets(checked, self.mirroredexcept_layout))
        ####### end layout for mirrored movement exceptions

        self.simultaneous_spacedlayout.addLayout(self.simultaneous_layout)
        self.handstype_2hmvmtsimult_radio.toggled.connect(lambda checked: self.enableChildWidgets(checked, self.simultaneous_layout))
        ###### end layout for simultaneous movement

        self.timing_layout.addLayout(self.simultaneous_spacedlayout)
        self.timing_box = QGroupBox('Movement timing relation')
        self.timing_box.setLayout(self.timing_layout)
        self.movement_2h_layout.addWidget(self.timing_box)
        ##### end layout for 2-handed movement timing relation

        self.movement_2h_spacedlayout.addLayout(self.movement_2h_layout)
        self.movement_layout.addLayout(self.movement_2h_spacedlayout)
        self.handstype_2hmvmtboth_radio.toggled.connect(lambda checked: self.enableChildWidgets(checked, self.movement_2h_layout))
        #### end layout for 2-handed movement relation in which both hands move

        self.movement_layout.addWidget(self.handstype_2hmvmtboth_radio)

        self.movement_box = QGroupBox('Movement relation')
        self.movement_box.setLayout(self.movement_layout)
        ### end layout for 2-handed movement relation

        self.twohand_spacedlayout.addLayout(self.twohand_col1_layout)
        self.twohand_spacedlayout.addWidget(self.movement_box)

        self.signtype_layout.addLayout(self.twohand_spacedlayout)

        self.handstype_2h_radio.toggled.connect(lambda checked: self.enableChildWidgets(checked, self.twohand_spacedlayout))
        ## end layout for 2-handed sign options

        self.signtype_box = QGroupBox('Sign type')
        self.signtype_box.setLayout(self.signtype_layout)
        # end layout for sign type (highest level)

        self.addWidget(self.signtype_box)

        # ensure all options are disabled except Unspecified
        self.handstype_1h_radio.toggle()
        self.handstype_2h_radio.toggle()
        self.handstype_unspec_radio.toggle()


    def enableChildWidgets(self, yesorno, parentlayout):
        numchildren = parentlayout.count()
        for childnum in range(numchildren):
            thechild = parentlayout.itemAt(childnum)
            if thechild.widget():
                thechild.widget().setEnabled(yesorno)
            elif thechild.layout():
                self.enableChildWidgets(yesorno, thechild.layout())


class SigntypeSelectorDialog(QDialog):
    # saved_movements = pyqtSignal(Movements)

    def __init__(self, system_default_signtype_specifications, app_settings, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.system_default_signtype_specifications = system_default_signtype_specifications

        self.signtype_layout = SigntypeSpecificationLayout(app_ctx)

        main_layout = QVBoxLayout()
        main_layout.addLayout(self.signtype_layout)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Cancel

        self.button_box = QDialogButtonBox(buttons, parent=self)

        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)
        self.setMinimumSize(QSize(500, 850))

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            # response = QMessageBox.question(self, 'Warning',
            #                                 'If you close the window, any unsaved changes will be lost. Continue?')
            # if response == QMessageBox.Yes:
            #     self.accept()

            self.reject()

    #     elif standard == QDialogButtonBox.RestoreDefaults:
    #         self.movement_tab.remove_all_pages()
    #         self.movement_tab.add_default_movement_tabs(is_system_default=True)
        elif standard == QDialogButtonBox.Save:
            # TODO KV implement
            print("saving signtype info (but not really...)")
            self.parent().current_sign.setsigntype("TODO KV construct signtype module")

            # self.save_new_images()
            # self.saved_locations.emit(self.location_tab.get_locations())
            QMessageBox.information(self, 'Sign Type Saved', 'Sign type has been successfully saved!')

            self.accept()
