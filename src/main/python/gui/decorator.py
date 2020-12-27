import functools
from datetime import date
from PyQt5.QtWidgets import (
    QMessageBox
)


def check_unsaved_change(func):
    @functools.wraps(func)
    def wrapper_check_unsaved_change(self, event, *args, **kwargs):
        if self.unsaved_changes:
            response = QMessageBox.question(self, 'Unsaved Changes', 'You have unsaved changes')
            if response == QMessageBox.No:
                return event.ignore()
        func(self, event, *args, **kwargs)
    return wrapper_check_unsaved_change


def check_date_format(func):
    @functools.wraps(func)
    def wrapper_check_date_format(self, *args, **kwargs):
        if len(self.update_edit.text().split(sep='-')) != 3:
            QMessageBox.critical(self, 'Date Format Error',
                                 'Please make sure your date follows the format of YYYY-MM-DD.')
            return
        try:
            year, month, day = self.update_edit.text().split(sep='-')
            date(int(year), int(month), int(day))
        except ValueError as error:
            QMessageBox.critical(self, 'Date Format Error', str(error))
            return
        else:
            return func(self, *args, **kwargs)
    return wrapper_check_date_format


def check_empty_gloss(func):
    @functools.wraps(func)
    def wrapper_check_empty_gloss(self, *args, **kwargs):
        if not self.gloss_edit.text():
            QMessageBox.critical(self, 'Empty Gloss', 'Gloss cannot be empty.')
            return
        else:
            return func(self, *args, **kwargs)
    return wrapper_check_empty_gloss
