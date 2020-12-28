import os
from PyQt5.QtCore import (
    Qt,
    QSize,
    QSettings,
    QPoint
)
from PyQt5.QtWidgets import (
    QGridLayout,
    QListView,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QAction,
    QStatusBar,
    QSplitter,
    QLineEdit,
    QCompleter,
    QFrame,
    QScrollArea
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence,
    QPixmap
)
from .initialization_dialog import InitializationDialog
from .hand_configuration import Config, ConfigGlobal
from .meta_data import MetaDataWidget
from .parameter import ParameterView
from .location_definer import LocationDefinerDialog
from .panel import (
    LexicalInformationPanel,
    HandTranscriptionPanel,
    HandIllustrationPanel,
    ParameterPanel
)

from collections import defaultdict
from constant import SAMPLE_LOCATIONS
from lexicon.lexicon_classes import (
    Corpus,
    GlobalHandshapeOptions,
    HandshapeTranscription,
    HandshapeTranscriptionConfig,
    HandshapeTranscriptionField,
    HandshapeTranscriptionHand,
    HandshapeTranscriptionSlot,
    LexicalInformation,
    LocationParameter,
    Locations,
    Sign
)
from pprint import pprint


class MainWindow(QMainWindow):
    def __init__(self, app_ctx):
        super().__init__()
        self.app_ctx = app_ctx

        self.handle_app_settings()
        self.check_storage()
        self.resize(self.app_settings['display']['size'])
        self.move(self.app_settings['display']['position'])

        # app title
        self.setWindowTitle('Sign Language Phonetic Annotator and Analyzer')

        # toolbar
        toolbar = QToolBar('Main toolbar', parent=self)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # actions
        # save
        action_save = QAction(QIcon(self.app_ctx.toolbar_icons['save']), 'Save', parent=self)
        action_save.setStatusTip('Save')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        action_save.triggered.connect(self.on_action_save)
        action_save.setCheckable(False)

        # copy
        action_copy = QAction(QIcon(self.app_ctx.toolbar_icons['copy']), 'Copy', parent=self)
        action_copy.setStatusTip('Copy the current sign')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_C))
        action_copy.triggered.connect(self.on_action_copy)
        action_copy.setCheckable(False)

        # paste
        action_paste = QAction(QIcon(self.app_ctx.toolbar_icons['paste']), 'Paste', parent=self)
        action_paste.setStatusTip('Paste the copied sign')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_P))
        action_paste.triggered.connect(self.on_action_paste)
        action_paste.setCheckable(False)

        # define locations
        action_define_location = QAction('Define locations...', parent=self)
        action_define_location.setStatusTip('Open define location window')
        action_define_location.triggered.connect(self.on_action_define_location)
        action_define_location.setCheckable(False)

        # new corpus
        action_new_corpus = QAction('New corpus', parent=self)
        action_new_corpus.setStatusTip('Create a new corpus')
        action_new_corpus.triggered.connect(self.on_action_new_corpus)
        action_new_corpus.setCheckable(False)

        # load corpus
        action_load_corpus = QAction('Load corpus...', parent=self)
        action_load_corpus.setStatusTip('Load a .corpus file')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
        action_load_corpus.triggered.connect(self.on_action_load_corpus)
        action_load_corpus.setCheckable(False)

        # close
        action_close = QAction('Close', parent=self)
        action_close.setStatusTip('Close the application')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_W))
        action_close.triggered.connect(self.on_action_close)
        action_close.setCheckable(False)

        # new sign
        action_new_sign = QAction(QIcon(self.app_ctx.toolbar_icons['new_sign']), 'New sign', parent=self)
        action_new_sign.setStatusTip('Create a new sign')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        action_new_sign.triggered.connect(self.on_action_new_sign)
        action_new_sign.setCheckable(False)

        toolbar.addAction(action_new_sign)
        toolbar.addSeparator()
        toolbar.addAction(action_save)
        toolbar.addSeparator()
        toolbar.addAction(action_copy)
        toolbar.addAction(action_paste)

        # status bar
        self.status_bar = QStatusBar(parent=self)
        self.setStatusBar(self.status_bar)

        # menu
        main_menu = self.menuBar()

        menu_file = main_menu.addMenu('&File')
        menu_file.addAction(action_new_corpus)
        menu_file.addAction(action_load_corpus)
        menu_file.addSeparator()
        menu_file.addAction(action_close)
        menu_file.addAction(action_save)
        menu_file.addSeparator()
        menu_file.addAction(action_new_sign)

        menu_edit = main_menu.addMenu('&Edit')
        menu_edit.addAction(action_copy)
        menu_edit.addAction(action_paste)

        menu_location = main_menu.addMenu('&Location')
        menu_location.addAction(action_define_location)

        # central widget
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_widget.setLayout(central_layout)

        # define main splitter and scroll areas
        main_splitter = QSplitter(Qt.Horizontal, parent=self)
        central_layout.addWidget(main_splitter)

        left_scroll = QScrollArea(parent=self)
        left_scroll.resize(QSize(100, 1000))
        left_scroll.setWidgetResizable(True)
        right_scroll = QScrollArea(parent=self)
        right_scroll.setWidgetResizable(True)
        right_frame = QFrame(parent=self)
        right_frame.resize(QSize(1000, 1000))
        right_layout = QVBoxLayout()
        right_frame.setLayout(right_layout)
        main_splitter.addWidget(left_scroll)
        main_splitter.addWidget(right_scroll)

        # corpus list view

        corpus_view = QListView(parent=self)
        corpus_view.resize(QSize(100, 1000))
        left_scroll.setWidget(corpus_view)

        # meta data
        meta_data = MetaDataWidget(parent=self)
        right_layout.addWidget(meta_data)

        configuration_layout = QGridLayout()
        right_layout.addLayout(configuration_layout)

        global_option = ConfigGlobal(title='Handshape global options', parent=self)
        configuration_layout.addWidget(global_option, 0, 0, 2, 1)

        #transcription_layout = QVBoxLayout()
        #transcription_layout.addStretch()
        #transcription_layout.setSpacing(5)
        #configuration_layout.addLayout(transcription_layout, 0, 1, 1, 1)

        self.config1 = Config(1, 'Configuration 1', parent=self)
        self.config1.slot_on_focus.connect(self.update_status_bar)
        self.config1.slot_num_on_focus.connect(self.update_hand_illustration)
        self.config1.slot_leave.connect(self.status_bar.clearMessage)
        self.config1.slot_leave.connect(lambda: self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio)))
        configuration_layout.addWidget(self.config1, 0, 1, 1, 2)

        self.config2 = Config(2, 'Configuration 2', parent=self)
        self.config2.slot_on_focus.connect(self.update_status_bar)
        self.config2.slot_num_on_focus.connect(self.update_hand_illustration)
        self.config2.slot_leave.connect(self.status_bar.clearMessage)
        self.config2.slot_leave.connect(lambda: self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio)))
        configuration_layout.addWidget(self.config2, 1, 1, 1, 2)

        # lower layout
        lower_layout = QHBoxLayout()
        right_layout.addLayout(lower_layout)

        self.parameter = ParameterView('Parameter', parent=self)
        lower_layout.addWidget(self.parameter)

        # hand image
        self.hand_illustration = QLabel()
        self.hand_illustration.setFixedSize(QSize(400, 400))
        neutral_img = QPixmap(self.app_ctx.hand_illustrations['neutral'])
        self.hand_illustration.setPixmap(
            neutral_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        lower_layout.addWidget(self.hand_illustration)

        self.open_initialization_window()

    def open_initialization_window(self):
        initialization = InitializationDialog(self.app_ctx, self.on_action_new_corpus, self.on_action_load_corpus, parent=self)
        response = initialization.exec_()
        if not response:  # close the window or press cancel
            self.on_action_new_sign()

    def handle_app_settings(self):
        self.app_settings = defaultdict(dict)

        self.app_qsettings = QSettings('UBC Phonology Tools',
                                       application='Sign Language Phonetic Annotator and Analyzer')

        self.app_qsettings.beginGroup('storage')
        self.app_settings['storage']['corpora'] = self.app_qsettings.value('corpora',
                                                                           defaultValue=os.path.normpath(
                                                                               os.path.join(
                                                                                   os.path.expanduser('~/Documents'),
                                                                                   'PCT', 'SLP-AA', 'CORPORA')))
        self.app_settings['storage']['image'] = self.app_qsettings.value('image',
                                                                         defaultValue=os.path.normpath(
                                                                             os.path.join(
                                                                                 os.path.expanduser('~/Documents'),
                                                                                 'PCT', 'SLP-AA', 'IMAGE')))
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('display')
        self.app_settings['display']['size'] = self.app_qsettings.value('size', defaultValue=QSize(1200, 1000))
        self.app_settings['display']['position'] = self.app_qsettings.value('position', defaultValue=QPoint(50, 50))
        self.app_settings['display']['sig_figs'] = self.app_qsettings.value('sig_figs', defaultValue=3)
        self.app_settings['display']['tooltips'] = self.app_qsettings.value('tooltips', defaultValue=True)
        self.app_qsettings.endGroup()

    def check_storage(self):
        if not os.path.exists(self.app_settings['storage']['corpora']):
            os.makedirs(self.app_settings['storage']['corpora'])

        if not os.path.exists(self.app_settings['storage']['image']):
            os.makedirs(self.app_settings['storage']['image'])

    def save_app_settings(self):
        self.app_qsettings = QSettings('UBC Phonology Tools',
                                       application='Sign Language Phonetic Annotator and Analyzer')

        self.app_qsettings.beginGroup('storage')
        self.app_qsettings.setValue('corpora', self.app_settings['storage']['corpora'])
        self.app_qsettings.setValue('image', self.app_settings['storage']['image'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('display')
        self.app_qsettings.setValue('size', self.size())
        self.app_qsettings.setValue('position', self.pos())
        self.app_qsettings.setValue('sig_figs', self.app_settings['display']['sig_figs'])
        self.app_qsettings.setValue('tooltips', self.app_settings['display']['tooltips'])
        self.app_qsettings.endGroup()

    def on_action_define_location(self):
        location_definer = LocationDefinerDialog(self.locations, self.app_settings, self.app_ctx, parent=self)
        location_definer.saved_locations.connect(self.save_new_locations)
        location_definer.exec_()

    def save_new_locations(self, new_locations):
        #TODO: need to reimplement this once corpus class is there
        self.locations = new_locations

    def update_status_bar(self, text):
        self.status_bar.showMessage(text)

    def update_hand_illustration(self, num):
        hand_img = QPixmap(self.app_ctx.hand_illustrations['slot' + str(num)])
        self.hand_illustration.setPixmap(
            hand_img.scaled(self.hand_illustration.width(), self.hand_illustration.height(), Qt.KeepAspectRatio))
        self.hand_illustration.repaint()

    def on_action_save(self, clicked):

        print(HandshapeTranscription([self.config1.get_value(), self.config2.get_value()]))


    def on_action_copy(self, clicked):
        pass
        #TODO: implement

    def on_action_paste(self, clicked):
        pass
        #TODO: implement

    def on_action_new_corpus(self, clicked):
        print('new_corpus', clicked)
        #TODO: implement

    def on_action_load_corpus(self, clicked):
        print('load_corpus', clicked)
        #TODO: implement

    def on_action_close(self, clicked):
        pass
        #TODO: implement

    def on_action_new_sign(self, clicked):
        pass
        #TODO: implement

    def closeEvent(self, event):
        self.save_app_settings()
        super().closeEvent(event)


class TestMainWindow(QMainWindow):
    def __init__(self, app_ctx):
        super().__init__()
        self.app_ctx = app_ctx

        # app title
        self.setWindowTitle('Sign Language Phonetic Annotator and Analyzer')

        central_splitter = QSplitter(Qt.Horizontal, parent=self)
        right_splitter = QSplitter(Qt.Vertical, parent=self)
        top_splitter = QSplitter(Qt.Horizontal, parent=self)
        bottom_splitter = QSplitter(Qt.Horizontal, parent=self)

        right_splitter.addWidget(top_splitter)
        right_splitter.addWidget(bottom_splitter)

        corpus_view = QListView(parent=self)
        corpus_view.resize(QSize(100, 1000))

        corpus_scroll = QScrollArea(parent=self)
        corpus_scroll.resize(QSize(100, 1000))
        corpus_scroll.setWidgetResizable(True)
        corpus_scroll.setWidget(corpus_view)

        lexical_scroll = LexicalInformationPanel(parent=self)
        transcription_scroll = HandTranscriptionPanel(parent=self)
        illustration_scroll = HandIllustrationPanel(self.app_ctx, parent=self)
        parameter_scroll = ParameterPanel(self.app_ctx, parent=self)

        top_splitter.addWidget(lexical_scroll)
        top_splitter.addWidget(transcription_scroll)
        bottom_splitter.addWidget(illustration_scroll)
        bottom_splitter.addWidget(parameter_scroll)

        central_splitter.addWidget(corpus_scroll)
        central_splitter.addWidget(right_splitter)

        self.setCentralWidget(central_splitter)