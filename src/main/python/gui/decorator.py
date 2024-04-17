import os
import functools
from datetime import date

from PyQt5.QtWidgets import (
    QMessageBox,
    QFileDialog
)


def check_unsaved_change(func):
    @functools.wraps(func)
    def wrapper_check_unsaved_change(self, event, *args, **kwargs):
        if self.corpus is None:  # if called while initializing, just proceed to the main function.
            return func(self, event, *args, **kwargs)

        if self.unsaved_changes:  # if there is any unsaved changes, prompt a warning.
            # Note: if SLPAA decides to use a centralized stack in the future (cf. #114), do the following:
            # (1) remove the Bool 'unsaved_changes' and use the stack, (2) uncomment the conditional below.
            # if not self.undostack.isClean():

            if event:   # called while closing the program
                contextual_msg = 'and close the app'
            else:       # all the other cases
                contextual_msg = 'and proceed'

            warning_box = QMessageBox(QMessageBox.Question,
                                      'Unsaved Changes',
                                      f'Are you sure you want to discard unsaved changes {contextual_msg}?')

            btn_discard = warning_box.addButton(f'Discard {contextual_msg}', QMessageBox.ResetRole)  # 7
            btn_cancel = warning_box.addButton('Cancel', QMessageBox.RejectRole)  # 1
            btn_save = warning_box.addButton(f'Save {contextual_msg}', QMessageBox.AcceptRole)  # 0
            warning_box.exec_()

            if warning_box.clickedButton() == btn_cancel:
                return event.ignore() if event else None
            elif warning_box.clickedButton() == btn_save:
                self.on_action_save(clicked=False)

        func(self, event, *args, **kwargs)
    return wrapper_check_unsaved_change


def check_empty_gloss(func):
    @functools.wraps(func)
    def wrapper_check_empty_gloss(self, *args, **kwargs):
        if not self.gloss_edit.text():
            QMessageBox.critical(self, 'Empty Gloss', 'Gloss cannot be empty.')
            return
        else:
            return func(self, *args, **kwargs)
    return wrapper_check_empty_gloss


def check_duplicated_gloss(func):
    @functools.wraps(func)
    def wrapper_duplicated_gloss(self, *args, **kwargs):
        signlevel_info = self.signlevelinfo_scroll.get_value()
        if signlevel_info is None:
            return
        else:
            if self.current_sign:
                if signlevel_info['gloss'] == \
                        self.current_sign.signlevel_info.gloss or \
                        signlevel_info['gloss'] not in self.corpus.get_sign_glosses():
                    return func(self, *args, **kwargs)

            if signlevel_info['gloss'] in self.corpus.get_sign_glosses():
                QMessageBox.critical(self, 'Duplicated Gloss',
                                     'Please use a different gloss. Duplicated glosses are not allowed.')
                return
            else:
                return func(self, *args, **kwargs)
    return wrapper_duplicated_gloss


def check_unsaved_corpus(func):
    # This decorator is a fail-safe that is activated when saving a (new) corpus for the first time.
    # I.e., check_(if we are dealing with an)_unsaved_corpus.
    # For example, it is active if the user creates a corpus from scratch and then saves it with the 'save' button.
    @functools.wraps(func)
    def wrapper_check_unsaved_corpus(self, *args, **kwargs):
        # if self.corpus is None:
        #     return func(self, *args, **kwargs)

        if self.corpus.path is None:
            file_name, _ = QFileDialog.getSaveFileName(self,
                                                       self.tr('Save Corpus'),
                                                       os.path.join(self.app_settings['storage']['recent_folder'], '.slpaa'),
                                                       self.tr('SLP-AA Corpus (*.slpaa)'))
            if file_name:
                self.corpus.path = file_name
                folder, _ = os.path.split(file_name)
                if folder:
                    self.app_settings['storage']['recent_folder'] = folder
        return func(self, *args, **kwargs)

    return wrapper_check_unsaved_corpus
