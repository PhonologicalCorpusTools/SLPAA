from fractions import Fraction

import io, os, pickle
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)

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
    QSpacerItem,
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
from gui.decorator import check_unsaved_search_targets
from search.results import ResultsView
import logging
from gui.xslotspecification_view import XslotSelectorDialog, XslotStructure
from constant import XSLOT_TARGET, SIGNLEVELINFO_TARGET, SIGNTYPEINFO_TARGET, MOV_REL_TARGET, LOC_REL_TARGET, HAND, ARM, LEG
import copy 
from PyQt5.QtCore import Qt, pyqtSignal, QObject, pyqtSlot
from lexicon.lexicon_classes import Sign
from gui.panel import SignLevelMenuPanel
from lexicon.module_classes import AddedInfo, TimingInterval, TimingPoint, ParameterModule, ModuleTypes, XslotStructure
from search.search_models import SearchModel, TargetHeaders, SearchValuesItem
from gui.signlevelinfospecification_view import SignlevelinfoSelectorDialog, SignLevelInformation
from search.search_classes import SearchTargetItem, CustomRBGrp, XslotTypes,Search_SignLevelInfoSelectorDialog, Search_ModuleSelectorDialog, XslotTypeItem, Search_SigntypeSelectorDialog

class SearchWindow(QMainWindow):

    def __init__(self, app_settings, corpus, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.searchmodel = SearchModel()
        self.app_ctx = app_ctx
        self.corpus = corpus
        self.app_settings = app_settings
        sli = self.app_ctx.main_window.current_sign.signlevel_information
        self.current_sign = SearchWindowSign(signlevel_info=sli)
        self.current_row = None
        self.unsaved_changes = False

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        self.setWindowTitle("Search")

        # Set up the layout
        self.mdi_area = QMdiArea(main_widget)
        self.init_ui()
        layout = QVBoxLayout(main_widget)
        layout.addWidget(self.mdi_area)


    def create_menu_bar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu('File')

        action_load = QAction(QIcon(self.app_ctx.icons['load16']), 'Load target file', self)
        action_load.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_L))
        action_load.triggered.connect(self.on_action_load)
        file_menu.addAction(action_load)

        action_save = QAction(QIcon(self.app_ctx.icons['save']), 'Save target file', self)
        action_save.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_S))
        action_save.triggered.connect(self.on_action_save)
        file_menu.addAction(action_save)

        # save as
        action_saveas = QAction(QIcon(self.app_ctx.icons['saveas']), 'Save As...', self)
        action_saveas.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_A))
        action_saveas.triggered.connect(self.on_action_save_as)
        file_menu.addAction(action_saveas)


        settings_menu = menu_bar.addMenu('Settings')

    def on_action_load(self):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           self.tr('Load Targets'),
                                                           self.app_settings['storage']['recent_folder'],
                                                           self.tr('SLP-AA SearchTargets (*.slpst)'))
        if not file_name:
            # the user cancelled out of the dialog
            return False
        folder, _ = os.path.split(file_name)
        if folder:
            self.app_settings['storage']['recent_folder'] = folder

        self.searchmodel = self.load_search_binary(file_name)
        self.search_targets_view.table_view.setModel(self.searchmodel)
        self.current_sign.updatemodules(self.searchmodel)
        self.unsaved_changes = False

        return self.searchmodel is not None  # bool(Corpus)

    def on_action_save_as(self):
        
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

            self.save_search_binary()

    @check_unsaved_search_targets
    def on_action_save(self):
        if self.searchmodel.path:
            self.save_search_binary()

        self.unsaved_changes = False
            
    def init_ui(self):
        self.create_menu_bar()
        self.search_targets_view = SearchTargetsView(self.searchmodel, mainwindow=self, parent=self)
        self.search_params_view = SearchParamsView(parent=self)
        self.search_params_view.search_clicked.connect(self.handle_search_clicked)
        self.build_search_target_view = BuildSearchTargetView(sign=None, mainwindow=self, parent=self)
        self.build_search_target_view.target_added.connect(self.handle_new_search_target_added)
        self.build_search_target_view.target_modified.connect(self.handle_target_modified)

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
        if self.searchmodel.rowCount() > 0 and self.search_params_view.match_degree is None:
            mssg += "\nMissing multiple target match type."
        elif self.searchmodel.rowCount() == 0:
            mssg += "\nNothing to search"
        if mssg != "":
            QMessageBox.critical(self, "Warning", mssg)
        else:
            self.searchmodel.searchtype = type
            self.searchmodel.matchtype = self.search_params_view.match_type
            self.searchmodel.matchdegree = self.search_params_view.match_degree

            resultsdict = self.searchmodel.search_corpus(self.corpus)
            self.results_view = ResultsView(resultsdict, mainwindow=self)
            self.results_view.show()
        



    def handle_match_type_changed(self, type):
        self.search_params_view.match_type = type

    def handle_match_degree_changed(self, degree):
        self.search_params_view.match_type = degree

    def handle_new_search_target_added(self, target):
        # TODO update unsaved_changes when targets added or modified.
        self.searchmodel.add_target(target)
    
    def handle_target_modified(self, target, row):
        self.searchmodel.modify_target(target, row)


    def save_search_binary(self):
        with open(self.searchmodel.path, 'wb') as f:
            pickle.dump(self.searchmodel.serialize(), f, protocol=pickle.HIGHEST_PROTOCOL)
        self.unsaved_changes = False
    
    def load_search_binary(self, path):
        with open(path, 'rb') as f:
            searchmodel = SearchModel(serializedsearchmodel=pickle.load(f))
            # in case we're loading a corpus that was originally created on a different machine / in a different folder
            searchmodel.path = path
            return searchmodel
    

            
