import os
import pickle
from collections import defaultdict
from getpass import getuser
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
        self.system_default_locations = SAMPLE_LOCATIONS

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
        self.action_show_sub_corpus.setChecked(True)

        # show/hide lexical subwindow
        self.action_show_sub_lexical = QAction('Show lexical information', parent=self)
        self.action_show_sub_lexical.setStatusTip('Show/hide lexical information')
        self.action_show_sub_lexical.triggered.connect(self.on_action_show_sub_lexical)
        self.action_show_sub_lexical.setCheckable(True)
        self.action_show_sub_lexical.setChecked(True)

        # show/hide transcription subwindow
        self.action_show_sub_transcription = QAction('Show transcription', parent=self)
        self.action_show_sub_transcription.setStatusTip('Show/hide transcription')
        self.action_show_sub_transcription.triggered.connect(self.on_action_show_sub_transcription)
        self.action_show_sub_transcription.setCheckable(True)
        self.action_show_sub_transcription.setChecked(True)

        # show/hide illustration subwindow
        self.action_show_sub_illustration = QAction('Show hand illustration', parent=self)
        self.action_show_sub_illustration.setStatusTip('Show/hide hand illustration')
        self.action_show_sub_illustration.triggered.connect(self.on_action_show_sub_illustration)
        self.action_show_sub_illustration.setCheckable(True)
        self.action_show_sub_illustration.setChecked(True)

        # show/hide parameter subwindow
        self.action_show_sub_parameter = QAction('Show parameter specifier', parent=self)
        self.action_show_sub_parameter.setStatusTip('Show/hide parameter specifier')
        self.action_show_sub_parameter.triggered.connect(self.on_action_show_sub_parameter)
        self.action_show_sub_parameter.setCheckable(True)
        self.action_show_sub_parameter.setChecked(True)

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
        menu_file.addAction(action_close)
        menu_file.addAction(action_save)
        menu_file.addSeparator()
        menu_file.addAction(action_new_sign)
        menu_file.addAction(self.action_delete_sign)

        menu_edit = main_menu.addMenu('&Edit')
        menu_edit.addAction(action_copy)
        menu_edit.addAction(action_paste)

        menu_edit = main_menu.addMenu('&View')
        menu_edit.addAction(self.action_show_sub_corpus)
        menu_edit.addAction(self.action_show_sub_lexical)
        menu_edit.addAction(self.action_show_sub_transcription)
        menu_edit.addAction(self.action_show_sub_illustration)
        menu_edit.addAction(self.action_show_sub_parameter)

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

        self.main_mdi.tileSubWindows()
        self.setCentralWidget(self.main_mdi)

        self.open_initialization_window()

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
        self.app_settings['display']['size'] = self.app_qsettings.value('size', defaultValue=QSize(1200, 1000))
        self.app_settings['display']['position'] = self.app_qsettings.value('position', defaultValue=QPoint(50, 50))
        self.app_settings['display']['sig_figs'] = self.app_qsettings.value('sig_figs', defaultValue=2)
        self.app_settings['display']['tooltips'] = self.app_qsettings.value('tooltips', defaultValue=True)
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('metadata')
        self.app_settings['metadata']['coder'] = self.app_qsettings.value('coder', defaultValue=getuser())
        self.app_qsettings.endGroup()

        self.app_qsettings.beginGroup('reminder')
        self.app_settings['reminder']['overwrite'] = self.app_qsettings.value('overwrite', defaultValue=True)
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
        self.app_qsettings.setValue('size', self.size())
        self.app_qsettings.setValue('position', self.pos())
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
        location_definer = LocationDefinerDialog(self.corpus.location_definition, self.app_settings, self.app_ctx, parent=self)
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

        self.corpus = Corpus(signs=None, location_definition=SAMPLE_LOCATIONS)

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
            self.predefined_handshape_dialog = PredefinedHandshapeDialog(self.app_ctx.predefined, parent=self)
            self.predefined_handshape_dialog.transcription.connect(self.handle_set_predefined)
            self.predefined_handshape_dialog.rejected.connect(self.handle_predefined_close)
            self.predefined_handshape_dialog.show()

            self.insert_predefined_buttons()
        else:
            self.predefined_handshape_dialog.raise_()

    def handle_set_predefined(self, transcription_list):
        undo_command = PredefinedUndoCommand(self.transcription_scroll, transcription_list)
        self.undostack.push(undo_command)

    def insert_predefined_buttons(self):
        self.transcription_scroll.insert_radio_button()

    def handle_predefined_close(self):
        self.transcription_scroll.remove_radio_button()
        self.predefined_handshape_dialog.deleteLater()
        self.predefined_handshape_dialog = None

    @check_unsaved_change
    def closeEvent(self, event):
        self.save_app_settings()
        super().closeEvent(event)
