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
    QListWidgetItem
)
import copy 
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes

SignLevelInfoTarget = "sign level info"
XSlotTarget = "xslot"
SignTypeInfoTarget = "sign type info"

class SearchItem():
    def __init__(self):
        self._moduledict = None
        self._matchtype = None # exact / minimal
        self._matchdegree = None # any / all
        self._searchtargetdict = None
        self._searchtype = None # new / add

    def __repr__(self):
        repr = "SearchItem:\n " + str(self.matchtype) + " match; " +  "match " + str(self.matchdegree) + "\n" + str(self.searchtype) + " search"
        return repr
    
    @property
    def moduledict(self):
        return self._moduledict

    @moduledict.setter
    def moduledict(self, value):
        self._moduledict = value

    @property
    def matchtype(self):
        return self._matchtype

    @matchtype.setter
    def matchtype(self, value):
        self._matchtype = value

    @property
    def matchdegree(self):
        return self._matchdegree

    @matchdegree.setter
    def matchdegree(self, value):
        self._matchdegree = value

    @property
    def searchtargetdict(self):
        return self._searchtargetdict

    @searchtargetdict.setter
    def searchtargetdict(self, value):
        self._searchtargetdict = value

    @property
    def searchtype(self):
        return self._searchtype

    @searchtype.setter
    def searchtype(self, value):
        self._searchtype = value

class SearchTargetItem(QObject):
    def __init__(self, targettype):
        self._name = None
        self._xslottype = None 
        self._xslotnum = None # only set if xslottype is concrete
        self.dict = dict()

        self.targettype = targettype

    def __repr__(self):
        msg =  "Name: " + str(self.name) + "\nxslottype: " + str(self.xslottype) + "\nxslotnum: " + str(self.xslotnum) + "\ntargettype " + str(self.targettype)  
        msg += "\nDict: " + repr(self.dict)
        return msg
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def xslottype(self):
        return self._xslottype

    @xslottype.setter
    def xslottype(self, value):
        self._xslottype = value

    @property
    def xslotnum(self):
        if self._xslotnum == None:
            return "None"
    
        return self._xslotnum

    @xslotnum.setter
    def xslotnum(self, value):
        self._xslotnum = value

class SearchDisplay(QWidget):

    def __init__(self, parent=None, corpus=None):
        super().__init__(parent=parent)

        self.mainwindow = parent
        self.searchitem = SearchItem()
        self.corpus = corpus

        self.create_layout()

    def create_layout(self):
        self.mdi_area = QMdiArea()

        self.search_targets_view = SearchTargetsView()
        self.search_params_view = SearchParamsView()
        self.build_search_target_view = BuildSearchTargetView()

        search_param_window = self.addSubWindow(self.mdi_area, "Search Parameters")
        build_search_window = self.addSubWindow(self.mdi_area, "Build Search Target")
        search_targets_window = self.addSubWindow(self.mdi_area, "Search Targets")

        self.search_params_view.search_clicked.connect(self.handle_search_clicked)
        self.build_search_target_view.target_added.connect(self.handle_new_search_target_added)
        
        self.search_targets_view.add_new_target("test")
        search_param_window.setWidget(self.search_params_view)
        search_targets_window.setWidget(self.search_targets_view)
        build_search_window.setWidget(self.build_search_target_view)
        
        self.mdi_area.tileSubWindows()
        self.mdi_area.show()

    def addSubWindow(self, area, title):
        window = QMdiSubWindow()
        area.addSubWindow(window)
        window.setWindowTitle(title)
        return window
    
    def handle_search_clicked(self, type):
        self.searchitem.searchtype = type

            # self.results_view = SearchResultsView()
            # self.results_view.setWindowFlag(2)  # Set modeless to allow clicking away from results
            # self.results_view.show()

        self.corpus.search(self.searchitem)
        box = QMessageBox()
        box.setText(repr(self.searchitem))
        box.exec_()

    def handle_match_type_changed(self, type):
        self.searchitem.matchtype = type

    def handle_match_degree_changed(self, degree):
        self.searchitem.matchdegree = degree

    def handle_new_search_target_added(self):
        print("hheyoere")
        # self.search_targets_view.add_new_target(target)

            
