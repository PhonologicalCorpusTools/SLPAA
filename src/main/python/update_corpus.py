import logging
import errno
import sys
from os import getcwd
from os.path import join, exists, realpath, dirname
from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property

import os
import pickle
import json
import csv
from collections import defaultdict
from copy import deepcopy
from datetime import date
from fractions import Fraction
from lexicon.module_classes import ModuleTypes, delimiter
from models import location_models, movement_models

from PyQt5.QtCore import (
    Qt,
    QSize,
    QSettings
)

from PyQt5.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QDialog,
    QGridLayout,
    QToolButton,
    QFrame,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout
)


from gui.main_window import MainWindow
from gui import modulespecification_dialog
from lexicon.lexicon_classes import Corpus, Sign
from serialization_classes import renamed_load
from gui.app import AppContext


class Converter(MainWindow):
    def __init__(self, app_ctx):
        super().__init__(app_ctx)
        self.app_ctx = app_ctx

        return
    
    def load_corpus(self):
        file_name, file_type = QFileDialog.getOpenFileName(self,
                                                           self.tr('Open Corpus'),
                                                           self.app_settings['storage']['recent_folder'])
        if not file_name:
            # the user cancelled out of the dialog
            return False
        folder, _ = os.path.split(file_name)
        if folder:
            self.app_settings['recent_folder'] = folder

        self.corpus = self.load_corpus_binary(file_name)

        self.unsaved_changes = False

        return self.corpus is not None  # bool(Corpus)
    
    def save(self):
        name = "test save"
        file_name, _ = QFileDialog.getSaveFileName(self,
                                                   self.tr('Save Corpus'),
                                                   os.path.join(self.app_settings['storage']['recent_folder'],
                                                                name + '.slpaa'),  # 'corpus.slpaa'),
                                                   self.tr('SLP-AA Corpus (*.slpaa)'))
        if file_name:
            self.corpus.path = file_name
            folder, _ = os.path.split(file_name)
            if folder:
                self.app_settings['storage']['recent_folder'] = folder

            super().save_corpus_binary()


        

    
    def review_changes(self, correctionsdict):
        reviewdialog = ReviewChangesDialog(parent=self, correctionsdict=correctionsdict) 
        response = reviewdialog.exec_()

        # You can use 'result' to determine which button was clicked
        if response == QDialog.Accepted:
            print("Okay button clicked")
            self.save()
            
        else:
            print("Cancel button clicked")

class ReviewChangesDialog(QDialog):
    def __init__(self, correctionsdict, **kwargs):
        super().__init__(**kwargs)
        self.correctionsdict = correctionsdict

        self.setWindowTitle('Update corpus')

        caption_label = QLabel("List of corrections")

        # Create a QLabel to display the contents of correctionsdict
        content_label = QLabel(self.format_dict())

        # Create QDialogButtonBox with Okay and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)

        # Connect the button signals to slots (actions)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        # Create a layout to hold the labels and the button box
        layout = QVBoxLayout()
        layout.addWidget(caption_label)
        layout.addWidget(content_label)
        layout.addWidget(button_box)

        # Set the layout for the QDialog
        self.setLayout(layout)

        # Set the size of the dialog
        self.setGeometry(100, 100, 400, 200)  # Adjust the width and height as needed


    def handle_button_click(self, button):
        standard = self.button_box.standardButton(button)
        if standard == QDialogButtonBox.Cancel:
            self.reject()

    def format_dict(self):
        text = "<table>  <tr><th>Corrected path</th><th>Old path</th></tr>"
        for key, value in self.correctionsdict.items():
            
            text = text + "<tr><td>"
            keynodes = get_node_sequence(key)
            valnodes = get_node_sequence(value)
            for k in keynodes:
                if k not in valnodes:
                    text = text + "<font color='blue'>" + k + "</font>"
                else:
                    text = text + k
                if k != keynodes[-1]:
                    text = text + delimiter
                else:
                    text = text + "</td><td>"
            for v in valnodes:
                
                if v not in keynodes:
                    text = text + "<font color='red'>" + v + "</font>"
                else:
                    text = text + v
                if v != valnodes[-1]:
                    text = text + delimiter
                else:
                    text = text + "</td>"
            text = text+"</tr>"
        text = text + "</table>"
        return text


 ######## put elsewhere??           

