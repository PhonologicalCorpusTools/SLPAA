import os
import json
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
    QListView,
    QVBoxLayout,
    QFileDialog,
    QWidget,
    QTabWidget,
    QTabBar,
    QDialogButtonBox,
    QMessageBox,
    QSlider,
    QTreeView,
    QComboBox,
    QLabel,
    QCompleter,
    QAbstractItemView,
    QStyledItemDelegate,
    QStyle,
    QStyleOptionButton,
    QApplication,
    QHeaderView
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
    pyqtSignal,
    QSize
)

from .helper_widget import EditableTabBar
from gui.movement_view import MovementTreeModel, MovementListModel, MovementPathsProxyModel, TreeSearchComboBox, TreeListView, mutuallyexclusiverole, texteditrole
from constant import LocationParameter, Locations # KV TODO , Movements
from constant import SAMPLE_LOCATIONS
from copy import copy, deepcopy
from pprint import pprint


# https://stackoverflow.com/questions/48575298/pyqt-qtreewidget-how-to-add-radiobutton-for-items
class Delegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        if index.data(Qt.UserRole+mutuallyexclusiverole):
            widget = option.widget
            style = widget.style() if widget else QApplication.style()
            opt = QStyleOptionButton()
            opt.rect = option.rect
            opt.text = index.data()
            opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
            style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)
        # TODO KV delete
        # if not index.parent().isValid():
        #     QStyledItemDelegate.paint(self, painter, option, index)
        # else:
        #     widget = option.widget
        #     style = widget.style() if widget else QApplication.style()
        #     opt = QStyleOptionButton()
        #     opt.rect = option.rect
        #     opt.text = index.data()
        #     opt.state |= QStyle.State_On if index.data(Qt.CheckStateRole) else QStyle.State_Off
        #     style.drawControl(QStyle.CE_RadioButton, opt, painter, widget)


# TODO KV - add sorting options, clear button, undo, ...


# TODO KV - copied from locationspecificationlayout - make sure contents are adjusted for movement
class MovementSpecificationLayout(QHBoxLayout):
    def __init__(self, movement_specifications, app_ctx, **kwargs):
        super().__init__(**kwargs)

        self.treemodel = MovementTreeModel(movementparameters=movement_specifications)
        self.rootNode = self.treemodel.invisibleRootItem()
        self.treemodel.populate(self.rootNode)

        self.listmodel = MovementListModel(self.treemodel)

        self.comboproxymodel = MovementPathsProxyModel(wantselected=False) #, parent=self.listmodel
        self.comboproxymodel.setSourceModel(self.listmodel)

        self.listproxymodel = MovementPathsProxyModel(wantselected=True)
        self.listproxymodel.setSourceModel(self.listmodel)

        selection_layout = QVBoxLayout()
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Enter tree node"))  # TODO KV delete? , self))

        self.combobox = TreeSearchComboBox(self)
        self.combobox.setModel(self.comboproxymodel)
        self.combobox.setCurrentIndex(-1)
        self.combobox.adjustSize()
        self.combobox.setEditable(True)
        self.combobox.setInsertPolicy(QComboBox.NoInsert)
        self.combobox.setFocusPolicy(Qt.StrongFocus)
        self.combobox.setEnabled(True)
        self.combobox.completer().setCaseSensitivity(Qt.CaseInsensitive)
        self.combobox.completer().setFilterMode(Qt.MatchContains)
        self.combobox.completer().setCompletionMode(QCompleter.PopupCompletion)
        # tct = TreeClickTracker(self)  todo kv
        # self.combobox.installEventFilter(tct)
        search_layout.addWidget(self.combobox)

        selection_layout.addLayout(search_layout)

        self.treedisplay = QTreeView()
        self.treedisplay.setItemDelegate(Delegate())
        self.treedisplay.setHeaderHidden(True)
        self.treedisplay.setModel(self.treemodel)
        # self.treedisplay.resizeColumnToContents(0)  # TODO KV more columns?
        # self.treedisplay.header().setSectionResizeMode(QHeaderView.Interactive)
        self.treedisplay.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.treedisplay.setMinimumWidth(500)

        selection_layout.addWidget(self.treedisplay)
        self.addLayout(selection_layout)

        self.pathslistview = TreeListView()
        self.pathslistview.setSelectionMode(QAbstractItemView.MultiSelection)
        self.pathslistview.setModel(self.listproxymodel)
        self.pathslistview.setMinimumWidth(500)

        self.addWidget(self.pathslistview)

        # central_widget.setLayout(mainlayout)
        # self.setCentralWidget(central_widget)  # Install the central widget

        # from location version
        # self.hand_switch = ToggleSwitch()
        # self.hand_switch.setChecked(True)
        # self.hand_switch.clicked.connect(self.change_hand)
        # self.start_location_group_layout = LocationGroupLayout('start', location_specifications, app_ctx)
        # self.end_location_group_layout = LocationGroupLayout('end', location_specifications, app_ctx)
        # self.location_point_panel = LocationPointPanel('Location points')
        #
        # self.addWidget(self.hand_switch)
        # #self.addWidget(self.location_point_panel)
        # self.addLayout(self.start_location_group_layout)
        # self.addLayout(self.end_location_group_layout)

    # todo kv
    # def change_hand(self):
    #     hand = 'D' if self.hand_switch.isChecked() else 'W'
    #     self.start_location_group_layout.change_hand(hand)
    #     self.end_location_group_layout.change_hand(hand)

    def get_movement_value(self):
        movement_value_dict = {
            # 'start': self.start_location_group_layout.get_location_value(),
            # 'end': self.end_location_group_layout.get_location_value()
        }

        return movement_value_dict

    # todo kv
    def clear(self, movement_specifications, app_ctx):
        pass
        # self.hand_switch.setChecked(True)
        # self.start_location_group_layout.clear(location_specifications, app_ctx)
        # self.end_location_group_layout.clear(location_specifications, app_ctx)

    # todo kv
    # def set_value(self, value):
    #     self.start_location_group_layout.set_value(value.start)
    #     self.end_location_group_layout.set_value(value.end)