class SearchTargetsView(QWidget):
    def __init__(self, searchmodel, mainwindow, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = mainwindow

        self.table_view = QTableView(parent=self)
        self.table_view.setModel(searchmodel)
        self.set_table_ui()

        layout = QVBoxLayout()
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        self.table_view.doubleClicked.connect(self.handle_target_doubleclicked) 
    
    def set_table_ui(self):
        self.table_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        # self.table_view.setStyleSheet("QTableView {alignment: AlignCenter;}")
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_view.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.list_del = ListDelegate()
        self.table_view.setItemDelegateForColumn(2, self.list_del) # The "values" column contains lists

        self.table_view.setEditTriggers(QTableView.NoEditTriggers) # disable edit via clicking table
        
    
    def get_search_target_item(self, row):
        model = self.table_view.model()
        it = SearchTargetItem(
            name=model.target_name(row),
            targettype=model.target_type(row),
            xslottype=model.target_xslottype(row),
            searchvaluesitem=model.target_values(row),
            module=model.target_module(row),
            negative=model.is_negative(row),
            include=model.is_included(row)
        )

        return it
    
    def open_module_dialog(self, modulekey, moduletype):
        modules_list = self.mainwindow.current_sign.getmoduledict(moduletype)
        module_to_edit = modules_list[modulekey]
        includearticulators = [HAND, ARM, LEG] if moduletype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION] \
            else ([] if moduletype == ModuleTypes.RELATION else [HAND])
        includephase = 2 if moduletype == ModuleTypes.MOVEMENT else (
            1 if moduletype == ModuleTypes.LOCATION else
            0  # default
        )
        module_selector = Search_ModuleSelectorDialog(moduletype=moduletype,
                                               xslotstructure=self.sign.xslotstructure,
                                               moduletoload=module_to_edit,
                                               includephase=includephase,
                                               incl_articulators=includearticulators,
                                               incl_articulator_subopts=includephase,
                                               parent=self
                                               )
        module_selector.module_saved.connect(
            lambda module_to_save, savedtype:
            self.mainwindow.build_search_target_view.handle_save_module(module_to_save=module_to_save,
                                                               moduletype=savedtype,
                                                               existing_key=modulekey)
        )
        module_selector.module_deleted.connect(
            lambda: self.mainwindow.build_search_target_view.handle_delete_module(existingkey=modulekey, moduletype=moduletype)
        )
        module_selector.exec_()


    def handle_target_doubleclicked(self, index):
        row = index.row()
        item = self.get_search_target_item(row)


        if item.targettype == XSLOT_TARGET:
            timing_selector = XSlotTargetDialog(parent=self, preexistingitem=item)
            timing_selector.target_saved.connect(lambda target_name, max_xslots, min_xslots: 
                                                 self.mainwindow.build_search_target_view.handle_save_xslottarget(target_name, max_xslots, min_xslots, preexistingitem=item, row=row))
            timing_selector.exec_()

        elif item.targettype == SIGNLEVELINFO_TARGET:
            initialdialog = NameDialog(parent=self, preexistingname=item.name)
            initialdialog.continue_clicked.connect(lambda name: 
                                                   self.mainwindow.build_search_target_view.show_next_dialog(SIGNLEVELINFO_TARGET, name, preexistingitem=item, row=row))
            initialdialog.exec_()
        
        elif item.targettype == SIGNTYPEINFO_TARGET:
            initialdialog = NameDialog(parent=self, preexistingname=item.name)
            initialdialog.continue_clicked.connect(lambda name: 
                                                   self.mainwindow.build_search_target_view.show_next_dialog(SIGNTYPEINFO_TARGET, name, preexistingitem=item, row=row))
            initialdialog.exec_()

        
        elif item.targettype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION, LOC_REL_TARGET, MOV_REL_TARGET]:
            initialdialog = XSlotTypeDialog(parent=self, preexistingitem=item)
            initialdialog.continue_clicked.connect(lambda name, xslottype: 
            self.mainwindow.build_search_target_view.show_next_dialog(item.targettype, name, xslottype, preexistingitem=item, row=row))
            initialdialog.exec_()


        
        else:
            QMessageBox.critical(self, "not implemented", "modify on double click not implemented for this target type")



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
    target_modified = pyqtSignal(SearchTargetItem, int)

    def __init__(self, sign, mainwindow, **kwargs):
        super().__init__(sign, mainwindow, **kwargs)
        self.sign = self.mainwindow.current_sign

    def enable_module_buttons(self, yesorno):
        for btn in self.modulebuttons_untimed + self.modulebuttons_timed:
            btn.setEnabled(True)
        self.signtype_button.setEnabled(True)
        self.xslots_button.setEnabled(True)

    def handle_xslotsbutton_click(self):
        timing_selector = XSlotTargetDialog(parent=self)
        timing_selector.target_saved.connect(self.handle_save_xslottarget)
        timing_selector.exec_()
    
    def emit_signal(self, target, row):
        if row == None:
            self.target_added.emit(target)
        else: # modify a preexisting target located at given row
            self.target_modified.emit(target, row)

    def handle_save_xslottarget(self, target_name, max_xslots, min_xslots, preexistingitem=None, row=None):
        negative=False 
        include=False
        if preexistingitem is not None:
            negative = preexistingitem.negative
            include = preexistingitem.include

        svi = SearchValuesItem(type=XSLOT_TARGET, 
                               module=None, 
                               values={ "xslot min": min_xslots, 
                                       "xslot max": max_xslots })
        target = SearchTargetItem(name=target_name, 
                                  targettype=XSLOT_TARGET, 
                                  xslottype=None, 
                                  searchvaluesitem=svi,
                                  include=include,
                                  negative=negative)


        self.emit_signal(target, row)


    def handle_signlevelbutton_click(self):
        initialdialog = NameDialog(parent=self)
        initialdialog.continue_clicked.connect(lambda name: self.show_next_dialog(SIGNLEVELINFO_TARGET, name))
        initialdialog.exec_()
    
    def handle_signtypebutton_click(self):
        initialdialog = NameDialog(parent=self)
        initialdialog.continue_clicked.connect(lambda name: self.show_next_dialog(SIGNTYPEINFO_TARGET, name))
        initialdialog.exec_()

    def handle_menumodulebtn_clicked(self, moduletype):
        initialdialog = XSlotTypeDialog(parent=self)
        initialdialog.continue_clicked.connect(lambda name, xslottype: self.show_next_dialog(moduletype,name,xslottype))
        initialdialog.exec_()

    def show_next_dialog(self, targettype, name, xslottype=None, preexistingitem=None, row=None): 
        self.sign.xslottype = xslottype
        module = None
        negative = False
        include = False
        associatedrelnmodule = None
        if preexistingitem is not None:
            module = preexistingitem.module
            negative = preexistingitem.negative
            include = preexistingitem.include
            associatedrelnmodule = preexistingitem.associatedrelnmodule

        
        if row is not None:
            self.mainwindow.current_row = row
        else:
            self.mainwindow.current_row = self.mainwindow.searchmodel.rowCount()


        target = SearchTargetItem(
            name=name,
            targettype=targettype,
            xslottype=xslottype,
            searchvaluesitem=None,
            module=module,
            negative=negative,
            include=include,
            associatedrelnmodule=associatedrelnmodule
        )
        

        if targettype == SIGNLEVELINFO_TARGET:
            if preexistingitem is not None:
                sli = SignLevelInformation(preexistingitem.searchvaluesitem.values)
            else:
                sli = None
            signlevelinfo_selector = Search_SignLevelInfoSelectorDialog(sli, parent=self)
            signlevelinfo_selector.saved_signlevelinfo.connect(lambda signlevelinfo: self.handle_save_signlevelinfo(target, signlevelinfo, row=row))
            signlevelinfo_selector.exec_()
        
        elif targettype == SIGNTYPEINFO_TARGET:            
            signtypeinfo_selector = Search_SigntypeSelectorDialog(signtypetoload=module, parent=self)
            signtypeinfo_selector.saved_signtype.connect(lambda signtype: self.handle_save_signtype(target, signtype, row=row))
            signtypeinfo_selector.exec_()
            

        
        elif targettype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION, ModuleTypes.RELATION, ModuleTypes.HANDCONFIG, LOC_REL_TARGET, MOV_REL_TARGET]:
            includearticulators = [HAND, ARM, LEG] if targettype in [ModuleTypes.MOVEMENT, ModuleTypes.LOCATION] \
            else ([] if targettype == ModuleTypes.RELATION else [HAND])
            includephase = 2 if targettype == ModuleTypes.MOVEMENT else (
                1 if targettype == ModuleTypes.LOCATION else
                0  # default
            )

            # xslotstructure = XslotStructure()
            module_selector = Search_ModuleSelectorDialog(moduletype=targettype,
                                                xslotstructure=None,
                                                xslottype=xslottype,
                                                moduletoload=module,
                                                includephase=includephase,
                                                incl_articulators=includearticulators,
                                                incl_articulator_subopts=includephase,
                                                parent=self)
            
            module_selector.module_saved.connect(lambda module_to_save: self.handle_add_target(target, module_to_save, row=row))
            
            module_selector.exec_()

    def handle_add_target(self, target, module_to_save, row=None):

        if target.targettype == LOC_REL_TARGET:
            moduletype = ModuleTypes.LOCATION
        elif target.targettype == MOV_REL_TARGET:
            moduletype == ModuleTypes.MOVEMENT
        else:   
            moduletype = target.targettype
        existingkey = module_to_save.uniqueid
        if existingkey is None or existingkey not in self.sign.getmoduledict(moduletype):
            self.sign.addmodule(module_to_save, moduletype)
        else:
            self.sign.updatemodule(existingkey, module_to_save, moduletype)

        target.searchvaluesitem = SearchValuesItem(moduletype, module_to_save)
        target.module = module_to_save

        # check if this is a loc/mvmt target that has just been converted into an anchor target
        curr_row = self.mainwindow.current_row
        if self.mainwindow.searchmodel.target_type(curr_row) in [LOC_REL_TARGET, MOV_REL_TARGET]:
            row = curr_row
            target.targettype = self.mainwindow.searchmodel.target_type(curr_row)
            target.associatedrelnmodule = self.mainwindow.searchmodel.target_associatedrelnmodule(curr_row)

        self.emit_signal(target, row)

    
    def handle_add_associated_relation_module(self, anchormodule, relnmodule):
        row = self.mainwindow.current_row
    
        # Replace the old anchor target with a new connected target
        name = self.mainwindow.searchmodel.target_name(row)
        targettype = MOV_REL_TARGET if self.mainwindow.searchmodel.target_type(row) == ModuleTypes.MOVEMENT else LOC_REL_TARGET
        xslottype = self.mainwindow.current_sign.xslottype
        searchvaluesitem = self.mainwindow.searchmodel.target_values(row)
        searchvaluesitem.type = targettype

        connectedtarget = SearchTargetItem(
            name=name,
            targettype=targettype,
            xslottype=xslottype,
            searchvaluesitem=searchvaluesitem,
            module=anchormodule
        )
        connectedtarget.associatedrelnmodule = relnmodule
        
        # self.sign.updatemodule(anchormodule.uniqueid, anchormodule, )
        self.sign.addmodule(relnmodule, ModuleTypes.RELATION)
        self.emit_signal(connectedtarget, row)
        

    
    def handle_save_signtype(self, target, signtype, row=None):
        target.searchvaluesitem = SearchValuesItem(SIGNTYPEINFO_TARGET, signtype)
        target.module = signtype
        self.emit_signal(target, row)

    def handle_save_signlevelinfo(self, target, signlevel_info, row=None):
        values = {}
        values["entryid"] = signlevel_info.entryid.display_string()
        values["gloss"] = signlevel_info.gloss
        values["idgloss"] = signlevel_info.idgloss
        values["lemma"] = signlevel_info.lemma
        values["source"] = signlevel_info.source
        values["signer"] = signlevel_info.signer
        values["frequency"] = signlevel_info.frequency
        values["coder"] = signlevel_info.coder
        values["date created"] = signlevel_info.datecreated
        values["date last modified"] = signlevel_info.datelastmodified
        values["note"] = signlevel_info.note
        # backward compatibility for attribute added 20230412!
        values["fingerspelled"] = signlevel_info.fingerspelled
        values["compoundsign"] = signlevel_info.compoundsign
        values["handdominance"] = signlevel_info.handdominance
        # TODO update to use signlevel info instead of target values
        target.searchvaluesitem = SearchValuesItem(target.targettype, module=None, values=values)
        self.emit_signal(target, row)
    
    @property
    def sign(self):
        return self._sign
    
    @sign.setter
    def sign(self, sign): # remove parent class's gloss attribute
        self._sign = sign

    def clear(self): # remove parent class's gloss attribute
        self._sign = None

