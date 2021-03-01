import os
import pickle
import json
import csv
from collections import defaultdict
from copy import deepcopy
#from getpass import getuser
from datetime import date
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
    QKeySequence,
    QPixmap
)

# Ref: https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html
from gui.initialization_dialog import InitializationDialog
from gui.corpus_view import CorpusView
from gui.location_definer import LocationDefinerDialog
from gui.corpus_summary_dialog import CorpusSummaryDialog
from gui.export_csv_dialog import ExportCSVDialog
from gui.panel import (
    LexicalInformationPanel,
    HandTranscriptionPanel,
    HandIllustrationPanel,
    ParameterPanel
)
from gui.preference_dialog import PreferenceDialog
from gui.decorator import check_unsaved_change, check_unsaved_corpus, check_duplicated_gloss
from gui.predefined_handshape_dialog import PredefinedHandshapeDialog
from gui.undo_command import TranscriptionUndoCommand, PredefinedUndoCommand, LexicalUndoCommand
from constant import SAMPLE_LOCATIONS
from lexicon.lexicon_classes import (
    Corpus,
    Sign
)


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

        # system-default locations
        self.system_default_locations = deepcopy(SAMPLE_LOCATIONS)

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
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_C))
        action_copy.triggered.connect(self.on_action_copy)
        action_copy.setCheckable(False)

        # paste
        action_paste = QAction(QIcon(self.app_ctx.icons['paste']), 'Paste', parent=self)
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
        action_new_corpus = QAction(QIcon(self.app_ctx.icons['blank16']), 'New corpus', parent=self)
        action_new_corpus.setStatusTip('Create a new corpus')
        action_new_corpus.triggered.connect(self.on_action_new_corpus)
        action_new_corpus.setCheckable(False)

        # load corpus
        action_load_corpus = QAction(QIcon(self.app_ctx.icons['load16']), 'Load corpus...', parent=self)
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

        # output handshape transcription to csv
        action_export_handshape_transcription_csv = QAction('Export handshape transcription as CSV...', parent=self)
        action_export_handshape_transcription_csv.triggered.connect(self.on_action_export_handshape_transcription_csv)

        # new sign
        action_new_sign = QAction(QIcon(self.app_ctx.icons['plus']), 'New sign', parent=self)
        action_new_sign.setStatusTip('Create a new sign')
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_N))
        action_new_sign.triggered.connect(self.on_action_new_sign)
        action_new_sign.setCheckable(False)

        # delete sign
        self.action_delete_sign = QAction(QIcon(self.app_ctx.icons['delete']), 'Delete sign', parent=self)
        self.action_delete_sign.setEnabled(False)
        self.action_delete_sign.setStatusTip('Delete the selected sign')
        self.action_delete_sign.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_Delete))
        self.action_delete_sign.triggered.connect(self.on_action_delete_sign)
        self.action_delete_sign.setCheckable(False)

        # predefined handshape
        action_predefined_handshape = QAction(QIcon(self.app_ctx.icons['hand']), 'Predefined handshape', parent=self)
        action_predefined_handshape.setStatusTip('Open predefined handshape window')
        action_predefined_handshape.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_P))
        action_predefined_handshape.triggered.connect(self.on_action_predefined_handshape)
        action_predefined_handshape.setCheckable(False)

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

        # show/hide lexical subwindow
        self.action_show_sub_lexical = QAction('Show lexical information', parent=self)
        self.action_show_sub_lexical.setStatusTip('Show/hide lexical information')
        self.action_show_sub_lexical.triggered.connect(self.on_action_show_sub_lexical)
        self.action_show_sub_lexical.setCheckable(True)
        self.action_show_sub_lexical.setChecked(self.app_settings['display']['sub_lexical_show'])

        # show/hide transcription subwindow
        self.action_show_sub_transcription = QAction('Show transcription', parent=self)
        self.action_show_sub_transcription.setStatusTip('Show/hide transcription')
        self.action_show_sub_transcription.triggered.connect(self.on_action_show_sub_transcription)
        self.action_show_sub_transcription.setCheckable(True)
        self.action_show_sub_transcription.setChecked(self.app_settings['display']['sub_transcription_show'])

        # show/hide illustration subwindow
        self.action_show_sub_illustration = QAction('Show hand illustration', parent=self)
        self.action_show_sub_illustration.setStatusTip('Show/hide hand illustration')
        self.action_show_sub_illustration.triggered.connect(self.on_action_show_sub_illustration)
        self.action_show_sub_illustration.setCheckable(True)
        self.action_show_sub_illustration.setChecked(self.app_settings['display']['sub_illustration_show'])

        # show/hide parameter subwindow
        self.action_show_sub_parameter = QAction('Show parameter specifier', parent=self)
        self.action_show_sub_parameter.setStatusTip('Show/hide parameter specifier')
        self.action_show_sub_parameter.triggered.connect(self.on_action_show_sub_parameter)
        self.action_show_sub_parameter.setCheckable(True)
        self.action_show_sub_parameter.setChecked(True)
        self.action_show_sub_parameter.setChecked(self.app_settings['display']['sub_parameter_show'])

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
        toolbar.addSeparator()
        toolbar.addAction(action_undo)
        toolbar.addAction(action_redo)
        toolbar.addSeparator()
        toolbar.addAction(action_copy)
        toolbar.addAction(action_paste)
        toolbar.addSeparator()
        toolbar.addAction(action_predefined_handshape)

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
        menu_edit.addAction(self.action_show_sub_lexical)
        menu_edit.addAction(self.action_show_sub_transcription)
        menu_edit.addAction(self.action_show_sub_illustration)
        menu_edit.addAction(self.action_show_sub_parameter)
        menu_edit.addSeparator()
        menu_edit.addAction(action_export_subwindow_config)
        menu_edit.addAction(action_import_subwindow_config)

        menu_location = main_menu.addMenu('&Location')
        menu_location.addAction(action_define_location)

        self.corpus_view = CorpusView('Untitled', parent=self)
        self.corpus_view.selected_gloss.connect(self.handle_sign_selected)

        self.corpus_scroll = QScrollArea(parent=self)
        self.corpus_scroll.setWidgetResizable(True)
        self.corpus_scroll.setWidget(self.corpus_view)

        self.lexical_scroll = LexicalInformationPanel(self.app_settings['metadata']['coder'], self.today, parent=self)
        self.lexical_scroll.finish_edit.connect(self.handle_lexical_edit)

        self.illustration_scroll = HandIllustrationPanel(self.app_ctx, parent=self)

        self.transcription_scroll = HandTranscriptionPanel(self.app_ctx.predefined, parent=self)
        self.transcription_scroll.config1.slot_on_focus.connect(self.update_status_bar)
        self.transcription_scroll.config1.slot_num_on_focus.connect(self.update_hand_illustration)
        self.transcription_scroll.config1.slot_leave.connect(self.status_bar.clearMessage)
        self.transcription_scroll.config1.slot_leave.connect(self.illustration_scroll.set_neutral_img)
        self.transcription_scroll.config1.slot_finish_edit.connect(self.handle_slot_edit)

        self.transcription_scroll.config2.slot_on_focus.connect(self.update_status_bar)
        self.transcription_scroll.config2.slot_num_on_focus.connect(self.update_hand_illustration)
        self.transcription_scroll.config2.slot_leave.connect(self.status_bar.clearMessage)
        self.transcription_scroll.config2.slot_leave.connect(self.illustration_scroll.set_neutral_img)
        self.transcription_scroll.config2.slot_finish_edit.connect(self.handle_slot_edit)

        self.parameter_scroll = ParameterPanel(dict(), self.app_ctx, parent=self)

        self.main_mdi = QMdiArea(parent=self)
        self.main_mdi.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.main_mdi.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.sub_parameter = SubWindow('Parameter', self.parameter_scroll, parent=self)
        self.sub_parameter.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_parameter)

        self.sub_illustration = SubWindow('Slot illustration', self.illustration_scroll, parent=self)
        self.sub_illustration.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_illustration)

        self.sub_transcription = SubWindow('Hand transcription', self.transcription_scroll, parent=self)
        self.sub_transcription.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_transcription)

        self.sub_lexical = SubWindow('Lexical information', self.lexical_scroll, parent=self)
        self.sub_lexical.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_lexical)

        self.sub_corpus = SubWindow('Corpus', self.corpus_scroll, parent=self)
        self.sub_corpus.subwindow_closed.connect(self.on_subwindow_manually_closed)
        self.main_mdi.addSubWindow(self.sub_corpus)

        self.show_hide_subwindows()
        self.arrange_subwindows()
        self.setCentralWidget(self.main_mdi)

        self.open_initialization_window()

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
                            info = [sign.lexical_information.gloss, sign.lexical_information.frequency,
                                    sign.lexical_information.coder, str(sign.lexical_information.update_date),
                                    sign.lexical_information.note,
                                    sign.global_handshape_information.forearm,
                                    sign.global_handshape_information.estimated,
                                    sign.global_handshape_information.uncertain,
                                    sign.global_handshape_information.incomplete,
                                    sign.global_handshape_information.fingerspelled,
                                    sign.global_handshape_information.initialized]
                            info.extend(sign.handshape_transcription.config1.hand1.get_hand_transcription_list())
                            info.extend(sign.handshape_transcription.config1.hand2.get_hand_transcription_list())
                            info.extend(sign.handshape_transcription.config2.hand1.get_hand_transcription_list())
                            info.extend(sign.handshape_transcription.config2.hand2.get_hand_transcription_list())
                            transcription_writer.writerow(info)
                    elif option == 'single':
                        transcription_writer.writerow(
                            ['GLOSS', 'FREQUENCY', 'CODER', 'LAST_UPDATED', 'NOTES', 'FOREARM', 'ESTIMATED',
                             'UNCERTAIN',
                             'INCOMPLETE', 'FINGERSPELLED', 'INITIALIZED',
                             'C1H1', 'C1H2', 'C2H1', 'C2H2'])

                        for sign in self.corpus:
                            info = [sign.lexical_information.gloss, sign.lexical_information.frequency,
                                    sign.lexical_information.coder, str(sign.lexical_information.update_date),
                                    sign.lexical_information.note,
                                    sign.global_handshape_information.forearm,
                                    sign.global_handshape_information.estimated,
                                    sign.global_handshape_information.uncertain,
                                    sign.global_handshape_information.incomplete,
                                    sign.global_handshape_information.fingerspelled,
                                    sign.global_handshape_information.initialized,
                                    sign.handshape_transcription.config1.hand1.get_hand_transcription_string(),
                                    sign.handshape_transcription.config1.hand2.get_hand_transcription_string(),
                                    sign.handshape_transcription.config2.hand1.get_hand_transcription_string(),
                                    sign.handshape_transcription.config2.hand2.get_hand_transcription_string()]
                            transcription_writer.writerow(info)

                QMessageBox.information(self, 'Handshape Transcriptions Exported',
                                        'Handshape transcriptions have been successfully exported!')

    def show_hide_subwindows(self):
        self.sub_parameter.setHidden(not self.app_settings['display']['sub_parameter_show'])
        self.sub_illustration.setHidden(not self.app_settings['display']['sub_illustration_show'])
        self.sub_transcription.setHidden(not self.app_settings['display']['sub_transcription_show'])
        self.sub_lexical.setHidden(not self.app_settings['display']['sub_lexical_show'])
        self.sub_corpus.setHidden(not self.app_settings['display']['sub_corpus_show'])

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
                'sub_lexical_show': not self.sub_lexical.isHidden(),
                'sub_lexical_pos': (self.sub_lexical.pos().x(), self.sub_lexical.pos().y()),
                'sub_lexical_size': (self.sub_lexical.size().width(), self.sub_lexical.size().height()),
                'sub_transcription_show': not self.sub_transcription.isHidden(),
                'sub_transcription_pos': (self.sub_transcription.pos().x(), self.sub_transcription.pos().y()),
                'sub_transcription_size': (self.sub_transcription.size().width(), self.sub_transcription.size().height()),
                'sub_illustration_show': not self.sub_illustration.isHidden(),
                'sub_illustration_pos': (self.sub_illustration.pos().x(), self.sub_illustration.pos().y()),
                'sub_illustration_size': (self.sub_illustration.size().width(), self.sub_illustration.size().height()),
                'sub_parameter_show': not self.sub_parameter.isHidden(),
                'sub_parameter_pos': (self.sub_parameter.pos().x(), self.sub_parameter.pos().y()),
                'sub_parameter_size': (self.sub_parameter.size().width(), self.sub_parameter.size().height())
            }
            with open(file_name, 'w') as f:
                json.dump(subwindow_config_dict, f, sort_keys=True, indent=4)

            QMessageBox.information(self, 'Subwindow Configuration Exported', 'Subwindow Configuration has been successfully exported!')

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
                    if sub in {'size', 'sub_corpus_size', 'sub_lexical_size', 'sub_transcription_size',
                               'sub_illustration_size', 'sub_parameter_size'}:
                        self.app_settings['display'][sub] = QSize(*config)
                    elif sub in {'position', 'sub_corpus_pos', 'sub_lexical_pos', 'sub_transcription_pos',
                                 'sub_illustration_pos', 'sub_parameter_pos'}:
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

        self.sub_lexical.resize(self.app_settings['display']['sub_lexical_size'])
        self.sub_lexical.move(self.app_settings['display']['sub_lexical_pos'])

        self.sub_transcription.resize(self.app_settings['display']['sub_transcription_size'])
        self.sub_transcription.move(self.app_settings['display']['sub_transcription_pos'])

        self.sub_illustration.resize(self.app_settings['display']['sub_illustration_size'])
        self.sub_illustration.move(self.app_settings['display']['sub_illustration_pos'])

        self.sub_parameter.resize(self.app_settings['display']['sub_parameter_size'])
        self.sub_parameter.move(self.app_settings['display']['sub_parameter_pos'])

        self.repaint()

    def on_action_default_view(self):
        self.sub_corpus.show()
        self.sub_lexical.show()
        self.sub_transcription.show()
        self.sub_illustration.show()
        self.sub_parameter.show()

        self.action_show_sub_corpus.setChecked(True)
        self.action_show_sub_lexical.setChecked(True)
        self.action_show_sub_transcription.setChecked(True)
        self.action_show_sub_illustration.setChecked(True)
        self.action_show_sub_parameter.setChecked(True)

        self.resize(QSize(1280, 755))
        self.move(0, 23)

        self.sub_corpus.resize(QSize(180, 700))
        self.sub_corpus.move(QPoint(0, 0))

        self.sub_lexical.resize(QSize(300, 350))
        self.sub_lexical.move(QPoint(180, 0))

        self.sub_transcription.resize(QSize(800, 350))
        self.sub_transcription.move(QPoint(480, 0))

        self.sub_illustration.resize(QSize(400, 350))
        self.sub_illustration.move(QPoint(180, 350))

        self.sub_parameter.resize(QSize(700, 350))
        self.sub_parameter.move(QPoint(580, 350))

    def on_subwindow_manually_closed(self, widget):
        if widget == self.corpus_scroll:
            self.action_show_sub_corpus.setChecked(False)
            self.on_action_show_sub_corpus()
        elif widget == self.lexical_scroll:
            self.action_show_sub_lexical.setChecked(False)
            self.on_action_show_sub_lexical()
        elif widget == self.transcription_scroll:
            self.action_show_sub_transcription.setChecked(False)
            self.on_action_show_sub_transcription()
        elif widget == self.illustration_scroll:
            self.action_show_sub_illustration.setChecked(False)
            self.on_action_show_sub_illustration()
        elif widget == self.parameter_scroll:
            self.action_show_sub_parameter.setChecked(False)
            self.on_action_show_sub_parameter()

    def on_action_show_sub_corpus(self):
        if self.action_show_sub_corpus.isChecked():
            self.sub_corpus.show()
        else:
            self.sub_corpus.hide()
        self.main_mdi.tileSubWindows()

    def on_action_show_sub_lexical(self):
        if self.action_show_sub_lexical.isChecked():
            self.sub_lexical.show()
        else:
            self.sub_lexical.hide()
        self.main_mdi.tileSubWindows()

    def on_action_show_sub_transcription(self):
        if self.action_show_sub_transcription.isChecked():
            self.sub_transcription.show()
        else:
            self.sub_transcription.hide()
        self.main_mdi.tileSubWindows()

    def on_action_show_sub_illustration(self):
        if self.action_show_sub_illustration.isChecked():
            self.sub_illustration.show()
        else:
            self.sub_illustration.hide()
        self.main_mdi.tileSubWindows()

    def on_action_show_sub_parameter(self):
        if self.action_show_sub_parameter.isChecked():
            self.sub_parameter.show()
        else:
            self.sub_parameter.hide()
        self.main_mdi.tileSubWindows()

    def handle_lexical_edit(self, lexical_field):
        undo_command = LexicalUndoCommand(lexical_field)
        self.undostack.push(undo_command)

    def handle_slot_edit(self, slot, old_prop, new_prop):
        undo_command = TranscriptionUndoCommand(slot, old_prop, new_prop)
        self.undostack.push(undo_command)

    def open_initialization_window(self):
        initialization = InitializationDialog(self.app_ctx, self.on_action_new_corpus, self.on_action_load_corpus, self.app_settings['metadata']['coder'], parent=self)
        response = initialization.exec_()
        if not response:  # close the window or press cancel
            self.on_action_new_corpus(False)

    def handle_sign_selected(self, gloss):
        selected_sign = self.corpus.get_sign_by_gloss(gloss)

        self.current_sign = selected_sign
        self.action_delete_sign.setEnabled(True)

        self.lexical_scroll.set_value(selected_sign.lexical_information)
        self.transcription_scroll.set_value(selected_sign.global_handshape_information,
                                            selected_sign.handshape_transcription)
        self.parameter_scroll.set_value(selected_sign.location)

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
        self.app_settings['display']['size'] = self.app_qsettings.value('size', defaultValue=QSize(1280, 755))
        self.app_settings['display']['position'] = self.app_qsettings.value('position', defaultValue=QPoint(0, 23))

        self.app_settings['display']['sub_corpus_show'] = bool(self.app_qsettings.value('sub_corpus_show', defaultValue=True))
        self.app_settings['display']['sub_corpus_pos'] = self.app_qsettings.value('sub_corpus_pos', defaultValue=QPoint(0, 0))
        self.app_settings['display']['sub_corpus_size'] = self.app_qsettings.value('sub_corpus_size', defaultValue=QSize(180, 700))

        self.app_settings['display']['sub_lexical_show'] = bool(self.app_qsettings.value('sub_lexical_show', defaultValue=True))
        self.app_settings['display']['sub_lexical_pos'] = self.app_qsettings.value('sub_lexical_pos', defaultValue=QPoint(180, 0))
        self.app_settings['display']['sub_lexical_size'] = self.app_qsettings.value('sub_lexical_size', defaultValue=QSize(300, 350))

        self.app_settings['display']['sub_transcription_show'] = bool(self.app_qsettings.value('sub_transcription_show', defaultValue=True))
        self.app_settings['display']['sub_transcription_pos'] = self.app_qsettings.value('sub_transcription_pos', defaultValue=QPoint(480, 0))
        self.app_settings['display']['sub_transcription_size'] = self.app_qsettings.value('sub_transcription_size', defaultValue=QSize(800, 350))

        self.app_settings['display']['sub_illustration_show'] = bool(self.app_qsettings.value('sub_illustration_show', defaultValue=True))
        self.app_settings['display']['sub_illustration_pos'] = self.app_qsettings.value('sub_illustration_pos', defaultValue=QPoint(180, 350))
        self.app_settings['display']['sub_illustration_size'] = self.app_qsettings.value('sub_illustration_size', defaultValue=QSize(400, 350))

        self.app_settings['display']['sub_parameter_show'] = bool(self.app_qsettings.value('sub_parameter_show', defaultValue=True))
        self.app_settings['display']['sub_parameter_pos'] = self.app_qsettings.value('sub_parameter_pos', defaultValue=QPoint(580, 350))
        self.app_settings['display']['sub_parameter_size'] = self.app_qsettings.value('sub_parameter_size', defaultValue=QSize(700, 350))

        self.app_settings['display']['sig_figs'] = self.app_qsettings.value('sig_figs', defaultValue=2)
        self.app_settings['display']['tooltips'] = bool(self.app_qsettings.value('tooltips', defaultValue=True))
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('metadata')
        #self.app_settings['metadata']['coder'] = self.app_qsettings.value('coder', defaultValue=getuser())
        self.app_settings['metadata']['coder'] = self.app_qsettings.value('coder', defaultValue='NEWUSERNAME')
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('reminder')
        self.app_settings['reminder']['overwrite'] = bool(self.app_qsettings.value('overwrite', defaultValue=True))
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

        self.app_qsettings.setValue('sub_lexical_show', not self.sub_lexical.isHidden())
        self.app_qsettings.setValue('sub_lexical_pos', self.sub_lexical.pos())
        self.app_qsettings.setValue('sub_lexical_size', self.sub_lexical.size())

        self.app_qsettings.setValue('sub_transcription_show', not self.sub_transcription.isHidden())
        self.app_qsettings.setValue('sub_transcription_pos', self.sub_transcription.pos())
        self.app_qsettings.setValue('sub_transcription_size', self.sub_transcription.size())

        self.app_qsettings.setValue('sub_illustration_show', not self.sub_illustration.isHidden())
        self.app_qsettings.setValue('sub_illustration_pos', self.sub_illustration.pos())
        self.app_qsettings.setValue('sub_illustration_size', self.sub_illustration.size())

        self.app_qsettings.setValue('sub_parameter_show', not self.sub_parameter.isHidden())
        self.app_qsettings.setValue('sub_parameter_pos', self.sub_parameter.pos())
        self.app_qsettings.setValue('sub_parameter_size', self.sub_parameter.size())

        self.app_qsettings.setValue('sig_figs', self.app_settings['display']['sig_figs'])
        self.app_qsettings.setValue('tooltips', self.app_settings['display']['tooltips'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('metadata')
        self.app_qsettings.setValue('coder', self.app_settings['metadata']['coder'])
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('reminder')
        self.app_qsettings.setValue('overwrite', self.app_settings['reminder']['overwrite'])
        self.app_qsettings.endGroup()

    def on_action_define_location(self):
        location_definer = LocationDefinerDialog(self.system_default_locations, self.corpus.location_definition, self.app_settings, self.app_ctx, parent=self)
        location_definer.saved_locations.connect(self.save_new_locations)
        location_definer.exec_()

    def save_new_locations(self, new_locations):
        # TODO: need to reimplement this once corpus class is there
        self.corpus.location_definition = new_locations
        self.parameter_scroll.clear(self.corpus.location_definition, self.app_ctx)

    def update_status_bar(self, text):
        self.status_bar.showMessage(text)

    def update_hand_illustration(self, num):
        hand_img = QPixmap(self.app_ctx.hand_illustrations['slot' + str(num)])
        self.illustration_scroll.set_img(hand_img)

    def on_action_edit_preference(self):
        pref_dialog = PreferenceDialog(self.app_settings, parent=self)
        pref_dialog.exec_()
        #self.app_settings

    @check_duplicated_gloss
    @check_unsaved_corpus
    def on_action_save(self, clicked):
        lexical_info = self.lexical_scroll.get_value()
        location_transcription_info = self.parameter_scroll.location_layout.get_location_value()
        global_hand_info = self.transcription_scroll.global_info.get_value()
        configs = [self.transcription_scroll.config1.get_value(),
                   self.transcription_scroll.config2.get_value()]

        # if missing then some of them will be none
        if lexical_info and location_transcription_info and global_hand_info and configs:
            if self.current_sign:
                response = QMessageBox.question(self, 'Overwrite the current sign',
                                                'Do you want to overwrite the existing transcriptions?')
                if response == QMessageBox.Yes:
                    self.corpus.remove_sign(self.current_sign)
                else:
                    return

            new_sign = Sign(lexical_info, global_hand_info, configs, location_transcription_info)
            self.corpus.add_sign(new_sign)
            self.corpus_view.updated_glosses(self.corpus.get_sign_glosses(), new_sign.lexical_information.gloss)
            self.current_sign = new_sign
            self.action_delete_sign.setEnabled(True)

            self.corpus.name = self.corpus_view.corpus_title.text()
            self.save_corpus_binary()

            self.undostack.clear()

    def save_corpus_binary(self):
        with open(self.corpus.path, 'wb') as f:
            pickle.dump(self.corpus, f, protocol=pickle.HIGHEST_PROTOCOL)

    def load_corpus_binary(self, path):
        with open(path, 'rb') as f:
            return pickle.load(f)

    def on_action_copy(self, clicked):
        pass
        # TODO: implement

    def on_action_paste(self, clicked):
        pass
        # TODO: implement

    def on_action_new_corpus(self, clicked):
        self.current_sign = None
        self.action_delete_sign.setEnabled(False)

        self.corpus = Corpus(signs=None, location_definition=deepcopy(SAMPLE_LOCATIONS))

        self.corpus_view.clear()
        self.lexical_scroll.clear(self.app_settings['metadata']['coder'])
        self.transcription_scroll.clear()
        self.parameter_scroll.clear(self.corpus.location_definition, self.app_ctx)

    def on_action_load_corpus(self, clicked):
        file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Open Corpus'), self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLAP-AA Corpus (*.slpaa)'))
        folder, _ = os.path.split(file_name)
        if folder:
            self.app_settings['storage']['recent_folder'] = folder

        self.corpus = self.load_corpus_binary(file_name)

        first = self.corpus.get_sign_glosses()[0]
        self.parameter_scroll.clear(self.corpus.location_definition, self.app_ctx)
        self.corpus_view.updated_glosses(self.corpus.get_sign_glosses(), self.corpus.get_sign_by_gloss(first).lexical_information.gloss)
        self.corpus_view.selected_gloss.emit(self.corpus.get_sign_by_gloss(first).lexical_information.gloss)

        return bool(self.corpus)

    def on_action_close(self, clicked):
        self.close()

    def on_action_new_sign(self, clicked):
        self.current_sign = None
        self.action_delete_sign.setEnabled(False)

        self.lexical_scroll.clear(self.app_settings['metadata']['coder'])
        self.transcription_scroll.clear()
        self.parameter_scroll.clear(self.corpus.location_definition, self.app_ctx)

        self.corpus_view.corpus_view.clearSelection()

    def on_action_delete_sign(self, clicked):
        response = QMessageBox.question(self, 'Delete the selected sign',
                                        'Do you want to delete the selected sign?')
        if response == QMessageBox.Yes:
            previous = self.corpus.get_previous_sign(self.current_sign.lexical_information.gloss)

            self.corpus.remove_sign(self.current_sign)
            self.corpus_view.updated_glosses(self.corpus.get_sign_glosses(), previous.lexical_information.gloss)

            self.handle_sign_selected(previous.lexical_information.gloss)

    def on_action_predefined_handshape(self, clicked):
        if self.predefined_handshape_dialog is None:
            focused_hand = self.insert_predefined_buttons()

            self.predefined_handshape_dialog = PredefinedHandshapeDialog(self.app_ctx.predefined, focused_hand, parent=self)
            self.predefined_handshape_dialog.transcription.connect(self.handle_set_predefined)
            self.predefined_handshape_dialog.selected_hand.connect(self.transcription_scroll.change_hand_selection)
            self.predefined_handshape_dialog.rejected.connect(self.handle_predefined_close)

            self.transcription_scroll.selected_hand.connect(self.predefined_handshape_dialog.change_hand_selection)

            self.predefined_handshape_dialog.show()

        else:
            self.predefined_handshape_dialog.raise_()

    def handle_set_predefined(self, transcription_list):
        undo_command = PredefinedUndoCommand(self.transcription_scroll, transcription_list)
        self.undostack.push(undo_command)

    def insert_predefined_buttons(self):
        focused_hands = [
            self.transcription_scroll.config1.hand1.hasFocus(), self.transcription_scroll.config1.hand2.hasFocus(),
            self.transcription_scroll.config2.hand1.hasFocus(), self.transcription_scroll.config2.hand2.hasFocus()
        ]
        if any(focused_hands):
            focused_hand = focused_hands.index(True) + 1
        else:
            focused_hand = 1

        self.transcription_scroll.insert_radio_button(focused_hand)

        return focused_hand

    def handle_predefined_close(self):
        self.transcription_scroll.remove_radio_button()
        self.predefined_handshape_dialog.deleteLater()
        self.predefined_handshape_dialog = None

    @check_unsaved_change
    def closeEvent(self, event):
        self.save_app_settings()
        super().closeEvent(event)
