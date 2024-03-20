from PyQt5.QtWidgets import (
    QVBoxLayout,
    QDialog,
    QWidget,
    QPushButton,
    QLabel,
    QComboBox,
    QMdiArea,
    QMdiSubWindow,
    QFormLayout,
    QFrame,
    QDialogButtonBox,
    QFileDialog,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QScrollArea,
    QButtonGroup,
    QLineEdit,
    QMessageBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QTableView,
    QHeaderView,
    QSizePolicy,
    QMainWindow,
    QItemDelegate,
    QStyledItemDelegate,
    QAction,
    QTabWidget
)
from PyQt5.Qt import (
    QStandardItem,
    QStandardItemModel, 
    QMessageBox,
    QLabel,
    QVBoxLayout,
    QDialog
)
import logging

class ResultHeaders:
    CORPUS = 0
    NAME = 1
    TYPE = 2
    ID = 3
    GLOSS = 4

class ResultsView(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        logging.warning("initiating results")
        self.setWindowTitle("Search Results")
        

        # Create a tab widget
        main_layout = QVBoxLayout()
        self.tab_widget = QTabWidget()
        
        self.summarytab = QWidget()
        self.summary_table_view = QTableView(parent=self)
        self.summary_table_view.setModel(ResultSummaryModel())
        summarylayout = QVBoxLayout()
        summarylayout.addWidget(self.summary_table_view)
        self.summarytab.setLayout(summarylayout)
        
        self.individualtab = QWidget()
        individuallayout = QVBoxLayout()
        self.individual_table_view = QTableView(parent=self)
        self.individual_table_view.setModel(IndividualSummaryModel())
        individuallayout.addWidget(self.individual_table_view)
        self.individualtab.setLayout(individuallayout)

        self.tab_widget.addTab(self.summarytab, "Summary")
        self.tab_widget.addTab(self.individualtab, "Individual results")

        self.showMaximized()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)



class ResultSummaryModel(QStandardItemModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.headers = ["Corpus", "Target Name(s)", "Result Type(s)", "Frequency"]
        self.setHorizontalHeaderLabels(self.headers)


class IndividualSummaryModel(QStandardItemModel):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.headers = ["Corpus", "Target Name(s)", "Result Type(s)", "Entry ID", "Gloss"]
        self.setHorizontalHeaderLabels(self.headers)