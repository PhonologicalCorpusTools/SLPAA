import os
import pickle
import json
import csv
from collections import defaultdict
from copy import deepcopy
from datetime import date
from fractions import Fraction

from PyQt5.QtCore import (
    Qt,
    QSize,
    QSettings,
    QPoint,
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QToolBar,
    QAction,
    QStatusBar,
    QScrollArea,
    QMessageBox,
    QUndoStack,
    QMdiArea,
    QMdiSubWindow,
    QWidget
)

from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)

# Ref: https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html
from gui.initialization_dialog import InitializationDialog
from gui.corpus_view import CorpusDisplay
from gui.location_definer import LocationDefinerDialog
from gui.signtypespecification_view import Signtype
from gui.export_csv_dialog import ExportCSVDialog
from gui.panel import SignLevelMenuPanel, SignSummaryPanel
from gui.preference_dialog import PreferenceDialog
from gui.decorator import check_unsaved_change, check_unsaved_corpus
from gui.undo_command import TranscriptionUndoCommand, SignLevelUndoCommand
from constant import SAMPLE_LOCATIONS
from lexicon.lexicon_classes import Corpus
from serialization_classes import renamed_load


class SubWindow(QMdiSubWindow):
    subwindow_closed = pyqtSignal(QWidget)

    def __init__(self, sub_name, widget, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle(sub_name)
        self.setWidget(widget)

    def closeEvent(self, closeEvent):
        self.subwindow_closed.emit(self.widget())


# TODO: add undo/redo stack: https://doc.qt.io/qt-5/qtwidgets-tools-undoframework-example.html
# TODO: location image size problem
class MainWindow(QMainWindow):
    def __init__(self, app_ctx):
        super().__init__()
        self.app_ctx = app_ctx

        self.corpus = None
        self.current_sign = None

        self.undostack = QUndoStack(parent=self)

        self.predefined_handshape_dialog = None

        # system-defaults
        self.system_default_locations = deepcopy(SAMPLE_LOCATIONS)
        self.system_default_movement = None
        self.system_default_handshape = None

        # handle setting-related stuff
        self.handle_app_settings()
        self.check_storage()
        self.resize(self.app_settings['display']['size'])
        self.move(self.app_settings['display']['position'])

        # date information
        self.today = date.today()

        # app title
        self.setWindowTitle('Sign Language Phonetic Annotator and Analyzer')

        # toolbar
        toolbar = QToolBar('Main toolbar', parent=self)
        toolbar.setIconSize(QSize(16, 16))
        self.addToolBar(toolbar)

        # actions
        # save
        action_save = QAction(QIcon(self.app_ctx.icons['save']), 'Save', parent=self)
        action_save.setStatusTip('Save')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        action_save.triggered.connect(self.on_action_save)
        action_save.setCheckable(False)

        # save as
        action_saveas = QAction(QIcon(self.app_ctx.icons['saveas']), 'Save As...', parent=self)
        action_saveas.setStatusTip('Save As...')
        action_saveas.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_A))
        action_saveas.triggered.connect(self.on_action_saveas)
        action_saveas.setCheckable(False)

        # undo
        action_undo = QAction(QIcon(self.app_ctx.icons['undo']), 'Undo', parent=self)
        action_undo.setEnabled(False)
        self.undostack.canUndoChanged.connect(lambda b: action_undo.setEnabled(b))
        action_undo.setStatusTip('Undo')
        action_undo.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Z))
        action_undo.triggered.connect(lambda: self.undostack.undo())
        action_undo.setCheckable(False)

        # redo
        action_redo = QAction(QIcon(self.app_ctx.icons['redo']), 'Redo', parent=self)
        action_redo.setEnabled(False)
        self.undostack.canRedoChanged.connect(lambda b: action_redo.setEnabled(b))
        action_redo.setStatusTip('Undo')
        action_redo.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Y))
        action_redo.triggered.connect(lambda: self.undostack.redo())
        action_redo.setCheckable(False)

        # copy
        action_copy = QAction(QIcon(self.app_ctx.icons['copy']), 'Copy', parent=self)
        action_copy.setStatusTip('Copy the current sign')
        action_copy.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_C))
        action_copy.triggered.connect(self.on_action_copy)
        action_copy.setCheckable(False)

        # paste
        action_paste = QAction(QIcon(self.app_ctx.icons['paste']), 'Paste', parent=self)
        action_paste.setStatusTip('Paste the copied sign')
        action_paste.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_P))
        action_paste.triggered.connect(self.on_action_paste)
        action_paste.setCheckable(False)

        # define locations
        action_define_location = QAction('Define locations...', parent=self)
        action_define_location.setStatusTip('Open define location window')
        action_define_location.triggered.connect(self.on_action_define_location)
        action_define_location.setCheckable(False)

        # new corpus
        action_new_corpus = QAction(QIcon(self.app_ctx.icons['blank16']), "New corpus", parent=self)
        action_new_corpus.setStatusTip("Create a new corpus")
        action_new_corpus.triggered.connect(self.on_action_new_corpus)
        action_new_corpus.setCheckable(False)

        # load corpus
        action_load_corpus = QAction(QIcon(self.app_ctx.icons['load16']), "Load corpus...", parent=self)
        action_load_corpus.setStatusTip("Load a .corpus file")
        action_load_corpus.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
        action_load_corpus.triggered.connect(self.on_action_load_corpus)
        action_load_corpus.setCheckable(False)

        # close
        action_close = QAction('Close', parent=self)
        action_close.setStatusTip('Close the application')
        action_close.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_W))
        action_close.triggered.connect(self.on_action_close)
        action_close.setCheckable(False)

        # output handshape transcription to csv
        action_export_handshape_transcription_csv = QAction('Export handshape transcription as CSV...', parent=self)
        action_export_handshape_transcription_csv.triggered.connect(self.on_action_export_handshape_transcription_csv)

        # new sign
        action_new_sign = QAction(QIcon(self.app_ctx.icons['plus']), 'New sign', parent=self)
        action_new_sign.setStatusTip('Create a new sign')
        action_new_sign.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        action_new_sign.triggered.connect(self.on_action_new_sign)
        action_new_sign.setCheckable(False)

        # delete sign
        self.action_delete_sign = QAction(QIcon(self.app_ctx.icons['delete']), 'Delete sign', parent=self)
        self.action_delete_sign.setEnabled(False)
        self.action_delete_sign.setStatusTip('Delete the selected sign')
        self.action_delete_sign.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Delete))
        self.action_delete_sign.triggered.connect(self.on_action_delete_sign)
        self.action_delete_sign.setCheckable(False)

        # preferences
        action_edit_preference = QAction('Preferences...', parent=self)
        action_edit_preference.setStatusTip('Open preference window')
        action_edit_preference.triggered.connect(self.on_action_edit_preference)
        action_edit_preference.setCheckable(False)

        # show/hide corpus subwindow
        self.action_show_sub_corpus = QAction('Show corpus list', parent=self)
        self.action_show_sub_corpus.setStatusTip('Show/hide corpus list')
        self.action_show_sub_corpus.triggered.connect(self.on_action_show_sub_corpus)
        self.action_show_sub_corpus.setCheckable(True)
        self.action_show_sub_corpus.setChecked(self.app_settings['display']['sub_corpus_show'])

        # show/hide sign-level options/menu subwindow
        self.action_show_sub_signlevelmenu = QAction('Show sign-level menu', parent=self)
        self.action_show_sub_signlevelmenu.setStatusTip('Show/hide sign-level menu')
        self.action_show_sub_signlevelmenu.triggered.connect(self.on_action_show_sub_signlevelmenu)
        self.action_show_sub_signlevelmenu.setCheckable(True)
        self.action_show_sub_signlevelmenu.setChecked(self.app_settings['display']['sub_signlevelmenu_show'])

        # show/hide module (xslot) summary subwindow
        self.action_show_sub_visualsummary = QAction('Show sign summary', parent=self)
        self.action_show_sub_visualsummary.setStatusTip('Show/hide sign summary')
        self.action_show_sub_visualsummary.triggered.connect(self.on_action_show_sub_visualsummary)
        self.action_show_sub_visualsummary.setCheckable(True)
        self.action_show_sub_visualsummary.setChecked(self.app_settings['display']['sub_visualsummary_show'])

        # export subwindow config
        action_export_subwindow_config = QAction('Export subwindow configuration...', parent=self)
        action_export_subwindow_config.setStatusTip('Export subwindow configuration')
        action_export_subwindow_config.triggered.connect(self.on_action_export_subwindow_config)

        # import subwindow config
        action_import_subwindow_config = QAction('Import subwindow configuration...', parent=self)
        action_import_subwindow_config.setStatusTip('Import subwindow configuration')
        action_import_subwindow_config.triggered.connect(self.on_action_import_subwindow_config)

        # go back to default view
        action_default_view = QAction('Restore default view', parent=self)
        action_default_view.setStatusTip('Show the default view')
        action_default_view.triggered.connect(self.on_action_default_view)
        action_default_view.setCheckable(False)

        toolbar.addAction(action_new_sign)
        toolbar.addAction(self.action_delete_sign)
        toolbar.addSeparator()
        toolbar.addAction(action_save)
        toolbar.addAction(action_saveas)
        toolbar.addSeparator()
        toolbar.addAction(action_undo)
        toolbar.addAction(action_redo)
        toolbar.addSeparator()
        toolbar.addAction(action_copy)
        toolbar.addAction(action_paste)

        # status bar
        self.status_bar = QStatusBar(parent=self)
        self.setStatusBar(self.status_bar)

        # menu
        main_menu = self.menuBar()

        menu_option = main_menu.addMenu('&Settings')
        menu_option.addAction(action_edit_preference)

        menu_file = main_menu.addMenu('&File')
        menu_file.addAction(action_new_corpus)
        menu_file.addAction(action_load_corpus)
        menu_file.addSeparator()
        menu_file.addAction(action_export_handshape_transcription_csv)
        menu_file.addSeparator()
        menu_file.addAction(action_close)
        menu_file.addAction(action_save)
        menu_file.addAction(action_saveas)
        menu_file.addSeparator()
        menu_file.addAction(action_new_sign)
        menu_file.addAction(self.action_delete_sign)

        menu_edit = main_menu.addMenu('&Edit')
        menu_edit.addAction(action_copy)
        menu_edit.addAction(action_paste)

        menu_edit = main_menu.addMenu('&View')
        menu_edit.addAction(action_default_view)
        menu_edit.addSeparator()
        menu_edit.addAction(self.action_show_sub_corpus)
        menu_edit.addAction(self.action_show_sub_signlevelmenu)
        menu_edit.addAction(self.action_show_sub_visualsummary)
        menu_edit.addSeparator()
        menu_edit.addAction(action_export_subwindow_config)
        menu_edit.addAction(action_import_subwindow_config)

        menu_location = main_menu.addMenu('&Location')
        menu_location.addAction(action_define_location)

        corpusname = ""
        if self.corpus and self.corpus.name:
            corpusname = self.corpus.name
        self.corpus_display = CorpusDisplay(corpusname, parent=self)
        self.corpus_display.selected_sign.connect(self.handle_sign_selected)
        self.corpus_display.title_changed.connect(self.setCorpusName)

        self.corpus_scroll = QScrollArea(parent=self)
        self.corpus_scroll.setWidgetResizable(True)
        self.corpus_scroll.setWidget(self.corpus_display)

        self.signlevel_panel = SignLevelMenuPanel(sign=self.current_sign, mainwindow=self, parent=self)

        self.signsummary_panel = SignSummaryPanel(mainwindow=self, sign=self.current_sign, parent=self)
        self.signlevel_panel.sign_updated.connect(self.signsummary_panel.refreshsign)

        self.main_mdi = QMdiArea(parent=self)
        self.main_mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_mdi.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.sub_corpus = SubWindow("Corpus", self.corpus_scroll, parent=self)
        self.sub_corpus.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_corpus)

        self.sub_signlevelmenu = SubWindow("Sign", self.signlevel_panel, parent=self)
        self.sub_signlevelmenu.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_signlevelmenu)

        self.sub_visualsummary = SubWindow("Summary", self.signsummary_panel, parent=self)
        self.sub_visualsummary.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_visualsummary)

        self.show_hide_subwindows()
        self.arrange_subwindows()
        self.setCentralWidget(self.main_mdi)

        self.open_initialization_window()

    def setCorpusName(self, newtitle):
        if self.corpus is not None:
            self.corpus.name = newtitle

    # TODO KV this needs an overhaul
    # GZ - missing compound sign attribute
    def on_action_export_handshape_transcription_csv(self):
        export_csv_dialog = ExportCSVDialog(self.app_settings, parent=self)
        if export_csv_dialog.exec_():
            file_name = export_csv_dialog.location_group.get_file_path()
            option = export_csv_dialog.transcription_option_group.get_selected_option()
            if file_name:
                with open(file_name, 'w') as f:
                    transcription_writer = csv.writer(f, delimiter=',', quoting=csv.QUOTE_MINIMAL)
                    if option == 'individual':
                        transcription_writer.writerow(
                            ['GLOSS', 'FREQUENCY', 'CODER', 'LAST_UPDATED', 'NOTES', 'FOREARM', 'ESTIMATED',
                             'UNCERTAIN',
                             'INCOMPLETE', 'FINGERSPELLED', 'INITIALIZED',
                             'C1H1_S2', 'C1H1_S3', 'C1H1_S4', 'C1H1_S5', 'C1H1_S6', 'C1H1_S7', 'C1H1_S8', 'C1H1_S9',
                             'C1H1_S10', 'C1H1_S11', 'C1H1_S12', 'C1H1_S13', 'C1H1_S14', 'C1H1_S15', 'C1H1_S16',
                             'C1H1_S17',
                             'C1H1_S18', 'C1H1_S19', 'C1H1_S20', 'C1H1_S21', 'C1H1_S22', 'C1H1_S23', 'C1H1_S24',
                             'C1H1_S25',
                             'C1H1_S26', 'C1H1_S27', 'C1H1_S28', 'C1H1_S29', 'C1H1_S30', 'C1H1_S31', 'C1H1_S32',
                             'C1H1_S33',
                             'C1H1_S34',
                             'C1H2_S2', 'C1H2_S3', 'C1H2_S4', 'C1H2_S5', 'C1H2_S6', 'C1H2_S7', 'C1H2_S8', 'C1H2_S9',
                             'C1H2_S10', 'C1H2_S11', 'C1H2_S12', 'C1H2_S13', 'C1H2_S14', 'C1H2_S15', 'C1H2_S16',
                             'C1H2_S17',
                             'C1H2_S18', 'C1H2_S19', 'C1H2_S20', 'C1H2_S21', 'C1H2_S22', 'C1H2_S23', 'C1H2_S24',
                             'C1H2_S25',
                             'C1H2_S26', 'C1H2_S27', 'C1H2_S28', 'C1H2_S29', 'C1H2_S30', 'C1H2_S31', 'C1H2_S32',
                             'C1H2_S33',
                             'C1H2_S34',
                             'C2H1_S2', 'C2H1_S3', 'C2H1_S4', 'C2H1_S5', 'C2H1_S6', 'C2H1_S7', 'C2H1_S8', 'C2H1_S9',
                             'C2H1_S10', 'C2H1_S11', 'C2H1_S12', 'C2H1_S13', 'C2H1_S14', 'C2H1_S15', 'C2H1_S16',
                             'C2H1_S17',
                             'C2H1_S18', 'C2H1_S19', 'C2H1_S20', 'C2H1_S21', 'C2H1_S22', 'C2H1_S23', 'C2H1_S24',
                             'C2H1_S25',
                             'C2H1_S26', 'C2H1_S27', 'C2H1_S28', 'C2H1_S29', 'C2H1_S30', 'C2H1_S31', 'C2H1_S32',
                             'C2H1_S33',
                             'C2H1_S34',
                             'C2H2_S2', 'C2H2_S3', 'C2H2_S4', 'C2H2_S5', 'C2H2_S6', 'C2H2_S7', 'C2H2_S8', 'C2H2_S9',
                             'C2H2_S10', 'C2H2_S11', 'C2H2_S12', 'C2H2_S13', 'C2H2_S14', 'C2H2_S15', 'C2H2_S16',
                             'C2H2_S17',
                             'C2H2_S18', 'C2H2_S19', 'C2H2_S20', 'C2H2_S21', 'C2H2_S22', 'C2H2_S23', 'C2H2_S24',
                             'C2H2_S25',
                             'C2H2_S26', 'C2H2_S27', 'C2H2_S28', 'C2H2_S29', 'C2H2_S30', 'C2H2_S31', 'C2H2_S32',
                             'C2H2_S33',
                             'C2H2_S34'
                             ])

                        for sign in self.corpus:
                            info = [sign.signlevel_information.gloss, sign.signlevel_information.frequency,
                                    sign.signlevel_information.coder, str(sign.signlevel_information.update_date),
                                    sign.signlevel_information.note,
                                    sign.global_handshape_information.forearm,
                                    sign.global_handshape_information.fingerspelled,
                                    sign.global_handshape_information.initialized]
                            info.extend(sign.handshape_transcription.config.hand.get_hand_transcription_list())
                            transcription_writer.writerow(info)
                    elif option == 'single':
                        transcription_writer.writerow(
                            ['GLOSS', 'FREQUENCY', 'CODER', 'LAST_UPDATED', 'NOTES', 'FOREARM', 'ESTIMATED',
                             'UNCERTAIN',
                             'INCOMPLETE', 'FINGERSPELLED', 'INITIALIZED',
                             'C1H1', 'C1H2', 'C2H1', 'C2H2'])

                        for sign in self.corpus:
                            info = [sign.signlevel_information.gloss, sign.signlevel_information.frequency,
                                    sign.signlevel_information.coder, str(sign.signlevel_information.update_date),
                                    sign.signlevel_information.note,
                                    sign.global_handshape_information.forearm,
                                    sign.global_handshape_information.fingerspelled,
                                    sign.global_handshape_information.initialized,
                                    sign.handshape_transcription.config.hand.get_hand_transcription_string(),
                                    sign.handshape_transcription.config.hand2.get_hand_transcription_string(),
                                    sign.handshape_transcription.config2.hand.get_hand_transcription_string(),
                                    sign.handshape_transcription.config2.hand2.get_hand_transcription_string()]
                            transcription_writer.writerow(info)

                QMessageBox.information(self, 'Handshape Transcriptions Exported',
                                        'Handshape transcriptions have been successfully exported!')

    def show_hide_subwindows(self):
        self.sub_signlevelmenu.setHidden(not self.app_settings['display']['sub_signlevelmenu_show'])
        self.sub_corpus.setHidden(not self.app_settings['display']['sub_corpus_show'])
        self.sub_visualsummary.setHidden(not self.app_settings['display']['sub_visualsummary_show'])

    def on_action_export_subwindow_config(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Export Subwindow Configuration'),
                                                           os.path.join(
                                                               self.app_settings['storage']['recent_folder'],
                                                               'subwindow_config.json'),
                                                           self.tr('JSON Config (*.json)'))

        if file_name:
            subwindow_config_dict = {
                'size': (self.size().width(), self.size().height()),
                'position': (self.pos().x(), self.pos().y()),
                'sub_corpus_show': not self.sub_corpus.isHidden(),
                'sub_corpus_pos': (self.sub_corpus.pos().x(), self.sub_corpus.pos().y()),
                'sub_corpus_size': (self.sub_corpus.size().width(), self.sub_corpus.size().height()),
                'sub_signlevelmenu_show': not self.sub_signlevelmenu.isHidden(),
                'sub_signlevelmenu_pos': (self.sub_signlevelmenu.pos().x(), self.sub_signlevelmenu.pos().y()),
                'sub_signlevelmenu_size': (self.sub_signlevelmenu.size().width(), self.sub_signlevelmenu.size().height()),
                'sub_visualsummary_show': not self.sub_visualsummary.isHidden(),
                'sub_visualsummary_pos': (self.sub_visualsummary.pos().x(), self.sub_visualsummary.pos().y()),
                'sub_visualsummary_size': (self.sub_visualsummary.size().width(), self.sub_visualsummary.size().height())
            }
            with open(file_name, 'w') as f:
                json.dump(subwindow_config_dict, f, sort_keys=True, indent=4)

            QMessageBox.information(self, 'Subwindow Configuration Exported',
                                    'Subwindow Configuration has been successfully exported!')

    def on_action_import_subwindow_config(self):
        file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Import Subwindow Configuration'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('JSON Config (*.json)'))

        folder, _ = os.path.split(file_name)
        if folder:
            self.app_settings['storage']['recent_folder'] = folder

        if file_name:
            with open(file_name, 'r') as f:
                subwindow_json = json.load(f)
                for sub, config in subwindow_json.items():
                    if sub in {'size', 'sub_corpus_size', 'sub_signlevelmenu_size', 'sub_visualsummary_size'}:
                        self.app_settings['display'][sub] = QSize(*config)
                    elif sub in {'position', 'sub_corpus_pos', 'sub_signlevelmenu_pos', 'sub_visualsummary_pos'}:
                        self.app_settings['display'][sub] = QPoint(*config)
                    else:
                        self.app_settings['display'][sub] = bool(config)

            self.show_hide_subwindows()
            self.arrange_subwindows()
            self.resize(self.app_settings['display']['size'])
            self.move(self.app_settings['display']['position'])

    def arrange_subwindows(self):
        self.sub_corpus.resize(self.app_settings['display']['sub_corpus_size'])
        self.sub_corpus.move(self.app_settings['display']['sub_corpus_pos'])

        self.sub_signlevelmenu.resize(self.app_settings['display']['sub_signlevelmenu_size'])
        self.sub_signlevelmenu.move(self.app_settings['display']['sub_signlevelmenu_pos'])

        self.sub_visualsummary.resize(self.app_settings['display']['sub_visualsummary_size'])
        self.sub_visualsummary.move(self.app_settings['display']['sub_visualsummary_pos'])

        self.repaint()

    def on_action_default_view(self):
        self.sub_corpus.show()
        self.sub_signlevelmenu.show()
        self.sub_visualsummary.show()

        self.action_show_sub_corpus.setChecked(True)
        self.action_show_sub_signlevelmenu.setChecked(True)
        self.action_show_sub_visualsummary.setChecked(True)

        self.resize(QSize(2000, 1200))
        self.move(0, 23)

        self.sub_corpus.resize(QSize(340, 700))
        self.sub_corpus.move(QPoint(0, 0))

        self.sub_signlevelmenu.resize(QSize(320, 700))
        self.sub_signlevelmenu.move(QPoint(340, 0))

        self.sub_visualsummary.resize(QSize(1200, 900))
        self.sub_visualsummary.move(QPoint(660, 0))

    def on_subwindow_manually_closed(self, widget):
        if widget == self.corpus_scroll:
            self.action_show_sub_corpus.setChecked(False)
            self.on_action_show_sub_corpus()
        elif widget == self.signlevel_panel:
            self.action_show_sub_signlevelmenu.setChecked(False)
            self.on_action_show_sub_signlevelmenu()
        elif widget == self.signsummary_panel:
            self.action_show_sub_visualsummary.setChecked(False)
            self.on_action_show_sub_visualsummary()

    def on_action_show_sub_corpus(self):
        if self.action_show_sub_corpus.isChecked():
            self.sub_corpus.show()
        else:
            self.sub_corpus.hide()
        self.main_mdi.tileSubWindows()

    def on_action_show_sub_signlevelmenu(self):
        if self.action_show_sub_signlevelmenu.isChecked():
            self.sub_signlevelmenu.show()
        else:
            self.sub_signlevelmenu.hide()
        self.main_mdi.tileSubWindows()

    def on_action_show_sub_visualsummary(self):
        if self.action_show_sub_visualsummary.isChecked():
            self.sub_visualsummary.show()
        else:
            self.sub_visualsummary.hide()
        self.main_mdi.tileSubWindows()

    def handle_signlevel_edit(self, signlevel_field):
        undo_command = SignLevelUndoCommand(signlevel_field)
        self.undostack.push(undo_command)

    def handle_slot_edit(self, slot, old_prop, new_prop):
        undo_command = TranscriptionUndoCommand(slot, old_prop, new_prop)
        self.undostack.push(undo_command)

    def open_initialization_window(self):
        initialization = InitializationDialog(self.app_ctx,
                                              self.on_action_new_corpus,
                                              self.on_action_load_corpus,
                                              self.app_settings['metadata']['coder'],
                                              parent=self)
        response = initialization.exec_()
        if not response:  # close the window or press cancel
            self.on_action_new_corpus(False)

    def handle_sign_selected(self, sign):
        selected_sign = sign

        self.current_sign = selected_sign
        self.action_delete_sign.setEnabled(True)
        self.signlevel_panel.sign = selected_sign
        self.signlevel_panel.enable_module_buttons(True)
        self.signsummary_panel.refreshsign(self.current_sign)

    def handle_app_settings(self):
        self.app_settings = defaultdict(dict)

        self.app_qsettings = QSettings('UBC Phonology Tools',
                                       application='Sign Language Phonetic Annotator and Analyzer')

        self.app_qsettings.beginGroup('storage')
        self.app_settings['storage']['recent_folder'] = self.app_qsettings.value(
            'recent_folder',
            defaultValue=os.path.expanduser('~/Documents'))
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
        self.app_settings['display']['size'] = self.app_qsettings.value('size', defaultValue=QSize(2000, 1200))
        self.app_settings['display']['position'] = self.app_qsettings.value('position', defaultValue=QPoint(0, 23))

        self.app_settings['display']['sub_corpus_show'] = bool(self.app_qsettings.value('sub_corpus_show',
                                                                                        defaultValue=True))
        self.app_settings['display']['sub_corpus_pos'] = self.app_qsettings.value('sub_corpus_pos',
                                                                                  defaultValue=QPoint(0, 0))
        self.app_settings['display']['sub_corpus_size'] = self.app_qsettings.value('sub_corpus_size',
                                                                                   defaultValue=QSize(340, 700))

        self.app_settings['display']['sub_signlevelmenu_show'] = bool(self.app_qsettings.value('sub_signlevelmenu_show',
                                                                                               defaultValue=True))
        self.app_settings['display']['sub_signlevelmenu_pos'] = self.app_qsettings.value('sub_signlevelmenu_pos',
                                                                                         defaultValue=QPoint(340, 0))
        self.app_settings['display']['sub_signlevelmenu_size'] = self.app_qsettings.value('sub_signlevelmenu_size',
                                                                                          defaultValue=QSize(320, 700))

        self.app_settings['display']['sub_visualsummary_show'] = bool(self.app_qsettings.value('sub_visualsummary_show',
                                                                                               defaultValue=True))
        self.app_settings['display']['sub_visualsummary_pos'] = self.app_qsettings.value('sub_visualsummary_pos',
                                                                                         defaultValue=QPoint(660, 0))
        self.app_settings['display']['sub_visualsummary_size'] = self.app_qsettings.value('sub_visualsummary_size',
                                                                                          defaultValue=QSize(1200, 900))

        self.app_settings['display']['sig_figs'] = self.app_qsettings.value('sig_figs', defaultValue=2)
        self.app_settings['display']['tooltips'] = bool(self.app_qsettings.value('tooltips', defaultValue=True))
        self.app_settings['display']['entryid_digits'] = self.app_qsettings.value('entryid_digits', defaultValue=4)
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('metadata')
        self.app_settings['metadata']['coder'] = self.app_qsettings.value('coder', defaultValue='NEWUSERNAME')
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('reminder')
        self.app_settings['reminder']['overwrite'] = bool(self.app_qsettings.value('overwrite', defaultValue=True))
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('signdefaults')
        self.app_settings['signdefaults']['handdominance'] = self.app_qsettings.value('handdominance',
                                                                                      defaultValue='R')
        self.app_settings['signdefaults']['signtype'] = self.app_qsettings.value('signtype', defaultValue='none')
        self.app_settings['signdefaults']['xslot_generation'] = self.app_qsettings.value('xslot_generation',
                                                                                         defaultValue='none')
        self.app_qsettings.beginGroup('partial_xslots')
        self.app_settings['signdefaults']['partial_xslots'] = defaultdict(dict)
        self.app_settings['signdefaults']['partial_xslots'][str(Fraction(1, 2))] = \
            self.app_qsettings.value(str(Fraction(1, 2)), defaultValue=True, type=bool)
        self.app_settings['signdefaults']['partial_xslots'][str(Fraction(1, 3))] = \
            self.app_qsettings.value(str(Fraction(1, 3)), defaultValue=True, type=bool)
        self.app_settings['signdefaults']['partial_xslots'][str(Fraction(1, 4))] = \
            self.app_qsettings.value(str(Fraction(1, 4)), defaultValue=False, type=bool)
        self.app_qsettings.endGroup()  # partial_xslots
        self.app_qsettings.endGroup()  # signdefaults

        self.app_qsettings.beginGroup('location')
        self.app_settings['location']['loctype'] = self.app_qsettings.value('loctype', defaultValue='none')
        self.app_qsettings.endGroup()  # location

    def check_storage(self):
        if not os.path.exists(self.app_settings['storage']['corpora']):
            os.makedirs(self.app_settings['storage']['corpora'])

        if not os.path.exists(self.app_settings['storage']['image']):
            os.makedirs(self.app_settings['storage']['image'])

    def save_app_settings(self):
        self.app_qsettings = QSettings('UBC Phonology Tools',
                                       application='Sign Language Phonetic Annotator and Analyzer')

        self.app_qsettings.beginGroup('storage')
        self.app_qsettings.setValue('recent_folder', self.app_settings['storage']['recent_folder'])
        self.app_qsettings.setValue('corpora', self.app_settings['storage']['corpora'])
        self.app_qsettings.setValue('image', self.app_settings['storage']['image'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('display')
        self.app_qsettings.setValue('size', self.size())  # MainWindow size
        self.app_qsettings.setValue('position', self.pos())  # MainWindow position
        self.app_qsettings.setValue('sub_corpus_show', not self.sub_corpus.isHidden())
        self.app_qsettings.setValue('sub_corpus_pos', self.sub_corpus.pos())
        self.app_qsettings.setValue('sub_corpus_size', self.sub_corpus.size())

        self.app_qsettings.setValue('sig_figs', self.app_settings['display']['sig_figs'])
        self.app_qsettings.setValue('tooltips', self.app_settings['display']['tooltips'])
        self.app_qsettings.setValue('entryid_digits', self.app_settings['display']['entryid_digits'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('metadata')
        self.app_qsettings.setValue('coder', self.app_settings['metadata']['coder'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('reminder')
        self.app_qsettings.setValue('overwrite', self.app_settings['reminder']['overwrite'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('signdefaults')
        self.app_qsettings.setValue('handdominance', self.app_settings['signdefaults']['handdominance'])
        self.app_qsettings.setValue('signtype', self.app_settings['signdefaults']['signtype'])
        self.app_qsettings.setValue('xslot_generation', self.app_settings['signdefaults']['xslot_generation'])

        self.app_qsettings.beginGroup('partial_xslots')
        for fracstring in self.app_settings['signdefaults']['partial_xslots'].keys():
            fractionchecked = self.app_settings['signdefaults']['partial_xslots'][fracstring]
            self.app_qsettings.setValue(fracstring, fractionchecked)
        self.app_qsettings.endGroup()  # partial_xslots

        self.app_qsettings.endGroup()  # signdefaults

        self.app_qsettings.beginGroup('location')
        self.app_qsettings.setValue('loctype', self.app_settings['location']['loctype'])
        self.app_qsettings.endGroup()  # location

    def on_action_define_location(self):
        location_definer = LocationDefinerDialog(self.system_default_locations,
                                                 self.corpus.location_definition,
                                                 self.app_settings,
                                                 self.app_ctx,
                                                 parent=self)
        location_definer.saved_locations.connect(self.save_new_locations)
        location_definer.exec_()

    def save_new_locations(self, new_locations):
        # TODO: need to reimplement this once corpus class is there
        self.corpus.location_definition = new_locations

    def update_status_bar(self, text):
        self.status_bar.showMessage(text)

    def on_action_edit_preference(self):
        pref_dialog = PreferenceDialog(self.app_settings,
                                       timingfracsinuse=self.getcurrentlyused_timingfractions(),
                                       parent=self)
        pref_dialog.xslotgeneration_changed.connect(self.handle_xslotgeneration_changed)
        pref_dialog.prefs_saved.connect(self.signsummary_panel.refreshsign)
        pref_dialog.exec_()

    def handle_xslotgeneration_changed(self, prev_xslotgen, new_xslotgen):
        self.signlevel_panel.enable_module_buttons(len(self.corpus.signs) > 0)

    def getcurrentlyused_timingfractions(self):
        fractionsinuse = []
        for sign in self.corpus.signs:
            timedmodules = sign.gettimedmodules()
            for modulecollection in timedmodules:
                for module in modulecollection.values():
                    timingintervals = module.timingintervals
                    for tint in timingintervals:
                        startfrac = tint.startpoint.fractionalpart
                        if startfrac not in fractionsinuse:
                            fractionsinuse.append(startfrac)
                        endfrac = tint.endpoint.fractionalpart
                        if endfrac not in fractionsinuse:
                            fractionsinuse.append(endfrac)
            structuralfrac = sign.xslotstructure.additionalfraction
            if structuralfrac not in [0, 1] and structuralfrac not in fractionsinuse:
                fractionsinuse.append(structuralfrac)
        return fractionsinuse

    # TODO KV is this for checking whether it's ok to change x-slot settings partway through a session/corpus?
    # def check_xslotdivisions(self, beforedict, afterdict):
    #     divisionsbefore = [Fraction(fracstring) for fracstring in beforedict.keys() if beforedict[fracstring]]
    #     fractionsbefore = []
    #     for frac in divisionsbefore:
    #         for num in range(1, frac.numerator):
    #             fracmultiple = num * frac
    #             if fracmultiple not in fractionsbefore:
    #                 fractionsbefore.append(fracmultiple)
    #     divisionsafter = [Fraction(fracstring) for fracstring in afterdict.keys() if afterdict[fracstring]]
    #     fractionsafter = []
    #     for frac in divisionsafter:
    #         for num in range(1, frac.numerator):
    #             fracmultiple = num * frac
    #             if fracmultiple not in fractionsafter:
    #                 fractionsafter.append(fracmultiple)
    #
    #     # divisionslost = [divn for divn in divisionsbefore if divn not in divisionsafter]
    #     fractionslost = [frac for frac in fractionsbefore if frac not in fractionsafter]
    #
    #     fractionsatrisk = []
    #
    #     for sign in self.corpus.signs:
    #         timedmodules = sign.gettimedmodules()
    #         for modulecollection in timedmodules:
    #             for module in modulecollection:
    #                 timingintervals = module.timingintervals
    #                 for tint in timingintervals:
    #                     startfrac = tint.startpoint.fractionalpart
    #                     endfrac = tint.endpoint.fractionalpart
    #
    #                     # if we're losing a division that is used in at least one sign...
    #                     if startfrac in fractionslost and startfrac not in fractionsatrisk:
    #                         fractionsatrisk.append(startfrac)
    #                     if endfrac in fractionslost and endfrac not in fractionsatrisk:
    #                         fractionsatrisk.append(endfrac)
    #
    #     return fractionsatrisk

    @check_unsaved_corpus
    def on_action_save(self, clicked):
        # signlevel_info = self.signlevelinfo_scroll.get_value()
        # location_transcription_info = self.parameter_scroll.location_layout.get_location_value()
        # global_hand_info = self.transcription_scroll.global_info.get_value()
        # configs = [self.transcription_scroll.config1.get_value(),
        #            self.transcription_scroll.config2.get_value()]
        #
        # # if missing then some of them will be none
        # if signlevel_info and location_transcription_info and global_hand_info and configs:
        #     if self.current_sign:
        #         response = QMessageBox.question(self, 'Overwrite the current sign',
        #                                         'Do you want to overwrite the existing transcriptions?')
        #         if response == QMessageBox.Yes:
        #             self.corpus.remove_sign(self.current_sign)
        #         else:
        #             return
        #
        #     if not self.new_sign:
        #         self.new_sign = Sign(signlevel_info, global_hand_info, configs, location_transcription_info)
        #     # new_sign = self.new_sign if self.new_sign else Sign(signlevel_info, global_hand_info, configs, location_transcription_info)
        #     self.corpus.add_sign(self.new_sign)
        #     self.corpus_view.updated_glosses(self.corpus.get_sign_glosses(), self.new_sign.signlevel_information.gloss)
        #     self.current_sign = self.new_sign
        #     self.action_delete_sign.setEnabled(True)

        if self.corpus.path:
            self.corpus.name = self.corpus_display.corpus_title.text()
            self.save_corpus_binary()

        self.undostack.clear()

    @check_unsaved_corpus
    def on_action_saveas(self, clicked):
        self.corpus.name = self.corpus_display.corpus_title.text()
        name = self.corpus.name
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   self.tr('Save Corpus'),
                                                   os.path.join(self.app_settings['storage']['recent_folder'],
                                                                name + '.slpaa'),  # 'corpus.slpaa'),
                                                   self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_name:
            self.corpus.path = file_name
            folder, _ = os.path.split(file_name)
            if folder:
                self.app_settings['storage']['recent_folder'] = folder

        self.save_corpus_binary()

    def save_corpus_binary(self):
        with open(self.corpus.path, 'wb') as f:
            pickle.dump(self.corpus.serialize(), f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_corpus_binary(self, path):
        with open(path, 'rb') as f:
            # corpus = Corpus(serializedcorpus=pickle.load(f))
            corpus = Corpus(serializedcorpus=renamed_load(f))
            # in case we're loading a corpus that was originally created on a different machine / in a different folder
            corpus.path = path
            return corpus

    def on_action_copy(self, clicked):
        pass
        # TODO: implement

    def on_action_paste(self, clicked):
        pass
        # TODO: implement

    # TODO KV check whether current corpus has been saved
    def on_action_new_corpus(self, clicked):
        self.current_sign = None
        self.action_delete_sign.setEnabled(False)

        self.corpus = Corpus(signs=None, location_definition=deepcopy(SAMPLE_LOCATIONS))

        self.corpus_display.clear()
        self.signlevel_panel.clear()
        self.signlevel_panel.enable_module_buttons(False)
        self.signsummary_panel.refreshsign()

    # TODO KV check whether current corpus has been saved
    def on_action_load_corpus(self, clicked):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           self.tr('Open Corpus'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        folder, _ = os.path.split(file_name)
        if folder:
            self.app_settings['storage']['recent_folder'] = folder

        self.corpus = self.load_corpus_binary(file_name)
        self.corpus_display.corpus_title.setText(self.corpus.name)  # TODO KV better / more abstract access?
        self.corpus_display.updated_signs(self.corpus.signs)
        if len(self.corpus.signs) > 0:
            self.corpus_display.selected_sign.emit((list(self.corpus.signs))[0])
        else: # if loading a blank corpus
            self.signsummary_panel.mainwindow.current_sign = None # refreshsign() checks for this
            self.signsummary_panel.refreshsign(None)
            self.signlevel_panel.clear()
            self.signlevel_panel.enable_module_buttons(False)
            

        return self.corpus is not None  # bool(Corpus)

    def on_action_close(self, clicked):
        self.close()

    def on_action_new_sign(self, clicked):
        self.current_sign = None
        # self.new_sign = None
        self.action_delete_sign.setEnabled(False)

        self.corpus_display.corpus_view.clearSelection()
        self.signlevel_panel.clear()
        self.signlevel_panel.handle_signlevelbutton_click()

    def on_action_delete_sign(self, clicked):
        response = QMessageBox.question(self, 'Delete the selected sign',
                                        'Do you want to delete the selected sign?')
        if response == QMessageBox.Yes:
            previous = self.corpus.get_previous_sign(self.current_sign.signlevel_information.gloss)

            self.corpus.remove_sign(self.current_sign)
            self.corpus_display.updated_signs(self.corpus.signs, previous)

            self.select_sign([previous])
            self.handle_sign_selected(previous)
            # TODO KV need to also have that sign selected in the corpus view,
            #  as well as displaying its summary in the xslot view

    # TODO KV finish implementing
    def select_sign(self, signstoselect):
        selectionmodel = self.corpus_display.corpus_view.selectionModel()
        indices = []
        for sign in signstoselect:
            indices.append(list(self.corpus.signs).index(sign))
        # print(indices)

    @check_unsaved_change
    def closeEvent(self, event):
        self.save_app_settings()
        super().closeEvent(event)