def get_mvmt_locn_modules(sign):
    print("\n")
    print(sign)
    mvmtdiff = []
    locndiff = []
    for k in sign.getmoduledict(ModuleTypes.MOVEMENT):
        module = sign.getmoduledict(ModuleTypes.MOVEMENT)[k]
        diff = module.movementtreemodel.compare_checked_lists()
        mvmtdiff.append(diff)
        print ("missing mvmt: " + str(diff) if len(diff) != 0 else "no mvmt diff")
    for k in sign.getmoduledict(ModuleTypes.LOCATION):
        module = sign.getmoduledict(ModuleTypes.LOCATION)[k]
        diff = module.locationtreemodel.compare_checked_lists()
        locndiff.append(diff)
        print ("missing locn: " + str(diff) if len(diff) != 0 else "no locn diff")
    return mvmtdiff, locndiff

def get_node_sequence(item):
    nodes = []
    curr = ""
    for c in item:
        if (c is not delimiter):
            curr = curr + c
        else:
            nodes.append(curr)
            curr = ""
    nodes.append(curr)
    return nodes



def update_nodes(nodes):
    paths_to_add = []
    length = len(nodes)
    # print(length)
   
    # Issue 193: Update thumb movements in joint activity section
    if nodes[0] == 'Joint activity':
        if (nodes[1] == 'Thumb base / metacarpophalangeal'):
            nodes[1] = 'Thumb base / metacarpophalangeal (MCP)'
            paths_to_add.append(nodes)
 
        elif (length > 1 and nodes[1] == 'Thumb non-base / interphalangeal'):
            nodes[1] = 'Thumb non-base / interphalangeal (IP)'
            paths_to_add.append(nodes)

        if (length > 2 and (nodes[2] == 'Abduction' or nodes[2] == 'Adduction')):
            nodes[1] = 'Thumb root / carpometacarpal (CMC)'
            paths_to_add.append(nodes[0:2] + (['Radial abduction'] if nodes[2] == 'Abduction' else ['Radial adduction']))
            paths_to_add.append(nodes[0:2] + (['Palmar abduction'] if nodes[2] == 'Abduction' else ['Palmar adduction']))
                

    # Issue 194: Add abs/rel movement options 
    if (length > 2 and (nodes[2] == 'Axis direction' or nodes[2] == 'Plane') and nodes[3] != 'Absolute'):
        nodes.insert(3, 'Absolute')
        paths_to_add.append(nodes)

    return paths_to_add


appcontext = AppContext()
converter = Converter(appcontext)

# mvmtdiff, locndiff = get_mvmt_locn_modules(list(oldcorpus.signs)[0])

correctionsdict = {}
for sign in converter.corpus.signs:
    print(sign)

    for k in sign.getmoduledict(ModuleTypes.MOVEMENT):
        
        module = sign.getmoduledict(ModuleTypes.MOVEMENT)[k]
        mvmttreemodel = module.movementtreemodel
        missing_values = mvmttreemodel.compare_checked_lists()
        print("missing:")
        for val in missing_values:
            print(val)
        print("\n")

        
        newpaths = []

        for oldpath in missing_values:
            paths_to_add = update_nodes(get_node_sequence(oldpath))
            for path in paths_to_add:

                newpath = delimiter.join(path)
                correctionsdict[newpath] = oldpath 
                newpaths.append(newpath)


        mvmttreemodel.addcheckedvalues(mvmttreemodel.invisibleRootItem(), newpaths, correctionsdict)
        mvmttreemodel.uncheck_in_checkstates(missing_values)



converter.review_changes(correctionsdict)



    

converter.show()
# exit_code = appcontext.app.exec()      
# sys.exit(exit_code)