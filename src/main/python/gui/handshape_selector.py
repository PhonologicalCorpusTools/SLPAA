from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QDialogButtonBox,
    QGridLayout,
    QLayout,
    QScrollArea,
    QButtonGroup,
    QLabel,
    QSizePolicy
)

from PyQt5.QtCore import (
    QSize,
    pyqtSignal,
    Qt
)

from PyQt5.QtGui import (
    QPixmap
)

# from gui.panel import HandTranscriptionPanel
from gui.hand_configuration import ConfigGlobal, Config
# from gui.module_selector import HandSelectionLayout
from lexicon.lexicon_classes import HandConfiguration
from gui.module_selector import ModuleSpecificationLayout
from gui.undo_command import TranscriptionUndoCommand


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
        return QSize(1300, 400)

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


# class HandshapeSpecificationLayout(QVBoxLayout):
class HandConfigSpecificationLayout(ModuleSpecificationLayout):
    saved_handconfig = pyqtSignal(dict, dict, list, int)

    def __init__(self, mainwindow, moduletoload=None, **kwargs):  # TODO KV app_ctx, movement_specifications,
    # def __init__(self, mainwindow, predefined_ctx, moduletoload=None, **kwargs):  # TODO KV app_ctx, movement_specifications,
        super().__init__(**kwargs)

        self.mainwindow = mainwindow

        main_layout = QHBoxLayout()

        self.panel = HandTranscriptionPanel(self.mainwindow.app_ctx.predefined)
        self.panel.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)  # QSizePolicy.MinimumExpanding,
        self.illustration = HandIllustrationPanel(self.mainwindow.app_ctx, parent=self.parent())  # (self.app_ctx, parent=self)
        self.illustration.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # QSizePolicy.MinimumExpanding,
        self.panel.config.slot_on_focus.connect(self.panel.update_details_label)
        self.panel.config.slot_num_on_focus.connect(self.illustration.update_hand_illustration)
        self.panel.config.slot_leave.connect(self.panel.update_details_label)
        self.panel.config.slot_leave.connect(self.illustration.set_neutral_img)
        self.panel.config.slot_finish_edit.connect(self.handle_slot_edit)

        if moduletoload:
            self.panel.set_value(moduletoload)
        # TODO KV also load forearm, uncertainty info

        main_layout.addWidget(self.panel)
        main_layout.addWidget(self.illustration)
        self.addLayout(main_layout)
        # self.addWidget(self.panel)

    def handle_slot_edit(self, slot, old_prop, new_prop):
        undo_command = TranscriptionUndoCommand(slot, old_prop, new_prop)
        self.mainwindow.undostack.push(undo_command)

    def get_savedmodule_signal(self):
        return self.saved_handconfig

    # def get_savedmodule_args(self):
    #     return (self.treemodel,)

    def get_savedmodule_args(self):
        # allconfigoptions = self.panel.config.get_value()
        # handconfig = allconfigoptions['hand']
        # overalloptions = {k: v for (k, v) in allconfigoptions.items() if k != 'hand'}
        # return (handconfig, overalloptions)
        return (self.panel.config.get_value(), )

    def refresh(self):
        self.clear()

    def clear(self):
        self.panel.clear()

    def desiredwidth(self):
        return 2000

    def desiredheight(self):
        return 400

