import io

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
    QStyledItemDelegate
)
from gui.xslotspecification_view import XslotSelectorDialog, XslotStructure
from constant import XSLOT_TARGET, SIGNLEVELINFO_TARGET, SIGNTYPEINFO_TARGET, HAND, ARM, LEG
import copy 
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
# from lexicon.lexicon_classes import Sign
from gui.panel import SignLevelMenuPanel
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes
from search.search_models import SearchModel, SearchTargetItem, TargetHeaders, ResultsModel
from gui.signlevelinfospecification_view import SignlevelinfoSelectorDialog
from search.search_classes import Search_SignLevelInfoSelectorDialog, Search_ModuleSelectorDialog

class SearchWindow(QMainWindow):

    def __init__(self, app_settings, corpus=None, **kwargs):
        super().__init__(**kwargs)
        self.searchmodel = SearchModel()
        self.corpus = corpus
        self.app_settings = app_settings
        self.current_sign = SearchWindowSign()

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        self.setWindowTitle("Search")

        # Set up the layout
        self.mdi_area = QMdiArea(main_widget)
        self.init_ui()
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.mdi_area)

    def init_ui(self):

        self.search_targets_view = SearchTargetsView(self.searchmodel, parent=self)
        self.search_params_view = SearchParamsView(parent=self)
        self.search_params_view.search_clicked.connect(self.handle_search_clicked)
        self.build_search_target_view = BuildSearchTargetView(sign=None, mainwindow=self, parent=self)
        self.build_search_target_view.target_added.connect(self.handle_new_search_target_added)

        search_param_window = QMdiSubWindow()
        search_param_window.setWidget(self.search_params_view)
        search_param_window.setWindowTitle("Search Parameters")

        build_search_window = QMdiSubWindow()
        build_search_window.setWidget(self.build_search_target_view)
        build_search_window.setWindowTitle("Build Search Target")

        search_targets_window = QMdiSubWindow()
        search_targets_window.setWidget(self.search_targets_view)
        search_targets_window.setWindowTitle("Search Targets")

        for w in [search_param_window, build_search_window, search_targets_window]:
            self.mdi_area.addSubWindow(w)    

        self.mdi_area.tileSubWindows()
        self.showMaximized()
        # TODO Fix this
        # w = self.mdi_area.width()
        # h = self.mdi_area.height()
        # search_targets_window.setGeometry(0, 0, int(2*w/3), h)
        # build_search_window.setGeometry(int(2*w/3), 0, int(1*w/3), int(1/2*h))
        # search_param_window.setGeometry(int(2*w/3), int(1/2*h), int(1*w/3), int(1/2*h))
        
    def handle_search_clicked(self, type):
        
        mssg = ""
        if self.search_params_view.match_type is None: 
            mssg += "Missing match type."
        if len(self.searchmodel.targets) > 0 and self.search_params_view.match_degree is None:
            mssg += "\nMissing multiple target match type."
        
        if mssg != "":
            QMessageBox.critical(self, "Warning", mssg)
        else:
            self.searchmodel.searchtype = type
            self.searchmodel.matchtype = self.search_params_view.match_type
            self.searchmodel.matchdegree = self.search_params_view.match_degree

            QMessageBox.critical(self, "Search", "a beautiful search occured")
            
            # self.results_view = ResultsView(self.searchmodel, self.corpus)
            # self.results_view.show()

    def handle_match_type_changed(self, type):
        self.search_params_view.match_type = type

    def handle_match_degree_changed(self, degree):
        self.search_params_view.match_type = degree

    def handle_new_search_target_added(self, target):
        self.searchmodel.add_target(target)
            
class SearchTargetsView(QWidget):
    def __init__(self, searchmodel, **kwargs):
        super().__init__(**kwargs)
        self.model = searchmodel

        self.table_view = QTableView(parent=self)
        self.table_view.setModel(self.model)
        self.set_table_ui()

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)
    
    def set_table_ui(self):
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.table_view.setStyleSheet("QTableView {alignment: AlignCenter;}")
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.table_view.setItemDelegateForColumn(2, ListDelegate()) # The "values" column contains lists

class ListDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
    def displayText(self, value, locale):
        if isinstance(value, list):
            display_text = '; '.join(value) # TODO prefer multiline...
            return display_text
        return super().displayText(value, locale)

        
