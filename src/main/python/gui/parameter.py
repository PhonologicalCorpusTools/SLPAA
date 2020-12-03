from PyQt5.QtCore import (
    Qt,
    QSize
)
from PyQt5.Qt import (
    QStandardItemModel, QStandardItem
)
from PyQt5.QtWidgets import (
    QGroupBox,
    QPlainTextEdit,
    QLineEdit,
    QGridLayout,
    QListView,
    QVBoxLayout,
    QHBoxLayout,
    QMainWindow,
    QWidget,
    QLabel,
    QToolBar,
    QAction,
    QStatusBar,
    QTreeView
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)

class ParameterNode(QStandardItem):
    def __init__(self, name, checkable=True):
        super().__init__()
        self.setText(name)
        self.setCheckable(checkable)

    def __str__(self):
        return self.text()

    def __repr__(self):
        return self.text()


class ParameterView(QGroupBox):
    def __init__(self, title, parent=None):
        super().__init__(title, parent=parent)
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        parameter_view = QTreeView(parent=self)
        main_layout.addWidget(parameter_view)
        parameter_view.setHeaderHidden(True)

        parameter_model = QStandardItemModel(parent=self)
        parameter_view.setModel(parameter_model)

        root_note = parameter_model.invisibleRootItem()

        #Quality, Major Movement, Local Movement, Major Location, Reduplication
        #Quality: Contact, Non-temporal, Temporal

        quality = ParameterNode('Quality', checkable=False)
        major_movement = ParameterNode('Major Movement', checkable=False)
        local_movement = ParameterNode('Local Movement', checkable=False)
        major_location = ParameterNode('Major Location', checkable=False)
        reduplication = ParameterNode('Reduplication', checkable=False)

        root_note.appendRows([quality, major_movement, local_movement, major_location, reduplication])

        # Quality
        quality_contact = ParameterNode('Contact', checkable=False)
        self.quality_contact_none = ParameterNode('None')
        self.quality_contact_contacting = ParameterNode('Contacting')
        quality_contact.appendRows([self.quality_contact_none, self.quality_contact_contacting])

        quality_non_temporal = ParameterNode('Non-temporal', checkable=False)
        self.quality_non_temporal_none = ParameterNode('None')
        self.quality_non_temporal_tensed = ParameterNode('Tensed')
        self.quality_non_temporal_reduced = ParameterNode('Reduced')
        self.quality_non_temporal_enlarged = ParameterNode('Enlarged')
        quality_non_temporal.appendRows([self.quality_non_temporal_none, self.quality_non_temporal_tensed, self.quality_non_temporal_reduced, self.quality_non_temporal_enlarged])

        quality_temporal = ParameterNode('Temporal', checkable=False)
        self.quality_temporal_none = ParameterNode('None')
        self.quality_temporal_prolonged = ParameterNode('Prolonged')
        self.quality_temporal_shortened = ParameterNode('Shortened')
        self.quality_temporal_accelerating = ParameterNode('Accelerating')
        quality_temporal.appendRows([self.quality_temporal_none, self.quality_temporal_prolonged, self.quality_temporal_shortened, self.quality_temporal_accelerating])

        quality.appendRows([quality_contact, quality_non_temporal, quality_temporal])

        # Major Movement
        major_movement_contour_of_movement = ParameterNode('Contour of movement', checkable=False)
        self.major_movement_contour_of_movement_hold = ParameterNode('Hold')
        self.major_movement_contour_of_movement_arc = ParameterNode('Arc')
        self.major_movement_contour_of_movement_circle = ParameterNode('Circle')
        self.major_movement_contour_of_movement_seven = ParameterNode('Seven')
        self.major_movement_contour_of_movement_straight = ParameterNode('Straight')
        self.major_movement_contour_of_movement_z_movement = ParameterNode('Z-movement')
        major_movement_contour_of_movement.appendRows([self.major_movement_contour_of_movement_hold,
                                                       self.major_movement_contour_of_movement_arc,
                                                       self.major_movement_contour_of_movement_circle,
                                                       self.major_movement_contour_of_movement_seven,
                                                       self.major_movement_contour_of_movement_straight,
                                                       self.major_movement_contour_of_movement_z_movement])

        major_movement_contour_planes = ParameterNode('Contour planes', checkable=False)
        self.major_movement_contour_planes_hold = ParameterNode('Hold')
        self.major_movement_contour_planes_horizontal = ParameterNode('Horizontal')
        self.major_movement_contour_planes_midline = ParameterNode('Midline')
        self.major_movement_contour_planes_oblique = ParameterNode('Oblique')
        self.major_movement_contour_planes_surface = ParameterNode('Surface')
        self.major_movement_contour_planes_vertical = ParameterNode('Vertical')
        major_movement_contour_planes.appendRows([self.major_movement_contour_planes_hold,
                                                  self.major_movement_contour_planes_horizontal,
                                                  self.major_movement_contour_planes_midline,
                                                  self.major_movement_contour_planes_oblique,
                                                  self.major_movement_contour_planes_surface,
                                                  self.major_movement_contour_planes_vertical])

        major_movement_direction = ParameterNode('Direction', checkable=False)
        self.major_movement_direction_none = ParameterNode('None')
        self.major_movement_direction_forward = ParameterNode('Forward')
        self.major_movement_direction_backward = ParameterNode('Backward')
        major_movement_direction.appendRows([self.major_movement_direction_none,
                                             self.major_movement_direction_forward,
                                             self.major_movement_direction_backward])

        major_movement_major_movement_repetition = ParameterNode('Contour of movement', checkable=False)
        self.major_movement_major_movement_repetition_none = ParameterNode('None')
        self.major_movement_major_movement_repetition_once = ParameterNode('Once')
        self.major_movement_major_movement_repetition_twice = ParameterNode('Twice')
        self.major_movement_major_movement_repetition_multiple = ParameterNode('Multiple')
        self.major_movement_major_movement_repetition_specify = ParameterNode('Specify')
        major_movement_major_movement_repetition.appendRows([self.major_movement_major_movement_repetition_none,
                                                             self.major_movement_major_movement_repetition_once,
                                                             self.major_movement_major_movement_repetition_twice,
                                                             self.major_movement_major_movement_repetition_multiple,
                                                             self.major_movement_major_movement_repetition_specify])

        major_movement.appendRows([major_movement_contour_of_movement, major_movement_contour_planes, major_movement_direction, major_movement_major_movement_repetition])

        local_movement_contour_of_movement = ParameterNode('Contour of movement', checkable=False)
        self.local_movement_contour_of_movement_hold = ParameterNode('Hold')
        self.local_movement_contour_of_movement_circling = ParameterNode('Circling')
        self.local_movement_contour_of_movement_flattening = ParameterNode('Flattening')
        self.local_movement_contour_of_movement_hooking = ParameterNode('Hooking')
        self.local_movement_contour_of_movement_nodding = ParameterNode('Nodding')
        self.local_movement_contour_of_movement_releasing = ParameterNode('Releasing')
        self.local_movement_contour_of_movement_rubbing = ParameterNode('Rubbing')
        self.local_movement_contour_of_movement_shaking = ParameterNode('Shaking')
        self.local_movement_contour_of_movement_twisting = ParameterNode('Twisting')
        self.local_movement_contour_of_movement_wiggling = ParameterNode('Wiggling')
        local_movement_contour_of_movement.appendRows([self.local_movement_contour_of_movement_hold,
                                                       self.local_movement_contour_of_movement_circling,
                                                       self.local_movement_contour_of_movement_flattening,
                                                       self.local_movement_contour_of_movement_hooking,
                                                       self.local_movement_contour_of_movement_nodding,
                                                       self.local_movement_contour_of_movement_releasing,
                                                       self.local_movement_contour_of_movement_rubbing,
                                                       self.local_movement_contour_of_movement_shaking,
                                                       self.local_movement_contour_of_movement_twisting,
                                                       self.local_movement_contour_of_movement_wiggling])

        local_movement_local_repetition = ParameterNode('Local Repetition', checkable=False)
        self.local_movement_local_repetition_none = ParameterNode('None')
        self.local_movement_local_repetition_once = ParameterNode('Once')
        self.local_movement_local_repetition_twice = ParameterNode('Twice')
        self.local_movement_local_repetition_multiple = ParameterNode('Multiple')
        self.local_movement_local_repetition_specify = ParameterNode('Specify')
        local_movement_local_repetition.appendRows([self.local_movement_local_repetition_none,
                                                    self.local_movement_local_repetition_once,
                                                    self.local_movement_local_repetition_twice,
                                                    self.local_movement_local_repetition_multiple,
                                                    self.local_movement_local_repetition_specify])

        local_movement.appendRows([local_movement_contour_of_movement, local_movement_local_repetition])

        major_location_body_location = ParameterNode('Body location')
        major_location_non_dominant_hand_location = ParameterNode('Non-dominant hand location')
        major_location_signing_space_location = ParameterNode('Signing space location')
        major_location.appendRows([major_location_body_location, major_location_non_dominant_hand_location, major_location_signing_space_location])

        reduplication_none = ParameterNode('None')
        reduplication_once = ParameterNode('Once')
        reduplication_twice = ParameterNode('Twice')
        reduplication_multiple = ParameterNode('Multiple')
        reduplication_specify = ParameterNode('Specify')
        reduplication.appendRows([reduplication_none, reduplication_once, reduplication_twice, reduplication_multiple, reduplication_specify])

        parameter_view.expandAll()