class MovementDefinerDialog(QDialog):
    # saved_movements = pyqtSignal(Movements)

    def __init__(self, system_default_movement_specifications, movement_specifications, app_settings, app_ctx, **kwargs):
        super().__init__(**kwargs)
        self.app_settings = app_settings
        self.system_default_movement_specifications = system_default_movement_specifications

        self.movement_layout = MovementSpecificationLayout(movement_specifications, app_ctx)

        # main_layout = QVBoxLayout()
        self.setLayout(self.movement_layout)
        self.setMinimumSize(QSize(500, 700))
    #
    #     self.movement_tab = MovementDefinerTabWidget(system_default_movement_specifications, movement_specifications, app_settings, app_ctx, parent=self)
    #     main_layout.addWidget(self.movement_tab)
    #
    #     separate_line = QFrame()
    #     separate_line.setFrameShape(QFrame.HLine)
    #     separate_line.setFrameShadow(QFrame.Sunken)
    #     main_layout.addWidget(separate_line)
    #
    #     buttons = QDialogButtonBox.RestoreDefaults | QDialogButtonBox.Save | QDialogButtonBox.Close
    #
    #     self.button_box = QDialogButtonBox(buttons, parent=self)
    #
    #     import_button = self.button_box.addButton('Import', QDialogButtonBox.ActionRole)
    #     import_button.setProperty('ActionRole', 'Import')
    #
    #     export_button = self.button_box.addButton('Export', QDialogButtonBox.ActionRole)
    #     export_button.setProperty('ActionRole', 'Export')
    #
    #     # TODO KV keep? from orig locationdefinerdialog: Ref: https://programtalk.com/vs2/python/654/enki/enki/core/workspace.py/
    #     self.button_box.clicked.connect(self.handle_button_click)
    #
    #     main_layout.addWidget(self.button_box)
    #
    # def handle_button_click(self, button):
    #     standard = self.button_box.standardButton(button)
    #     if standard == QDialogButtonBox.Close:
    #         response = QMessageBox.question(self, 'Warning',
    #                                         'If you close the window, any unsaved changes will be lost. Continue?')
    #         if response == QMessageBox.Yes:
    #             self.accept()
    #
    #     elif standard == QDialogButtonBox.RestoreDefaults:
    #         self.movement_tab.remove_all_pages()
    #         self.movement_tab.add_default_movement_tabs(is_system_default=True)
    #     # elif standard == QDialogButtonBox.Save:
    #     #     self.save_new_images()
    #     #     self.saved_locations.emit(self.location_tab.get_locations())
    #     #
    #     #     QMessageBox.information(self, 'Locations Saved', 'New locations have been successfully saved!')
    #     # elif standard == QDialogButtonBox.NoButton:
    #     #     action_role = button.property('ActionRole')
    #     #     if action_role == 'Export':
    #     #         file_name, file_type = QFileDialog.getSaveFileName(self,
    #     #                                                            self.tr('Export Locations'),
    #     #                                                            os.path.join(
    #     #                                                                self.app_settings['storage'][
    #     #                                                                    'recent_folder'],
    #     #                                                                'locations.json'),
    #     #                                                            self.tr('JSON Files (*.json)'))
    #     #
    #     #         if file_name:
    #     #             with open(file_name, 'w') as f:
    #     #                 json.dump(self.location_tab.get_locations().get_attr_dict(), f, sort_keys=True, indent=4)
    #     #
    #     #             QMessageBox.information(self, 'Locations Exported',
    #     #                                     'Locations have been successfully exported!')
    #     #     elif action_role == 'Import':
    #     #         file_name, file_type = QFileDialog.getOpenFileName(self, self.tr('Import Locations'),
    #     #                                                            self.app_settings['storage']['recent_folder'],
    #     #                                                            self.tr('JSON Corpus (*.json)'))
    #     #         if file_name:
    #     #             with open(file_name, 'r') as f:
    #     #                 location_json = json.load(f)
    #     #                 imported_locations = Locations(
    #     #                     {loc_id: LocationParameter(name=param['name'],
    #     #                                                image_path=param['image_path'],
    #     #                                                location_polygons=param['location_polygons'],
    #     #                                                default=param['default'])
    #     #                      for loc_id, param in location_json.items()}
    #     #                 )
    #     #                 self.location_tab.import_locations(imported_locations)
    #     #                 self.saved_locations.emit(self.location_tab.get_locations())

        # TODO KV - continue copying from location version in location_definer