class BuildSearchTargetView(SignLevelMenuPanel): 
    target_added = pyqtSignal(SearchTargetItem)

    def __init__(self, sign, mainwindow, **kwargs):
        super().__init__(sign, mainwindow, **kwargs)
        
    def enable_module_buttons(self, yesorno):
        for btn in self.modulebuttons_untimed + self.modulebuttons_timed:
            btn.setEnabled(True)
        self.signtype_button.setEnabled(True)
        self.xslots_button.setEnabled(True)

    def handle_xslotsbutton_click(self):
        timing_selector = XSlotTargetDialog(parent=self)
        timing_selector.target_saved.connect(self.handle_save_xslottarget)
        timing_selector.exec_()

    def handle_save_xslottarget(self, target_name, max_xslots, min_xslots):
        target = SearchTargetItem()
        target.targettype = XSLOT_TARGET
        target.name = target_name
        if min_xslots != "":
            target.dict["xslot min"] = min_xslots
        if max_xslots != "":
            target.dict["xslot max"] = max_xslots
        
        self.target_added.emit(target)

    def handle_signlevelbutton_click(self):
        initialdialog = NameDialog(parent=self)
        initialdialog.continue_clicked.connect(lambda name: self.show_next_dialog(SIGNLEVELINFO_TARGET, name))
        initialdialog.exec_()

    def handle_menumodulebtn_clicked(self, moduletype):
        initialdialog = XSlotTypeDialog(parent=self)
        initialdialog.continue_clicked.connect(lambda name, xslottype, xslotnum: self.show_next_dialog(moduletype, name, xslottype, xslotnum))
        initialdialog.exec_()

    def show_next_dialog(self, targettype, name, xslottype=None, num=None):
        target = SearchTargetItem()
        target.targettype = targettype
        target.name = name
        target.xslottype = xslottype
        target.xslotnum = num

        if targettype==SIGNLEVELINFO_TARGET:
            signlevelinfo_selector = Search_SignLevelInfoSelectorDialog(None, parent=self)
            signlevelinfo_selector.saved_signlevelinfo.connect(lambda signlevelinfo: self.handle_save_signlevelinfo(target, signlevelinfo))
            signlevelinfo_selector.exec_()
        
        if targettype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION, ModuleTypes.HANDCONFIG]:
            includearticulators = [HAND, ARM, LEG] if targettype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION] \
            else ([] if targettype == ModuleTypes.RELATION else [HAND])
            includephase = 2 if targettype == ModuleTypes.MOVEMENT else (
                1 if targettype == ModuleTypes.LOCATION else
                0  # default
            )
            module_selector = Search_ModuleSelectorDialog(moduletype=targettype,
                                                xslotstructure=None,
                                                moduletoload=None,
                                                includephase=includephase,
                                                incl_articulators=includearticulators,
                                                incl_articulator_subopts=includephase,
                                                parent=self)
            module_selector.module_saved.connect(lambda moduletosave, savedtype: self.handle_save_module(moduletosave, moduletype=savedtype))
            module_selector.exec_()


    def handle_save_signlevelinfo(self, target, signlevel_info):
        target.dict["entryid"] = signlevel_info.entryid
        target.dict["gloss"] = signlevel_info.gloss
        target.dict["lemma"] = signlevel_info.lemma
        target.dict["source"] = signlevel_info.source
        target.dict["signer"] = signlevel_info.signer
        target.dict["frequency"] = signlevel_info.frequency
        target.dict["coder"] = signlevel_info.coder
        target.dict["date created"] = signlevel_info.datecreated
        target.dict["date last modified"] = signlevel_info.datelastmodified
        target.dict["note"] = signlevel_info.note
        # backward compatibility for attribute added 20230412!
        target.dict["fingerspelled"] = signlevel_info.fingerspelled
        target.dict["compoundsign"] = signlevel_info.compoundsign
        target.dict["handdominance"] = signlevel_info.handdominance
       

        self.target_added.emit(target)


class NameWidget(QWidget):
    on_name_entered = pyqtSignal()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = None

        layout = QVBoxLayout()
        label = QLabel("Name of search target")
        self.text_entry = QLineEdit()
        self.text_entry.textEdited.connect(self.on_name_edited)

        layout.addWidget(label)
        layout.addWidget(self.text_entry)
        self.setLayout(layout)

    def on_name_edited(self):
        self.name = self.text_entry.text()
        self.on_name_entered.emit()