# TODO move these classes to search_classes.py
class NameWidget(QWidget):
    on_name_entered = pyqtSignal()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = ""

        layout = QVBoxLayout()
        label = QLabel("Name of search target")
        self.text_entry = QLineEdit()
        self.text_entry.textChanged.connect(self.on_name_edited)

        layout.addWidget(label)
        layout.addWidget(self.text_entry)
        self.setLayout(layout)

    def on_name_edited(self):
        self.name = self.text_entry.text()
        self.on_name_entered.emit()

class NameDialog(QDialog):
    continue_clicked = pyqtSignal(str)

    def __init__(self, preexistingname=None, **kwargs):
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
        if preexistingname is not None:
            self.reload_item(preexistingname)
    
    def toggle_continue_selectable(self):
        self.buttonbox.save_button.setEnabled(self.name_widget.name != "")
    
    def reload_item(self, name):
        self.name_widget.text_entry.setText(name)
        self.toggle_continue_selectable()


    def on_continue_clicked(self):
        self.continue_clicked.emit(self.name_widget.name)
        self.accept()
    
    def on_restore_defaults_clicked(self):
        self.name_widget.text_entry.setText("")
        self.buttonbox.save_button.setEnabled(False)

class XSlotTypeDialog(QDialog): # TODO maybe subclass the namedialog
    continue_clicked = pyqtSignal(str, XslotTypeItem)

    def __init__(self, preexistingitem=None, **kwargs):
        super().__init__(**kwargs)
        self.mainwindow = self.parent().mainwindow
        self.name_widget = NameWidget(parent=self)
        layout = QVBoxLayout()
        layout.addWidget(self.name_widget)
        self.name_widget.on_name_entered.connect(self.toggle_continue_selectable) 

        self.xslot_type = None

        self.xslot_type_button_group = CustomRBGrp()
        self.ignore_xslots_rb = QRadioButton('Ignore x-slots')
        self.ignore_xslots_rb.setProperty("name", XslotTypes.IGNORE)
        self.abstract_xslot_rb = QRadioButton('Use an abstract x-slot') 
        self.abstract_xslot_rb.setProperty("name", XslotTypes.ABSTRACT_XSLOT)
        self.abstract_whole_sign_rb = QRadioButton('Use an abstract whole sign') 
        self.abstract_whole_sign_rb.setProperty("name", XslotTypes.ABSTRACT_WHOLE)
        self.concrete_xslots_rb = QRadioButton('Use concrete x-slots') 
        self.concrete_xslots_rb.setProperty("name", XslotTypes.CONCRETE)
        self.concrete_xslots_num = QLineEdit()
        self.concrete_xslots_num.setPlaceholderText("Specify number")
        self.concrete_xslots_num.textEdited.connect(self.on_xslots_num_edited)

        self.partial_layout = QVBoxLayout()
        self.partial_label = QLabel("Add a partial x-slot if necessary:")
        self.partial_layout.addWidget(self.partial_label)

        self.fraction_layout = QVBoxLayout()
        partialxslots = self.mainwindow.app_settings['signdefaults']['partial_xslots']
        self.avail_denoms = [Fraction(f).denominator for f in list(partialxslots.keys()) if partialxslots[f]]
        self.fractionalpoints = []
        for d in self.avail_denoms:
            for mult in range(1, d):
                self.fractionalpoints.append(Fraction(mult, d))
        self.fractionalpoints = list(set(self.fractionalpoints))
        self.partial_buttongroup = CustomRBGrp()
        none_radio = QRadioButton("none")
        none_radio.setProperty('fraction', Fraction(0))
        self.partial_buttongroup.addButton(none_radio)
        self.fraction_layout.addWidget(none_radio)
        for fraction in sorted(self.fractionalpoints):
            partial_radio = QRadioButton(str(fraction))
            partial_radio.setProperty('fraction', fraction)
            self.partial_buttongroup.addButton(partial_radio)
            self.fraction_layout.addWidget(partial_radio)
        self.partial_buttongroup.buttonClicked.connect(self.on_xslots_frac_edited)
        if len(self.avail_denoms) == 0:
            self.nopartials_label = QLabel("You do not have any fractional x-slot points selected in Global Settings.")
            self.fraction_layout.addWidget(self.nopartials_label)

        self.fraction_spacedlayout = QHBoxLayout()
        self.fraction_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.fraction_spacedlayout.addLayout(self.fraction_layout)
        self.partial_layout.addLayout(self.fraction_spacedlayout)
        self.partial_spacedlayout = QHBoxLayout()
        self.partial_spacedlayout.addSpacerItem(QSpacerItem(25, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        self.partial_spacedlayout.addLayout(self.partial_layout)


        self.xslot_type_button_group.addButton(self.ignore_xslots_rb) 
        self.xslot_type_button_group.addButton(self.abstract_xslot_rb) 
        self.xslot_type_button_group.addButton(self.abstract_whole_sign_rb) 
        self.xslot_type_button_group.addButton(self.concrete_xslots_rb)
        self.xslot_type_button_group.buttonClicked.connect(self.on_xslot_type_clicked)

        layout.addWidget(self.ignore_xslots_rb)
        layout.addWidget(self.abstract_xslot_rb)
        layout.addWidget(self.abstract_whole_sign_rb)

        concrete_xslots_layout = QVBoxLayout()
        concrete_num_layout = QHBoxLayout()
        concrete_num_layout.addWidget(self.concrete_xslots_rb)
        concrete_num_layout.addWidget(self.concrete_xslots_num)
        concrete_xslots_layout.addLayout(concrete_num_layout)
        concrete_xslots_layout.addLayout(self.partial_spacedlayout)

        layout.addLayout(concrete_xslots_layout)

        self.buttonbox = InitialButtonBox(parent=self)
        self.buttonbox.save_button.setEnabled(False)
        self.buttonbox.continue_clicked.connect(self.on_continue_clicked)
        self.buttonbox.restore_defaults_clicked.connect(self.on_restore_defaults_clicked)
        layout.addWidget(self.buttonbox)

        self.setLayout(layout)

        if preexistingitem is not None:
            self.reload_item(preexistingitem)
    
    def toggle_continue_selectable(self):
        self.buttonbox.save_button.setEnabled(self.name_widget.name != ""  
            and ((self.concrete_xslots_num.text() != "" and self.concrete_xslots_rb.isChecked())
            or (self.xslot_type_button_group.checkedButton() is not None and not self.concrete_xslots_rb.isChecked())))
        
    def on_xslots_num_edited(self):
        self.concrete_xslots_rb.setChecked(True)
        self.xslot_type = self.xslot_type_button_group.checkedButton() 
        self.toggle_continue_selectable()
    
    def on_xslots_frac_edited(self):
        for b in self.xslot_type_button_group.buttons():
            b.setChecked(self.partial_buttongroup.checkedButton() is None)
        self.concrete_xslots_rb.setChecked(self.partial_buttongroup.checkedButton() is not None)
        self.xslot_type = self.xslot_type_button_group.checkedButton() 


    def on_xslot_type_clicked(self):
        if self.xslot_type_button_group.checkedButton() is not None:
            self.xslot_type = self.xslot_type_button_group.checkedButton() 
 
            self.concrete_xslots_num.setEnabled(self.xslot_type == self.concrete_xslots_rb)
            for b in self.partial_buttongroup.buttons():
                b.setEnabled(self.xslot_type == self.concrete_xslots_rb)
        self.toggle_continue_selectable()

    def on_continue_clicked(self):
        txt = ""
        
        if (self.xslot_type == self.concrete_xslots_rb and self.concrete_xslots_num.text() == ""):
            txt = "Specify an x-slot number."
        if txt:
            QMessageBox.critical(self, "Warning", txt)
        else:
            if self.xslot_type == self.ignore_xslots_rb:
                type = XslotTypes.IGNORE
            elif self.xslot_type == self.abstract_xslot_rb:
                type = XslotTypes.ABSTRACT_XSLOT
            elif self.xslot_type == self.abstract_whole_sign_rb:
                type = XslotTypes.ABSTRACT_WHOLE
            elif self.xslot_type == self.concrete_xslots_rb:
                type = XslotTypes.CONCRETE
            else:
                logging.warning("couldn't identify xslot type")
            num = int(self.concrete_xslots_num.text()) if self.concrete_xslots_num.text() != "" else 1
            if self.partial_buttongroup.checkedButton() is not None:
                frac = self.partial_buttongroup.checkedButton().property('fraction')
            else:
                frac = None
            toemit = XslotTypeItem(type, num, frac)
            self.continue_clicked.emit(self.name_widget.name, toemit)
            self.accept()
            
    def reload_item(self, it):
        self.name_widget.text_entry.setText(it.name)
        
        if it.xslottype.type == XslotTypes.ABSTRACT_XSLOT:
            btn_to_check = self.abstract_xslot_rb
        elif it.xslottype.type == XslotTypes.ABSTRACT_WHOLE:
            btn_to_check = self.abstract_whole_sign_rb
        elif it.xslottype.type == XslotTypes.CONCRETE:   
            btn_to_check = self.concrete_xslots_rb
            self.concrete_xslots_num.setText(str(it.xslottype.num))
            for b in self.partial_buttongroup.buttons():
                b.setChecked(b.property('fraction') == it.xslottype.frac)
        else:
            btn_to_check = self.ignore_xslots_rb
        
        for b in self.xslot_type_button_group.buttons():
            b.setChecked(b==btn_to_check)
        self.xslot_type = btn_to_check
        self.toggle_continue_selectable()
    
    def on_restore_defaults_clicked(self):
        self.buttonbox.save_button.setEnabled(False) 
        for b in self.xslot_type_button_group.buttons():
            b.setChecked(False)
        for b in self.partial_buttongroup.buttons():
            b.setChecked(False)
        self.concrete_xslots_num.setText("")
        self.name_widget.text_entry.setText("")

class XSlotTargetDialog(QDialog):
    target_saved = pyqtSignal(str, str, str)

    def __init__(self, preexistingitem=None, **kwargs):
        super().__init__(**kwargs)

        layout = QVBoxLayout()
        self.name_widget = NameWidget()
        layout.addWidget(self.name_widget)
        self.name_widget.on_name_entered.connect(self.toggle_continue_selectable)

        self.min_xslots_cb = QCheckBox('Minimum number of x-slots:')
        self.max_xslots_cb = QCheckBox('Maximum number of x-slots:') 
        self.max_num = QLineEdit()
        self.min_num = QLineEdit()
        self.max_num.textChanged.connect(self.on_xslottarget_max_edited)
        self.min_num.textChanged.connect(self.on_xslottarget_min_edited)

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

        if preexistingitem is not None:
            self.reload_item(preexistingitem)

    def reload_item(self, it):
        self.name_widget.text_entry.setText(it.name)
        if "xslot max" in it.searchvaluesitem.values:
            self.max_num.setText(it.searchvaluesitem.values["xslot max"])
        if "xslot min" in it.searchvaluesitem.values:
            self.min_num.setText(it.searchvaluesitem.values["xslot min"])
        self.toggle_continue_selectable()
    
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
        self.match_type_button_group.buttonToggled.connect(self.on_match_type_button_clicked)

        self.match_degree_button_group = QButtonGroup()
        self.match_any_rb = QRadioButton("Return signs that match any selected targets")
        self.match_all_rb = QRadioButton("Return signs that match all selected targets")
        self.match_any_rb.setObjectName("any")
        self.match_all_rb.setObjectName("all")
        self.match_degree_button_group.addButton(self.match_any_rb)
        self.match_degree_button_group.addButton(self.match_all_rb)
        self.match_degree_button_group.buttonToggled.connect(self.on_match_degree_button_clicked)

        layout.addWidget(QLabel("Type of match"))
        layout.addWidget(self.exact_match_rb)
        layout.addWidget(self.minimal_match_rb)
        layout.addWidget(QLabel("Multiple targets"))
        layout.addWidget(self.match_any_rb)
        layout.addWidget(self.match_all_rb)

        # TODO change default?
        self.match_all_rb.setChecked(True)
        self.minimal_match_rb.setChecked(True)

        return layout

    def on_search_button_clicked(self, button):
        self.search_clicked.emit(button.objectName())
        

    def on_match_type_button_clicked(self, button):
        self.match_type = button.objectName()

    def on_match_degree_button_clicked(self, button):
        self.match_degree = button.objectName()
    
    
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

# TODO consider if main sign inherits from this
# check if xslotstructure is None
# In the search window, the search targets are equivalent to modules of a single sign -- this one.
class SearchWindowSign(Sign): # equivalent of sign for when xslotstructure etc need to be specified due to subclassing
    def __init__(self, signlevel_info=None, serializedsign=None):
        super().__init__(signlevel_info, serializedsign)
        self._xslotstructure = XslotStructure()
        self._xslottype = XslotTypeItem()

        
    
    def updatemodules(self, model):
        for row in range(model.rowCount()):
            moduletype = model.target_type(row)
            if moduletype in [ModuleTypes.LOCATION, ModuleTypes.MOVEMENT, ModuleTypes.HANDCONFIG, ModuleTypes.RELATION, ModuleTypes.ORIENTATION]:
                module_to_add = model.target_module(row)
                self.addmodule(module_to_add, moduletype)

    def addmodule(self, module_to_add, moduletype):
        if module_to_add is not None:
            self.getmoduledict(moduletype)[module_to_add.uniqueid] = module_to_add
            self.getmodulenumbersdict(moduletype)[module_to_add.uniqueid] = self.getnextmodulenumber(moduletype)
        else:
            logging.warning("failed to add " + moduletype)


    def removemodule(self, uniqueid, moduletype):
        self.getmoduledict(moduletype).pop(uniqueid)
        self.removemodulenumber(uniqueid, moduletype)
    
    def lastmodifiednow(self):
        return


    # TODO. probably add xslotstructure, signtype, and signlevel module dicts in the same way as mvmt and loc
    @property
    def xslotstructure(self):
        return self._xslotstructure
    
    @xslotstructure.setter
    def xslotstructure(self, xslotstructure):
        self._xslotstructure = xslotstructure
    
    @property
    def xslottype(self):
        return self._xslottype
    
    @xslottype.setter
    def xslottype(self, xslottype):
        self._xslottype = xslottype
    
