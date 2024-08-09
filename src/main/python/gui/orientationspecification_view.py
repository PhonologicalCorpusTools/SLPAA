from PyQt5.QtWidgets import (
    QRadioButton,
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
    QGroupBox,
    QCheckBox,
    QSpacerItem,
    QSizePolicy,
)

from lexicon.module_classes import (
    OrientationModule,
    Direction,
)

from gui.modulespecification_widgets import ModuleSpecificationPanel


class OrientationSpecificationPanel(ModuleSpecificationPanel):

    def __init__(self, moduletoload=None, **kwargs):
        super().__init__(**kwargs)

        main_layout = QVBoxLayout()

        # create layout for palm direction
        palm_box = self.create_palm_box()
        main_layout.addWidget(palm_box)
        
        # create layout for finger root direction
        finger_box = self.create_finger_root_box()
        main_layout.addWidget(finger_box)

        # set according to the existing module being loaded
        if moduletoload is not None and isinstance(moduletoload, OrientationModule):
            self.setvalues(moduletoload)
            self.existingkey = moduletoload.uniqueid

        self.setLayout(main_layout)

    def validity_check(self):
        # Needs to be implemented as in all module classes
        # But no for this module, allow any number of empty selections
        return True, ""

    def getsavedmodule(self, articulators, timingintervals, phonlocs, addedinfo, inphase):

        orimod = OrientationModule(palmdirs_list=self.getcurrentpalmdirections(),
                                   rootdirs_list=self.getcurrentrootdirections(),
                                   articulators=articulators,
                                   timingintervals=timingintervals,
                                   phonlocs=phonlocs,
                                   addedinfo=addedinfo
                                   )
        
        if self.existingkey is not None:
            orimod.uniqueid = self.existingkey
        else:
            self.existingkey = orimod.uniqueid
        return orimod

    # create layout for distance or direction options on a particular axis
    def create_axis_layout(self, radio1, radio2, radiogroup, axis_cb=None, axis_label=None):
        axis_layout = QVBoxLayout()
        axisoptions_spacedlayout = QHBoxLayout()
        axisoptions_layout = QVBoxLayout()
        radiogroup.addButton(radio1)
        radiogroup.addButton(radio2)

        if axis_cb is not None:
            radiogroup.buttonToggled.connect(lambda rb, ischecked: self.handle_axisgroup_toggled(rb, ischecked, axis_cb))
            axis_cb.toggled.connect(lambda ischecked: self.handle_axiscb_toggled(ischecked, radiogroup))
            axis_layout.addWidget(axis_cb)
        elif axis_label is not None:
            axis_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            axis_layout.addWidget(axis_label)
        axisoptions_spacedlayout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Minimum, QSizePolicy.Maximum))
        axisoptions_layout.addWidget(radio1)
        axisoptions_layout.addWidget(radio2)
        
        axisoptions_spacedlayout.addLayout(axisoptions_layout)
        axis_layout.addLayout(axisoptions_spacedlayout)

        return axis_layout

    def handle_axiscb_toggled(self, ischecked, radiogroup):
        isdirgroup = radiogroup in [self.palm_dirhor_group, self.palm_dirver_group, self.palm_dirsag_group,
                                    self.root_dirhor_group, self.root_dirver_group, self.root_dirsag_group]

        for btn in radiogroup.buttons():
            btn.setEnabled(ischecked and isdirgroup)

    def handle_axisgroup_toggled(self, rb, ischecked, axis_cb):
        if not ischecked:
            # don't need to do anything special
            return

        # ensure the parent is checked
        axis_cb.setChecked(True)

    # create side-by-side layout for specifying direction of relation
    def create_palm_box(self):
        palm_box = QGroupBox("Direction of palm")
        palm_layout = QVBoxLayout()
        palm_sublayout = QHBoxLayout()

        # create layout for horizontal direction options
        self.palm_dirhor_box = QGroupBox()
        self.palm_dirhor_cb = QCheckBox("Horizontal")
        self.palm_dirhoripsi_rb = OrientationRadioButton("Ipsilateral")
        self.palm_dirhorcontra_rb = OrientationRadioButton("Contralateral")
        self.palm_dirhor_group = OrientationButtonGroup()
        dir_hor_layout = self.create_axis_layout(self.palm_dirhoripsi_rb,
                                                 self.palm_dirhorcontra_rb,
                                                 self.palm_dirhor_group,
                                                 axis_cb=self.palm_dirhor_cb)
        self.palm_dirhor_box.setLayout(dir_hor_layout)
        palm_sublayout.addWidget(self.palm_dirhor_box)

        # create layout for vertical direction options
        self.palm_dirver_box = QGroupBox()
        self.palm_dirver_cb = QCheckBox("Vertical")
        self.palm_dirverup_rb = OrientationRadioButton("Up")
        self.palm_dirverdown_rb = OrientationRadioButton("Down")
        self.palm_dirver_group = OrientationButtonGroup()
        dir_ver_layout = self.create_axis_layout(self.palm_dirverup_rb,
                                                 self.palm_dirverdown_rb,
                                                 self.palm_dirver_group,
                                                 axis_cb=self.palm_dirver_cb)
        self.palm_dirver_box.setLayout(dir_ver_layout)
        palm_sublayout.addWidget(self.palm_dirver_box)

        # create layout for sagittal direction options
        self.palm_dirsag_box = QGroupBox()
        self.palm_dirsag_cb = QCheckBox("Sagittal")
        self.palm_dirsagdist_rb = OrientationRadioButton("Distal")
        self.palm_dirsagprox_rb = OrientationRadioButton("Proximal")
        self.palm_dirsag_group = OrientationButtonGroup()
        dir_sag_layout = self.create_axis_layout(self.palm_dirsagdist_rb,
                                                 self.palm_dirsagprox_rb,
                                                 self.palm_dirsag_group,
                                                 axis_cb=self.palm_dirsag_cb)
        self.palm_dirsag_box.setLayout(dir_sag_layout)
        palm_sublayout.addWidget(self.palm_dirsag_box)

        palm_layout.addLayout(palm_sublayout)
        palm_box.setLayout(palm_layout)
        return palm_box

    def create_finger_root_box(self):
        root_box = QGroupBox("Direction of finger root")
        root_layout = QVBoxLayout()
        root_sublayout = QHBoxLayout()

        # create layout for horizontal direction options
        self.root_dirhor_box = QGroupBox()
        self.root_dirhor_cb = QCheckBox("Horizontal")
        self.root_dirhoripsi_rb = OrientationRadioButton("Ipsilateral")
        self.root_dirhorcontra_rb = OrientationRadioButton("Contralateral")
        self.root_dirhor_group = OrientationButtonGroup()
        dir_hor_layout = self.create_axis_layout(self.root_dirhoripsi_rb,
                                                 self.root_dirhorcontra_rb,
                                                 self.root_dirhor_group,
                                                 axis_cb=self.root_dirhor_cb)
        self.root_dirhor_box.setLayout(dir_hor_layout)
        root_sublayout.addWidget(self.root_dirhor_box)

        # create layout for vertical direction options
        self.root_dirver_box = QGroupBox()
        self.root_dirver_cb = QCheckBox("Vertical")
        self.root_dirverup_rb = OrientationRadioButton("Up")
        self.root_dirverdown_rb = OrientationRadioButton("Down")
        self.root_dirver_group = OrientationButtonGroup()
        dir_ver_layout = self.create_axis_layout(self.root_dirverup_rb,
                                                 self.root_dirverdown_rb,
                                                 self.root_dirver_group,
                                                 axis_cb=self.root_dirver_cb)
        self.root_dirver_box.setLayout(dir_ver_layout)
        root_sublayout.addWidget(self.root_dirver_box)

        # create layout for sagittal direction options
        self.root_dirsag_box = QGroupBox()
        self.root_dirsag_cb = QCheckBox("Sagittal")
        self.root_dirsagdist_rb = OrientationRadioButton("Distal")
        self.root_dirsagprox_rb = OrientationRadioButton("Proximal")
        self.root_dirsag_group = OrientationButtonGroup()
        dir_sag_layout = self.create_axis_layout(self.root_dirsagdist_rb,
                                                 self.root_dirsagprox_rb,
                                                 self.root_dirsag_group,
                                                 axis_cb=self.root_dirsag_cb)
        self.root_dirsag_box.setLayout(dir_sag_layout)
        root_sublayout.addWidget(self.root_dirsag_box)

        root_layout.addLayout(root_sublayout)
        root_box.setLayout(root_layout)
        return root_box

    def setvalues(self, moduletoload):
        self.setcurrentpalmdirection(moduletoload.palm)
        self.setcurrentrootdirection(moduletoload.root)

    def getcurrentpalmdirections(self):
        direction_hor = Direction(axis=Direction.HORIZONTAL,
                                  axisselected=self.palm_dirhor_cb.isChecked(),
                                  plus=self.palm_dirhoripsi_rb.isChecked(),
                                  minus=self.palm_dirhorcontra_rb.isChecked()
                                  )
        direction_ver = Direction(axis=Direction.VERTICAL,
                                  axisselected=self.palm_dirver_cb.isChecked(),
                                  plus=self.palm_dirverup_rb.isChecked(),
                                  minus=self.palm_dirverdown_rb.isChecked()
                                  )
        direction_sag = Direction(axis=Direction.SAGITTAL,
                                  axisselected=self.palm_dirsag_cb.isChecked(),
                                  plus=self.palm_dirsagprox_rb.isChecked(),
                                  minus=self.palm_dirsagdist_rb.isChecked()
                                  )
        directions = [direction_hor, direction_ver, direction_sag]
        return directions

    def getcurrentrootdirections(self):
        direction_hor = Direction(axis=Direction.HORIZONTAL,
                                  axisselected=self.root_dirhor_cb.isChecked(),
                                  plus=self.root_dirhoripsi_rb.isChecked(),
                                  minus=self.root_dirhorcontra_rb.isChecked()
                                  )
        direction_ver = Direction(axis=Direction.VERTICAL,
                                  axisselected=self.root_dirver_cb.isChecked(),
                                  plus=self.root_dirverup_rb.isChecked(),
                                  minus=self.root_dirverdown_rb.isChecked()
                                  )
        direction_sag = Direction(axis=Direction.SAGITTAL,
                                  axisselected=self.root_dirsag_cb.isChecked(),
                                  plus=self.root_dirsagprox_rb.isChecked(),
                                  minus=self.root_dirsagdist_rb.isChecked()
                                  )
        directions = [direction_hor, direction_ver, direction_sag]
        return directions

    def setcurrentpalmdirection(self, directions_list):
        if directions_list is not None:
            hor_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.HORIZONTAL][0]
            ver_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.VERTICAL][0]
            sag_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.SAGITTAL][0]

            self.palm_dirhor_cb.setChecked(hor_direction.axisselected)
            if hor_direction.axisselected:
                self.palm_dirhoripsi_rb.setChecked(hor_direction.plus)
                self.palm_dirhorcontra_rb.setChecked(hor_direction.minus)

            self.palm_dirver_cb.setChecked(ver_direction.axisselected)
            if ver_direction.axisselected:
                self.palm_dirverup_rb.setChecked(ver_direction.plus)
                self.palm_dirverdown_rb.setChecked(ver_direction.minus)

            self.palm_dirsag_cb.setChecked(sag_direction.axisselected)
            if sag_direction.axisselected:
                self.palm_dirsagprox_rb.setChecked(sag_direction.plus)
                self.palm_dirsagdist_rb.setChecked(sag_direction.minus)
            
    def setcurrentrootdirection(self, directions_list):
        if directions_list is not None:
            hor_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.HORIZONTAL][0]
            ver_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.VERTICAL][0]
            sag_direction = [axis_dir for axis_dir in directions_list if axis_dir.axis == Direction.SAGITTAL][0]

            self.root_dirhor_cb.setChecked(hor_direction.axisselected)
            if hor_direction.axisselected:
                self.root_dirhoripsi_rb.setChecked(hor_direction.plus)
                self.root_dirhorcontra_rb.setChecked(hor_direction.minus)

            self.root_dirver_cb.setChecked(ver_direction.axisselected)
            if ver_direction.axisselected:
                self.root_dirverup_rb.setChecked(ver_direction.plus)
                self.root_dirverdown_rb.setChecked(ver_direction.minus)
                
            self.root_dirsag_cb.setChecked(sag_direction.axisselected)
            if sag_direction.axisselected:
                self.root_dirsagprox_rb.setChecked(sag_direction.plus)
                self.root_dirsagdist_rb.setChecked(sag_direction.minus)

    def clear_group_buttons(self, buttongroup):
        buttongroup.setExclusive(False)

        for b in buttongroup.buttons():
            b.setChecked(False)
            b.setEnabled(True)

        buttongroup.setExclusive(True)

    def clear_direction_buttons(self):
        for cb in [self.palm_dirhor_cb, self.palm_dirver_cb, self.palm_dirsag_cb,
                   self.root_dirhor_cb, self.root_dirver_cb, self.root_dirsag_cb]:
            cb.setChecked(False)
        for grp in [self.palm_dirhor_group, self.palm_dirver_group, self.palm_dirsag_group,
                    self.root_dirhor_group, self.root_dirver_group, self.root_dirsag_group]:
            self.clear_group_buttons(grp)

        for grpbox in [self.palm_dirhor_box, self.palm_dirver_box, self.palm_dirsag_box,
                       self.root_dirhor_box, self.root_dirver_box, self.root_dirsag_box]:
            grpbox.setEnabled(True)

    def clear(self):
        self.clear_direction_buttons()

    def desiredwidth(self):
        return 500

    def desiredheight(self):
        return 700


class OrientationRadioButton(QRadioButton):

    def __init__(self, text, **kwargs):
        super().__init__(text, **kwargs)

    def setChecked(self, checked):
        if checked and self.group() is not None:
            self.group().previously_checked = self
        super().setChecked(checked)


class OrientationButtonGroup(QButtonGroup):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # in order to compare new checked button with previously-checked button
        self.previously_checked = None

        self.buttonClicked.connect(self.handle_button_clicked)

    def handle_button_clicked(self, btn):
        if self.previously_checked == btn:
            # user clicked an already-selected button; we'll uncheck it
            self.setExclusive(False)
            btn.setChecked(False)
            self.setExclusive(True)
            self.previously_checked = None
        else:
            # user clicked a previously-unselected button
            self.previously_checked = btn