class NameDialog(QDialog):
    continue_clicked = pyqtSignal(str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name_widget = NameWidget(parent=self)
        self.name_widget.on_name_entered.connect(self.toggle_continue_selectable)
        layout = QVBoxLayout()
        layout.addWidget(self.name_widget)
        self.buttonbox = InitialButtonBox(parent=self)
        self.buttonbox.continue_clicked.connect(self.on_continue_clicked)
        self.buttonbox.restore_defaults_clicked.connect(self.on_restore_defaults_clicked)
        layout.addWidget(self.buttonbox)

        self.setLayout(layout)
    
    def toggle_continue_selectable(self):
        self.buttonbox.save_button.setEnabled(self.name_widget.name != "")


    def on_continue_clicked(self):
        self.continue_clicked.emit(self.name_widget.name)
        self.accept()
    
    def on_restore_defaults_clicked(self):
        self.name_widget.text_entry.setText("")
        self.buttonbox.save_button.setEnabled(False)

class XSlotTypeDialog(QDialog): # TODO maybe subclass the namedialog
    continue_clicked = pyqtSignal(str, str, str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.name_widget = NameWidget(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.name_widget)
        self.name_widget.on_name_entered.connect(self.toggle_continue_selectable)

        self.xslot_type = None

        self.xslot_type_button_group = QButtonGroup()
        self.ignore_xslots_rb = QRadioButton('Ignore x-slots')
        self.abstract_xslot_rb = QRadioButton('Use an abstract x-slot') 
        self.abstract_whole_sign_rb = QRadioButton('Use an abstract whole sign') 
        self.concrete_xslots_rb = QRadioButton('Use concrete x-slots') 
        self.concrete_xslots_num = QLineEdit()
        self.concrete_xslots_num.setPlaceholderText("Specify number")
        self.concrete_xslots_num.textEdited.connect(self.on_xslots_num_edited)

        self.xslot_type_button_group.addButton(self.ignore_xslots_rb) 
        self.xslot_type_button_group.addButton(self.abstract_xslot_rb) 
        self.xslot_type_button_group.addButton(self.abstract_whole_sign_rb) 
        self.xslot_type_button_group.addButton(self.concrete_xslots_rb)
        self.xslot_type_button_group.buttonToggled.connect(self.on_xslot_type_clicked)

        layout.addWidget(self.ignore_xslots_rb)
        layout.addWidget(self.abstract_xslot_rb)
        layout.addWidget(self.abstract_whole_sign_rb)

        concrete_xslots_layout = QHBoxLayout()
        concrete_xslots_layout.addWidget(self.concrete_xslots_rb)
        concrete_xslots_layout.addWidget(self.concrete_xslots_num)

        layout.addLayout(concrete_xslots_layout)

        self.buttonbox = InitialButtonBox(parent=self)
        self.buttonbox.save_button.setEnabled(False)
        self.buttonbox.continue_clicked.connect(self.on_continue_clicked)
        self.buttonbox.restore_defaults_clicked.connect(self.on_restore_defaults_clicked)
        layout.addWidget(self.buttonbox)

        self.setLayout(layout)
    
    def toggle_continue_selectable(self):
        self.buttonbox.save_button.setEnabled(self.name_widget.name != ""  
            and (self.concrete_xslots_num.text() != "" and self.concrete_xslots_rb.isChecked()
            or (self.xslot_type_button_group.checkedButton() and not self.concrete_xslots_rb.isChecked())))
        
    def on_xslots_num_edited(self):
        self.concrete_xslots_rb.setChecked(True)
        self.toggle_continue_selectable()

    def on_xslot_type_clicked(self, btn):
        self.xslot_type = btn   
        self.concrete_xslots_num.setEnabled(btn == self.concrete_xslots_rb)
        self.toggle_continue_selectable()

    def on_continue_clicked(self):
        txt = ""
        
        if (self.xslot_type == self.concrete_xslots_rb and self.concrete_xslots_num.text() == ""):
            txt = "Specify an x-slot number."
        
        if txt:
            QMessageBox.critical(self, "Warning", txt)
        else:
            if self.xslot_type == self.ignore_xslots_rb:
                type = "ignore"
            elif self.xslot_type == self.abstract_xslot_rb:
                type = "abstract xslot"
            elif self.xslot_type == self.abstract_whole_sign_rb:
                type = "abstract whole sign"
            else:
                type = "concrete"
            
            self.continue_clicked.emit(self.name_widget.name, type, self.concrete_xslots_num.text())
            self.accept()
    
    def on_restore_defaults_clicked(self):
        for b in self.buttonbox.buttons():
            b.setEnabled(False)   
        for b in self.xslot_type_button_group.buttons():
            b.setChecked(False)
        self.concrete_xslots_num.setText("")
        self.name_widget.text_entry.setText("")

class XSlotTargetDialog(QDialog):
    target_saved = pyqtSignal(str, str, str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout()
        self.name_widget = NameWidget(parent=self)
        layout.addWidget(self.name_widget)
        self.name_widget.on_name_entered.connect(self.toggle_continue_selectable)

        self.min_xslots_cb = QCheckBox('Minimum number of x_slots:')
        self.max_xslots_cb = QCheckBox('Maximum number of x_slots:') 
        self.max_num = QLineEdit()
        self.min_num = QLineEdit()
        self.max_num.textEdited.connect(self.on_xslottarget_max_edited)
        self.min_num.textEdited.connect(self.on_xslottarget_min_edited)

        for button in [self.min_xslots_cb, self.max_xslots_cb]:
            button.setEnabled(False) # to make life easier, the user can only modify the number

        min_layout = QHBoxLayout()
        min_layout.addWidget(self.min_xslots_cb)
        min_layout.addWidget(self.min_num)

        max_layout = QHBoxLayout()
        max_layout.addWidget(self.max_xslots_cb)
        max_layout.addWidget(self.max_num)

        layout.addWidget(QLabel("Number of x-slots in search results:"))
        layout.addLayout(min_layout)
        layout.addLayout(max_layout)

        self.buttonbox = SaveTargetButtonBox(parent=self)
        self.buttonbox.save_clicked.connect(self.on_save_clicked)
        self.buttonbox.restore_defaults_clicked.connect(self.on_restore_defaults_clicked)
        layout.addWidget(self.buttonbox)

        self.setLayout(layout)
    
    def toggle_continue_selectable(self):
        self.buttonbox.save_button.setEnabled(self.name_widget.name != "" and 
                                              (self.max_num.text() != "" or self.min_num.text() != ""))
    
    # TODO combine into one function?
    def on_xslottarget_max_edited(self):
        num = self.max_num.text()
        self.max_xslots_cb.setEnabled(num != "")
        self.max_xslots_cb.setChecked(num != "")
        self.toggle_continue_selectable()

    def on_xslottarget_min_edited(self):
        num = self.min_num.text()
        self.min_xslots_cb.setEnabled(num != "")
        self.min_xslots_cb.setChecked(num != "")
        self.toggle_continue_selectable()

    def on_save_clicked(self):
        max = self.max_num.text() if self.max_xslots_cb.isChecked() else ""
        min = self.min_num.text() if self.min_xslots_cb.isChecked() else ""
        txt = ""
        
        if (max == "" and min == ""):
            txt = "Please select at least one of [max, min]."
        elif not ((max.isdigit() or max == "") and (min.isdigit() or min == "")):
            txt = "\nMax and min specifications must be positive integers."
        elif (max != "" and min != "" and int(max) < int(min)):
            txt = "\n Max must be greater than min."
        
        if txt:
            QMessageBox.critical(self, "Warning", txt)
        else:
            self.target_saved.emit(self.name_widget.name, max, min)
            self.accept()

    def on_restore_defaults_clicked(self):
        self.buttonbox.save_button.setEnabled(False)
        for b in [self.min_xslots_cb, self.max_xslots_cb]:
            b.setChecked(False)
            b.setEnabled(False)
        self.min_xslots_cb.setChecked(False)
        self.min_xslots_cb.setChecked(False)
        self.max_num.setText("")
        self.min_num.setText("")
        self.name_widget.text_entry.setText("")

class SearchParamsView(QFrame):
    search_clicked = pyqtSignal(str)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.match_type = None
        self.match_degree = None

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = QVBoxLayout()
        main_frame.setLayout(main_layout)

        main_layout.addLayout(self.create_search_params_layout())
        main_layout.addLayout(self.create_search_button_layout())

    def create_search_button_layout(self):
        layout = QHBoxLayout()

        self.search_button_group = QButtonGroup()
        self.new_search_pb = QPushButton('SEARCH\n(Start new results table)')
        self.add_search_pb = QPushButton('SEARCH\n(Add to current results table)') 
        self.add_search_pb.setObjectName("add")
        self.new_search_pb.setObjectName("new")
        self.search_button_group.addButton(self.new_search_pb)
        self.search_button_group.addButton(self.add_search_pb)
        self.search_button_group.buttonClicked.connect(self.on_search_button_clicked)

        layout.addWidget(self.new_search_pb)
        layout.addWidget(self.add_search_pb)
        return layout

    def create_search_params_layout(self):
        layout = QVBoxLayout()

        self.match_type_button_group = QButtonGroup()
        self.exact_match_rb = QRadioButton("Exact match")
        self.minimal_match_rb = QRadioButton("Minimal match")
        self.exact_match_rb.setObjectName("exact")
        self.minimal_match_rb.setObjectName("minimal")
        self.match_type_button_group.addButton(self.exact_match_rb)
        self.match_type_button_group.addButton(self.minimal_match_rb)
        self.match_type_button_group.buttonClicked.connect(self.on_match_type_button_clicked)

        self.match_degree_button_group = QButtonGroup()
        self.match_any_rb = QRadioButton("Return signs that match any selected targets")
        self.match_all_rb = QRadioButton("Return signs that match all selected targets")
        self.match_any_rb.setObjectName("any")
        self.match_all_rb.setObjectName("all")
        self.match_degree_button_group.addButton(self.match_any_rb)
        self.match_degree_button_group.addButton(self.match_all_rb)
        self.match_degree_button_group.buttonClicked.connect(self.on_match_degree_button_clicked)

        layout.addWidget(QLabel("Type of match"))
        layout.addWidget(self.exact_match_rb)
        layout.addWidget(self.minimal_match_rb)
        layout.addWidget(QLabel("Multiple targets"))
        layout.addWidget(self.match_any_rb)
        layout.addWidget(self.match_all_rb)

        return layout

    def on_search_button_clicked(self, button):
        self.search_clicked.emit(button.objectName())
        

    def on_match_type_button_clicked(self, button):
        self.match_type = button.objectName()

    def on_match_degree_button_clicked(self, button):
        self.match_degree = button.objectName()
    
class SearchResultsView(QWidget):
    def __init__(self):
        super().__init__()
        results=['testing', 'testing', 'beep boop']

        layout = self.create_search_results_layout(results)
        self.setLayout(layout)

        # Set dialog properties
        self.setWindowTitle("Results")
    
    def create_search_results_layout(self, results):
        results_layout = QVBoxLayout()
        
        for text in results:
            label = QLabel(text)
            results_layout.addWidget(label)

        scroll_widget = QWidget()
        scroll_widget.setLayout(results_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)
        return main_layout
    
class SaveTargetButtonBox(QWidget):
    save_clicked = pyqtSignal()
    restore_defaults_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.save_button = QPushButton('Save', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.restore_defaults_button = QPushButton('Restore defaults', self)

        self.save_button.setEnabled(False)

        layout = QHBoxLayout(self)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.restore_defaults_button)

        self.save_button.clicked.connect(self.on_save_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.restore_defaults_button.clicked.connect(self.on_restore_defaults_clicked)


    def on_save_clicked(self):
        self.save_clicked.emit()

    def on_cancel_clicked(self):
        self.parent().reject()  

    def on_restore_defaults_clicked(self):
        self.restore_defaults_clicked.emit()

class InitialButtonBox(QWidget):
    # TODO change the on save on continue
    continue_clicked = pyqtSignal()
    restore_defaults_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.save_button = QPushButton('Continue', self)
        self.cancel_button = QPushButton('Cancel', self)
        self.restore_defaults_button = QPushButton('Restore defaults', self)
        
        self.save_button.setEnabled(False) 

        layout = QHBoxLayout(self)
        layout.addWidget(self.save_button)
        layout.addWidget(self.cancel_button)
        layout.addWidget(self.restore_defaults_button)

        self.save_button.clicked.connect(self.on_save_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        self.restore_defaults_button.clicked.connect(self.on_restore_defaults_clicked)

    def buttons(self):
        return [self.save_button, self.cancel_button, self.restore_defaults_button]

    def on_save_clicked(self):
        self.continue_clicked.emit()

    def on_cancel_clicked(self):
        self.parent().reject()  

    def on_restore_defaults_clicked(self):
        self.restore_defaults_clicked.emit()

class SearchWindowSign: # equivalent of sign for when xslotstructure etc need to be specified due to subclassing
    def __init__(self):
        self.xslotstructure = XslotStructure()

class ResultsView(QWidget):
    def __init__(self, searchmodel, corpus, **kwargs):
        super().__init__(**kwargs)

        self.setWindowTitle("Search Results")
        
        self.model = ResultsModel(searchmodel, corpus)

        self.table_view = QTableView(parent=self)
        self.table_view.setModel(self.model)

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)