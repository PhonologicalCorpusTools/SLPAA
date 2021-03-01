from PyQt5.QtCore import (
    Qt,
    QSize,
    pyqtSlot,
    QPoint,
    QAbstractTableModel,
    pyqtSignal,
    QMimeData
)
from PyQt5.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QDialog,
    QDialogButtonBox,
    QMessageBox,
    QTableView,
    QAction,
    QAbstractItemView,
    QMenu,
    QFrame,
    QRadioButton,
    QGroupBox,
    QPlainTextEdit
)
from PyQt5.QtGui import (
    QIcon,
    QPixmap,
    QColor,
    QDrag,
    QImage
)


class NoteBox(QGroupBox):
    def __init__(self, title, corpus_note, *args, **kwargs):
        super().__init__(title, *args, **kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.note = QPlainTextEdit(corpus_note, parent=self)
        self.note.setPlaceholderText('Enter corpus notes here...')
        main_layout.addWidget(self.note)

    def get_note(self):
        return self.note.toPlainText()


class CorpusSummaryDialog(QDialog):
    updated_note = pyqtSignal(str)

    def __init__(self, corpus_note, **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.note_groupbox = NoteBox('Corpus notes', corpus_note, parent=self)
        main_layout.addWidget(self.note_groupbox)

        buttons = QDialogButtonBox.Save | QDialogButtonBox.Close
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.handle_button_click)

        main_layout.addWidget(self.button_box)

    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Close:
            response = QMessageBox.question(self, 'Warning',
                                            'If you close the window, any unsaved changes will be lost. Continue?')
            if response == QMessageBox.Yes:
                self.accept()

        elif standard == QDialogButtonBox.Save:
            self.updated_note.emit(self.note_groupbox.get_note())
            QMessageBox.information(self, 'Note Saved', 'Corpus note updated!')