class SearchTargetsView(QWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.list_widget = QListWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        self.setLayout(layout)
    
    def add_new_target(self, target):
        item = QListWidgetItem(repr(target))
        self.list_widget.addItem(item)
        self.list_widget.repaint()
        

class BuildSearchTargetView(QScrollArea): # Similarities to panel's SignLevelMenuPanel
    target_added = pyqtSignal()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.targettype = None
        self.targetitem = None

        self.setFrameStyle(QFrame.StyledPanel)
        main_frame = QFrame(parent=self)

        main_layout = self.create_button_layout()
        main_frame.setLayout(main_layout)


    def create_button_layout(self):
        layout = QVBoxLayout()
        self.buttonsgroup = QButtonGroup()

        self.signlevel_button = QPushButton("Sign-level information")
        self.signtype_button = QPushButton("Sign type information")
        self.xslots_button = QPushButton("X-slot information")
        self.movement_button = QPushButton("Add movement module")
        self.location_button = QPushButton("Add location module")
        self.relation_button = QPushButton("Add relation module")
        self.orientation_button = QPushButton("Add orientation module")
        self.handshape_button = QPushButton("Add hand configuration module")
        self.nonmanual_button = QPushButton("Add non-manual module")

        buttons = [
            self.signlevel_button,
            self.signtype_button,
            self.xslots_button,
            self.movement_button,
            self.location_button,
            self.relation_button,
            self.orientation_button,
            self.handshape_button,
            self.nonmanual_button
        ]

        for button in buttons:
            self.buttonsgroup.addButton(button)
            layout.addWidget(button)
            # add a line after xslots-button
            if button == self.xslots_button:
                line = QFrame()
                line.setFrameShape(QFrame.HLine)
                line.setFrameShadow(QFrame.Sunken)
                layout.addWidget(line)
            
        self.buttonsgroup.buttonClicked.connect(self.on_target_selected)

        return layout

    def on_target_selected(self, button):

        
        if button == self.xslots_button: # Only one dialog
            self.targettype = XSlotTarget
        else:
            self.targettype = ModuleTypes.MOVEMENT


        self.target_widget = TargetWidget(targettype = self.targettype)
        self.target_widget.target_saved.connect(self.on_target_saved)
        


    def on_target_saved(self):
        print("here")
        self.targetitem = SearchTargetItem()
        self.targetitem.targettype = self.target_widget.targettype
        self.targetitem.name = self.target_widget.name
        self.targetitem.xslottype = self.target_widget.xslottype
        self.targetitem.xslotnum = self.target_widget.xslotnum
        self.targetitem.dict = copy(self.target_widget.dict)

        self.target_added.emit()



class TargetWidget(QWidget):
    target_saved = pyqtSignal()
    def __init__(self, targettype, **kwargs):
        super().__init__(**kwargs)
        self.targettype = targettype
        self.name = None
        self.xslottype = None
        self.xslotnum = None
        self.dict = dict()

        self.initial_dialog = QDialog(self)
        self.initial_dialog.setLayout(self.create_initial_layout())
        if self.initial_dialog.exec_():
            self.handle_initial_dialog_accepted() 
            

    def handle_initial_dialog_accepted(self):
        if self.targettype in [XSlotTarget]:
            print("emitting target widget")
            self.target_saved.emit()
        else:
            self.secondary_dialog = QDialog(self)
            self.secondary_dialog.setLayout(self.create_secondary_layout())
            if self.secondary_dialog.exec_():
                print("Emitting secondary widget")
                self.target_saved.emit()

    def create_initial_layout(self):
        initial_layout = QVBoxLayout()

        # in all cases, prompt user to name search target
        self.name_widget = NameWidget()
        initial_layout.addWidget(self.name_widget)

        # most targettypes prompt user to specify xslot type
        if self.targettype not in [XSlotTarget, SignLevelInfoTarget, SignTypeInfoTarget]:
            self.xslot_widget = XSlotTypeWidget()
            initial_layout.addWidget(self.xslot_widget)
        
        # xslot target type only shows one window
        if self.targettype == XSlotTarget:
            self.xslottargetnum_widget = XSlotTargetNumWidget()
            initial_layout.addWidget(self.xslottargetnum_widget)


        # todo change to "Continue"
        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.initial_button_box = QDialogButtonBox(buttons, parent=self)
        self.initial_button_box.clicked.connect(self.handle_initial_button_click)
        initial_layout.addWidget(self.initial_button_box)

        return initial_layout

    # Used by target types that have a secondary widget
    def handle_initial_button_click(self, button):
        standard = self.initial_button_box.standardButton(button)
        
        if standard == QDialogButtonBox.Ok:
            # todo validate and save
            self.save_search_target_name()
            
            if self.targettype == XSlotTarget: # This target type has only one window.
                self.save_xslot_target()
            if self.targettype not in [XSlotTarget]:
                self.save_xslot_type()
            self.initial_dialog.accept()

            
                
        elif standard == QDialogButtonBox.Cancel:
            self.initial_dialog.reject()

    
    def create_secondary_layout(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("This is the second widget"))

        buttons = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.secondary_button_box = QDialogButtonBox(buttons, parent=self)
        self.secondary_button_box.clicked.connect(self.handle_secondary_button_click)
        layout.addWidget(self.secondary_button_box)

        return layout
    
    # Used by target types that have a secondary widget
    # todo validate and save
    def handle_secondary_button_click(self, button):
        standard = self.secondary_button_box.standardButton(button)
        
        if standard == QDialogButtonBox.Ok:
            self.secondary_dialog.accept()
                
        elif standard == QDialogButtonBox.Cancel:
            self.secondary_dialog.reject()




    def save_search_target_name(self):
        self.name = self.name_widget.name

    def save_xslot_type(self):
        self.xslottype = self.xslot_widget.xslot_type
        self.xslotnum = self.xslot_widget.xslot_num
        
    def save_xslot_target(self):
        if self.xslottargetnum_widget.has_max and self.xslottargetnum_widget.max != "":
            self.dict["xslot target max"] = self.xslottargetnum_widget.max
        if self.xslottargetnum_widget.has_min and self.xslottargetnum_widget.min != "":
            self.dict["xslot target min"] = self.xslottargetnum_widget.min

class NameWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.name = None

        layout = QVBoxLayout()
        label = QLabel("Name of search target")
        text_entry = QLineEdit()
        text_entry.textEdited.connect(self.on_name_edited)

        layout.addWidget(label)
        layout.addWidget(text_entry)
        self.setLayout(layout)

    def on_name_edited(self, str):
        self.name = str

class XSlotTypeWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.xslot_type = None
        self.xslot_num = None

        layout = QVBoxLayout()

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

        layout.addWidget(self.ignore_xslots_rb)
        layout.addWidget(self.abstract_xslot_rb)
        layout.addWidget(self.abstract_whole_sign_rb)

        concrete_xslots_layout = QHBoxLayout()
        concrete_xslots_layout.addWidget(self.concrete_xslots_rb)
        concrete_xslots_layout.addWidget(self.concrete_xslots_num)

        layout.addLayout(concrete_xslots_layout)

        self.xslot_type_button_group.buttonClicked.connect(self.on_xslot_type_clicked)
        self.setLayout(layout)
    
    def on_xslots_num_edited(self, num):
        self.xslot_num = num
        self.concrete_xslots_rb.setChecked(True)

    def on_xslot_type_clicked(self, btn):
        self.xslot_type = btn      
        self.concrete_xslots_num.setEnabled(btn == self.concrete_xslots_rb)

class XSlotTargetNumWidget(QWidget):

    def __init__(self):
        super().__init__()

        self.has_max = False
        self.max = None
        self.has_min = False
        self.min = None

        layout = QVBoxLayout()

        self.xslottargetnum_button_group = QButtonGroup()
        self.min_xslots_cb = QCheckBox('Minimum number of x_slots:')
        self.max_xslots_cb = QCheckBox('Maximum number of x_slots:') 
        self.max_num = QLineEdit()
        self.min_num = QLineEdit()

        self.xslottargetnum_button_group.addButton(self.min_xslots_cb)
        self.xslottargetnum_button_group.addButton(self.max_xslots_cb)

        for button in self.xslottargetnum_button_group.buttons():
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


        self.max_num.textEdited.connect(self.on_xslottarget_max_edited)
        self.min_num.textEdited.connect(self.on_xslottarget_min_edited)

        self.setLayout(layout)
    
    def on_xslottarget_max_edited(self, num):
        self.max_xslots_cb.setEnabled(True)
        self.max_xslots_cb.setChecked(True)
        self.has_max = True
        self.max = num
            

    def on_xslottarget_min_edited(self, num):
        self.min_xslots_cb.setEnabled(True)
        self.min_xslots_cb.setChecked(True)
        self.has_min = True
        self.min = num
            

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
    
