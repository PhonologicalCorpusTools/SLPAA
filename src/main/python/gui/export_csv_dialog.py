import sys
import os

from PyQt5.QtWidgets import (
    QGraphicsPolygonItem,
    QGraphicsView,
    QGraphicsScene,
    QGraphicsPixmapItem,
    QFrame,
    QGridLayout,
    QLineEdit,
    QPushButton,
    QDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QSlider,
    QApplication,
    QGroupBox,
    QRadioButton
)

from PyQt5.QtGui import (
    QBrush,
    QColor,
    QPen,
    QPolygonF,
    QPixmap,
    QIcon
)

from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRectF,
    QAbstractListModel,
    pyqtSignal
)


class LocationGroup(QGroupBox):
    def __init__(self, app_settings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.app_settings = app_settings

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.path_edit = QLineEdit(parent=self)
        file_open_button = QPushButton('Browse...')
        file_open_button.clicked.connect(self.on_file_open)
        main_layout.addWidget(QLabel('File location', parent=self))
        main_layout.addWidget(self.path_edit)
        main_layout.addWidget(file_open_button)

    def on_file_open(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Export Handshape Transcriptions'),
                                                           os.path.join(
                                                               self.app_settings['storage']['recent_folder'],
                                                               'handshape_transcriptions.csv'),
                                                           self.tr('CSV Files (*.csv)'))

        if file_name:
            self.path_edit.setText(file_name)

    def get_file_path(self):
        return self.path_edit.text()


class TranscriptionOptionGroup(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        self.option1 = QRadioButton('Slots in individual cells')
        self.option1.setChecked(True)
        self.option2 = QRadioButton('Slots in a single cell')

        main_layout.addWidget(self.option1)
        main_layout.addWidget(self.option2)

    def get_selected_option(self):
        return 'individual' if self.option1.isChecked() else 'single'


class ExportCSVDialog(QDialog):
    def __init__(self, app_settings, *args, **kwargs):
        super().__init__(*args, **kwargs)

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.location_group = LocationGroup(app_settings, 'Location', parent=self)
        main_layout.addWidget(self.location_group)

        self.transcription_option_group = TranscriptionOptionGroup('Options', parent=self)
        main_layout.addWidget(self.transcription_option_group)

        separate_line = QFrame()
        separate_line.setFrameShape(QFrame.HLine)
        separate_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(separate_line)

        buttons = QDialogButtonBox.Cancel | QDialogButtonBox.Save
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.on_button_click)

        main_layout.addWidget(self.button_box)

    def on_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Save:
            if not self.location_group.get_file_path():
                QMessageBox.Critical(self, 'File Location Empty', 'File location cannot be empty.')
                return
            self.accept()

        elif standard == QDialogButtonBox.Cancel:
            self.reject()


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = ExportCSVDialog(1)
#     window.show()
#     sys.exit(app.exec_())
