import io
import json

from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QPushButton,
    QLabel,
    QFormLayout,
    QFrame,
    QDialogButtonBox,
    QFileDialog,
    QComboBox
)

from gui.modulespecification_widgets import StatusDisplay


class ExportCorpusDialog(QDialog):

    def __init__(self, app_settings, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.exportfilepath = ""
        self.outputformat = "json"

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.selectformatlabel = QLabel("1. Choose which format you'd like for the exported data: JSON (.txt) is currently the only option.")
        self.selectformatcombo = QComboBox()
        self.selectformatcombo.addItems(["JSON (.txt)"])
        self.selectformatcombo.currentTextChanged.connect(self.formatcombo_changed)
        form_layout.addRow(self.selectformatlabel, self.selectformatcombo)
        self.chooseexportedfilelabel = QLabel("2. Choose the name and location for the exported file.")
        self.chooseexportedfilebutton = QPushButton("Select exported file")
        self.chooseexportedfilebutton.clicked.connect(self.handle_select_exportedfile)
        form_layout.addRow(self.chooseexportedfilelabel, self.chooseexportedfilebutton)
        self.exportcorpuslabel = QLabel("3. Export current .slpaa file.")
        self.exportcorpusbutton = QPushButton("Export corpus")
        self.exportcorpusbutton.setEnabled(False)
        self.exportcorpusbutton.clicked.connect(self.handle_export_corpus)
        form_layout.addRow(self.exportcorpuslabel, self.exportcorpusbutton)
        self.statuslabel = QLabel("4. Status of export:")
        self.statusdisplay = StatusDisplay("not yet attempted")
        form_layout.addRow(self.statuslabel, self.statusdisplay)

        main_layout.addLayout(form_layout)

        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.HLine)
        horizontal_line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(horizontal_line)

        buttons = QDialogButtonBox.Close
        self.button_box = QDialogButtonBox(buttons, parent=self)
        self.button_box.clicked.connect(self.handle_buttonbox_click)
        main_layout.addWidget(self.button_box)

        self.setLayout(main_layout)

    def formatcombo_changed(self, txt):
        if "json" in txt.lower():
            newoutputformat = "json"
        else:
            newoutputformat = "something else"

        if newoutputformat != self.outputformat:
            self.statusdisplay.setText(newoutputformat + " format selected")
        self.outputformat = newoutputformat

    def handle_select_exportedfile(self):
        file_name, file_type = QFileDialog.getSaveFileName(self,
                                                           self.tr('Select export destination'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('JSON file (*.txt)'))
        if file_name != self.exportfilepath:
            self.statusdisplay.setText("destination selected")
        self.exportfilepath = file_name
        if len(self.exportfilepath) > 0 and self.parent().corpus is not None:
            self.exportcorpusbutton.setEnabled(True)

    def handle_export_corpus(self):
        self.statusdisplay.setText("exporting...")
        resultmessage = self.export_corpus()
        self.statusdisplay.setText(resultmessage)

    def export_corpus(self):
        serialized_corpus = self.parent().corpus.serialize()
        with io.open(self.exportfilepath, "w") as exfile:
            # can also specify separators=(item_separator, key_separator)
            # default is (', ', ': ') if indent is None and (',', ': ') otherwise
            try:
                json.dump(serialized_corpus, exfile, indent=3, default=lambda x: getattr(x, '__dict__', str(x)))
            except Exception:
                return "export failed"

        return "export completed"

    def handle_buttonbox_click(self, button):
        standard = self.button_box.standardButton(button)

        if standard == QDialogButtonBox.Close:
            # close dialog
            self.accept()
