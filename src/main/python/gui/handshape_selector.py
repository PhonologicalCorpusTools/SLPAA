from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QDialogButtonBox,
    QGridLayout,
    QLayout,
    QScrollArea,
    QButtonGroup
)

from PyQt5.QtCore import (
    QSize,
    pyqtSignal
)

# from gui.panel import HandTranscriptionPanel
from gui.hand_configuration import ConfigGlobal, Config
# from gui.module_selector import HandSelectionLayout
from lexicon.lexicon_classes import HandshapeTranscription
from gui.module_selector import ModuleSpecificationLayout


class HandTranscriptionPanel(QScrollArea):
    selected_hand = pyqtSignal(int)

    def __init__(self, predefined_ctx, **kwargs):
        super().__init__(**kwargs)

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        # main_layout = QGridLayout()
        main_layout = QHBoxLayout()
        main_frame.setLayout(main_layout)

        self.global_info = ConfigGlobal(title='Handshape global options', parent=self)
        # main_layout.addWidget(self.global_info, 0, 0, 2, 1)
        main_layout.addWidget(self.global_info)

        self.config = Config(predefined_ctx, parent=self)  # 1, 'Configuration 1'
        # main_layout.addWidget(self.config1, 0, 1, 1, 2)
        main_layout.addWidget(self.config)

        # TODO KV delete
        # self.config2 = Config(2, 'Configuration 2', predefined_ctx, parent=self)
        # main_layout.addWidget(self.config2, 1, 1, 1, 2)

        self.setWidget(main_frame)

    def clear(self):
        self.global_info.clear()
        self.config.clear()
        # TODO KV delete
        # self.config2.clear()

    def set_value(self, global_handshape_info, hand_transcription):
        self.global_info.set_value(global_handshape_info)
        self.config.set_value(hand_transcription.config)  #1)
        # TODO KV delete
        # self.config2.set_value(hand_transcription.config2)

    # def change_hand_selection(self, hand):
    #     if hand == 1:
    #         self.button1.setChecked(True)
    #     elif hand == 2:
    #         self.button2.setChecked(True)
    #     # TODO KV delete
    #     # elif hand == 3:
    #     #     self.button3.setChecked(True)
    #     # elif hand == 4:
    #     #     self.button4.setChecked(True)

    def insert_radio_button(self, focused_hand):
        self.selected_hand_group = QButtonGroup(parent=self)
        self.button1, self.button2 = self.config.insert_radio_button()
        # TODO KV delete
        # self.button3, self.button4 = self.config2.insert_radio_button()

        self.button1.clicked.connect(lambda: self.selected_hand.emit(1))
        self.button2.clicked.connect(lambda: self.selected_hand.emit(2))
        # TODO KV delete
        # self.button3.clicked.connect(lambda: self.selected_hand.emit(3))
        # self.button4.clicked.connect(lambda: self.selected_hand.emit(4))

        if focused_hand == 1:
            self.button1.setChecked(True)
        elif focused_hand == 2:
            self.button2.setChecked(True)
        # TODO KV delete
        # elif focused_hand == 3:
        #     self.button3.setChecked(True)
        # elif focused_hand == 4:
        #     self.button4.setChecked(True)

        self.selected_hand_group.addButton(self.button1, 1)
        self.selected_hand_group.addButton(self.button2, 2)
        # TODO KV delete
        # self.selected_hand_group.addButton(self.button3, 3)
        # self.selected_hand_group.addButton(self.button4, 4)

    def remove_radio_button(self):
        self.config.remove_radio_button()
        # TODO KV delete
        # self.config2.remove_radio_button()
        self.selected_hand_group.deleteLater()

    def get_hand_transcription(self, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            return self.config.hand1.get_hand_transcription_list()
        elif hand == 2:
            return self.config.hand2.get_hand_transcription_list()
        # TODO KV delete
        # elif hand == 3:
        #     return self.config2.hand1.get_hand_transcription_list()
        # elif hand == 4:
        #     return self.config2.hand2.get_hand_transcription_list()

    def set_predefined(self, transcription_list, hand=None):
        if hand is None:
            hand = self.selected_hand_group.checkedId()

        if hand == 1:
            self.config.hand1.set_predefined(transcription_list)
        elif hand == 2:
            self.config.hand2.set_predefined(transcription_list)
        # TODO KV delete
        # elif hand == 3:
        #     self.config2.hand1.set_predefined(transcription_list)
        # elif hand == 4:
        #     self.config2.hand2.set_predefined(transcription_list)


# class HandshapeSpecificationLayout(QVBoxLayout):
class HandshapeSpecificationLayout(ModuleSpecificationLayout):
    saved_handshape = pyqtSignal(ConfigGlobal, HandshapeTranscription, dict)

    def __init__(self, predefined_ctx, moduletoload=None, **kwargs):  # TODO KV app_ctx, movement_specifications,
        super().__init__(**kwargs)

        self.panel = HandTranscriptionPanel(predefined_ctx)
        if moduletoload is not None:
            self.panel.set_value(moduletoload[0], moduletoload[1])
        self.addWidget(self.panel)

    def get_savedmodule_signal(self):
        return self.saved_handshape

    def get_savedmodule_args(self):
        return (self.panel.global_info, HandshapeTranscription(self.panel.config.get_value()))

    def clear(self):
        self.panel.clear()

    def desiredwidth(self):
        return 2000

    def desiredheight(self):
        return 400

