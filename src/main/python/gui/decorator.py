import os
import functools
from datetime import date

from PyQt5.QtWidgets import (
    QMessageBox,
    QFileDialog
)

from lexicon.module_classes import EntryID


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


def check_empty_glosslemmaIDgloss(func):
    @functools.wraps(func)
    def wrapper_check_empty_glosslemmaIDgloss(self, *args, **kwargs):
        if len(self.glosses_model.glosses()) == 0 and self.lemma_edit.text() == "" and self.idgloss_edit.text() == "":
            QMessageBox.critical(self, 'No identifiers', 'All of gloss, lemma, and ID-gloss are empty; please enter a value for at least one of these fields.')
            return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return wrapper_check_empty_glosslemmaIDgloss


def check_duplicated_idgloss(func):
    @functools.wraps(func)
    def wrapper_check_duplicated_idgloss(self, *args, **kwargs):
        thisidgloss_lower = self.get_idgloss().lower().strip()
        idglossesincorpus_lower = [idgloss.lower().strip() for idgloss in self.mainwindow.corpus.get_all_idglosses()]

        if not thisidgloss_lower:
            return func(self, *args, **kwargs)
        elif thisidgloss_lower not in idglossesincorpus_lower:
            return func(self, *args, **kwargs)
        elif self.mainwindow.current_sign and self.mainwindow.current_sign.signlevel_information.idgloss.lower().strip() == thisidgloss_lower:
            return func(self, *args, **kwargs)
        else:
            othersignswiththisidgloss = [sign for sign in self.mainwindow.corpus.signs
                                         if thisidgloss_lower == sign.signlevel_information.idgloss.lower().strip()
                                         and sign != self.mainwindow.current_sign]
            messagetext = "This ID-gloss is also used by the sign(s) listed below:"
            for sign in othersignswiththisidgloss:
                glosseslist = sign.signlevel_information.gloss
                messagetext += "\n - gloss" + \
                               ("es" if len(glosseslist) > 1 else "") + \
                               " " + \
                               ", ".join(glosseslist)
                if sign.signlevel_information.entryid.display_string() != EntryID.nodisplay:
                    messagetext += " / Entry ID " + sign.signlevel_information.entryid.display_string()
            messagetext += "\n\nDuplicates are not allowed; please use a different ID-gloss."
            QMessageBox.critical(self, "Duplicated ID-gloss", messagetext)
            return
    return wrapper_check_duplicated_idgloss


def check_duplicated_lemma(func):
    @functools.wraps(func)
    def wrapper_check_duplicated_lemma(self, *args, **kwargs):
        if not self.settings['reminder']['duplicatelemma']:
            # user doesn't want to see warnings for duplicate lemmas
            return func(self, *args, **kwargs)

        thislemma_lower = self.get_lemma().lower().strip()
        lemmasincorpus_lower = [lemma.lower().strip() for lemma in self.mainwindow.corpus.get_all_lemmas()]

        if not thislemma_lower:
            return func(self, *args, **kwargs)
        elif thislemma_lower not in lemmasincorpus_lower:
            return func(self, *args, **kwargs)
        elif self.mainwindow.current_sign and self.mainwindow.current_sign.signlevel_information.lemma.lower().strip() == thislemma_lower:
            return func(self, *args, **kwargs)
        else:
            othersignswiththislemma = [sign for sign in self.mainwindow.corpus.signs
                                       if thislemma_lower == sign.signlevel_information.lemma.lower().strip()
                                       and sign != self.mainwindow.current_sign]
            messagetext = "This lemma is also used by the sign(s) listed below:"
            for sign in othersignswiththislemma:
                glosseslist = sign.signlevel_information.gloss
                messagetext += "\n - gloss" + \
                               ("es" if len(glosseslist) > 1 else "") + \
                               " " + \
                               ", ".join(glosseslist)
                if sign.signlevel_information.entryid.display_string() != EntryID.nodisplay:
                    messagetext += " / Entry ID " + sign.signlevel_information.entryid.display_string()
            messagetext += "\n\nDo you want to save the lemma as is, or cancel and enter a different one?"
            result = QMessageBox.warning(self,
                                         "Duplicated Lemma",
                                         messagetext,
                                         QMessageBox.Save | QMessageBox.Cancel,
                                         QMessageBox.Save)
            if result == QMessageBox.Save:
                return func(self, *args, **kwargs)
            else:
                return
    return wrapper_check_duplicated_lemma


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

def check_unsaved_search_targets(func):
    ''' This decorator is a fail-safe that is activated when saving a (new) search targets file for the first time.
    I.e., check (if we are dealing with an) unsaved search targets file.
    For example, it is active if the user creates a search targets file from scratch and then saves it with the 'save' button.'''
    @functools.wraps(func)
    def wrapper_check_unsaved_search_targets(self, **kwargs):
        if self.searchmodel.path is None:
            name = self.searchmodel.name or "New search"
            file_name, _ = QFileDialog.getSaveFileName(self,
                                                    self.tr('Save Targets'),
                                                    os.path.join(self.app_settings['storage']['recent_folder'],
                                                                    name + '.slpst'),  # 'corpus.slpaa'),
                                                    self.tr('SLP-AA Search Targets (*.slpst)'))
            if file_name:
                self.searchmodel.path = file_name
                folder, _ = os.path.split(file_name)
                if folder:
                    self.app_settings['storage']['recent_folder'] = folder
        return func(self, **kwargs)

    return wrapper_check_unsaved_search_targets
