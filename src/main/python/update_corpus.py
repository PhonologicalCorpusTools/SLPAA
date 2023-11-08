import logging
import errno
import sys
from os import getcwd
from os.path import join, exists, realpath, dirname
from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property

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

from gui.main_window import MainWindow
from lexicon.lexicon_classes import Corpus
from serialization_classes import renamed_load



class AppContext(ApplicationContext):
    def __init__(self):
        super().__init__()
        
    def run(self):
        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)

class MainWindow(QMainWindow):
    def __init__(self, app_ctx):
        super().__init__()
        self.app_ctx = app_ctx
        self.handle_app_settings()
        self.load_corpus()
    
    def handle_app_settings(self):
        self.app_settings = defaultdict(dict)

        self.app_qsettings = QSettings('UBC Phonology Tools',
                                       application='Corpus conversion tool')

        self.app_qsettings.beginGroup('storage')
        self.app_settings['storage']['recent_folder'] = self.app_qsettings.value(
            'recent_folder',
            defaultValue=os.path.expanduser('~/Documents'))


    def load_corpus(self):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           self.tr('Open Corpus'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA Corpus (*.slpaa)'))
        if not file_name:
            # the user cancelled out of the dialog
            return False
        folder, _ = os.path.split(file_name)
        if folder:
            self.app_settings['recent_folder'] = folder

        self.corpus = self.load_corpus_binary(file_name)
        # print(self.corpus.get_sign_glosses())
        for gloss in self.corpus.get_sign_glosses():
            sign = self.corpus.get_sign_by_gloss(gloss)
            logging.warning(sign)
            logging.warning(sign.getmoduledict("MOVEMENT"))

        self.unsaved_changes = False

        return self.corpus is not None  # bool(Corpus)

    def load_corpus_binary(self, path):
        with open(path, 'rb') as f:
            # corpus = Corpus(serializedcorpus=pickle.load(f))
            corpus = Corpus(serializedcorpus=renamed_load(f))
            # in case we're loading a corpus that was originally created on a different machine / in a different folder
            corpus.path = path
            return corpus

appctxt = AppContext()
exit_code = appctxt.run()
sys.exit(exit_code)