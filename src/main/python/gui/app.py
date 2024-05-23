import errno
import sys
from copy import deepcopy
from os import getcwd
from os.path import join, exists, realpath, dirname
from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from .main_window import MainWindow


class AppContext(ApplicationContext):
    right = "R"
    left = "L"
    both = "both/all"
    div = "with_Divisions"
    nodiv = "no divisions"
    contraoripsi = "contra/ipsi"
    contra = "contra"
    ipsi = "ipsi"

    def __init__(self):
        super().__init__()
        
    def run(self):
        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)

    def get_resource(self, relative_path):
        """
        Translate relative path to absolute path.

        If frozen, refer to the MEIPASS directory;
        If running from source, src/main/resources/base, followed by the rel path.
        Raise FileNotFoundError if abs path cannot be decided
        """
        if hasattr(sys, 'frozen'):  # running as executable
            resource_dir = join(sys._MEIPASS, 'resources')  # cf. 'datas' parameter in .spec
        else:                       # running from source
            parent_dir = dirname(getcwd())
            resource_dir = join(parent_dir, 'resources', 'base')
            # workaround
            if relative_path == 'Icon.ico':
                resource_dir = join(parent_dir, 'icons')

        resource_path = join(resource_dir, relative_path)
        if exists(resource_path):
            return realpath(resource_path)
        raise FileNotFoundError(errno.ENOENT, 'Could not locate resource', relative_path)

    @cached_property
    def icons(self):
        return {
            'blank': self.get_resource('icons/blank.png'),
            'blank16': self.get_resource('icons/blank16.png'),
            'copy': self.get_resource('icons/copy.png'),
            'delete': self.get_resource('icons/delete.png'),
            'load': self.get_resource('icons/load.png'),
            'load16': self.get_resource('icons/load16.png'),
            'paste': self.get_resource('icons/paste.png'),
            'plus': self.get_resource('icons/plus.png'),
            'save': self.get_resource('icons/disk.png'),
            'saveas': self.get_resource('icons/diskpencil.png'),
            'hand': self.get_resource('icons/hand.png'),
            'redo': self.get_resource('icons/redo.png'),
            'undo': self.get_resource('icons/undo.png')
        }

    # @cached_property
    # def default_location_images(self):
    #     return {
    #         'head': self.get_resource('default_location_images/head.jpg'),
    #         'upper_body': self.get_resource('default_location_images/upper_body.jpg'),
    #         'weak_hand': self.get_resource('default_location_images/weak_hand.jpg'),
    #         'body_hands_front': self.get_resource('default_location_images/body_hands_front.png'),
    #         'body_hands_back': self.get_resource('default_location_images/body_hands_back.png')
    #     }

    @cached_property
    def default_location_images(self):
        return {
            'back': self.get_resource('predefined_locations/Back_View.svg'),
            'front': self.get_resource('predefined_locations/Front_View.svg'),
            'side': self.get_resource('predefined_locations/Side_View.svg')
        }

    @cached_property
    def predefined_locations_yellow(self):
        return self.predefined_locations_bycolour("yellow")

    @cached_property
    def predefined_locations_green(self):
        return self.predefined_locations_bycolour("green")

    @cached_property
    def predefined_locations_violet(self):
        return self.predefined_locations_bycolour("violet")

    def predefined_locations_bycolour(self, colour):
        predef_locs = deepcopy(self.predefined_locations_key)
        for locname in predef_locs.keys():
            for side in predef_locs[locname].keys():
                for hasdiv in predef_locs[locname][side].keys():
                    if predef_locs[locname][side][hasdiv]:
                        resource_string = self.get_resource('predefined_locations/' +
                                                            colour +
                                                            '_20240508version/' +
                                                            self.fnamestr_by_predef_locns_descr(locname, side) +
                                                            ("_with_Divisions" if hasdiv == self.div else "") +                                                             '-' +
                                                            colour +
                                                            '.svg')
                        predef_locs[locname][side][hasdiv] = resource_string
                    else:
                        predef_locs[locname][side][hasdiv] = ""
        return predef_locs

    @cached_property
    def predefined_locations_key(self):
        return {
            "Abdominal/waist area": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Above forehead (hairline)": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Ankle": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Armpit": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Arm": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: True},
                self.right: {self.nodiv: True, self.div: True},
            },
            "Back of head": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Behind ear": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Below nose / philtrum": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Between eyebrows": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Between Fingers 1 and 2": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Between Fingers 2 and 3": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Between Fingers 3 and 4": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Between fingers": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Between Thumb and Finger 1": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Biceps": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Buttocks": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Cheek": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Cheek/nose": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Cheekbone in front of ear": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Cheekbone under eye": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Chest/breast area": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Chin": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Corner of mouth": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Earlobe": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Ear": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: True},
                self.right: {self.nodiv: True, self.div: True},
            },
            "Elbow": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Eye region": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Eyebrow": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Eyelid": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Eye": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Face": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Finger 1": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Finger 2": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Finger 3": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Finger 4": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Fingers and thumb": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Fingers": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Foot": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Forearm": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Forehead region": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Forehead": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Groin": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Hand minus fingers": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Whole hand": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: True},
                self.right: {self.nodiv: True, self.div: True},
            },
            "Head": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Heel of hand": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Hip": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Jaw": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Knee": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Leg and foot": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: True},
                self.right: {self.nodiv: True, self.div: True},
            },
            "Lips": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Lower eyelid": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Lower leg": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Lower lip": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Lower torso": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Mouth": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Neck": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Nose": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Nose root": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Nose ridge": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Nose tip": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Nostril": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Outer corner of eye": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            # "Overall": {
            #     self.both: {self.nodiv: True, self.div: True},
            #     self.left: {self.nodiv: False, self.div: False},
            #     self.right: {self.nodiv: False, self.div: False},
            # },
            "Pelvis area": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Septum": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Septum / nostril area": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Shoulder": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Side of face": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Sternum/clavicle area": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Teeth": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Temple": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Thumb": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Top of head": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Torso": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Under chin": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Upper arm above biceps": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Upper arm": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: True, self.div: True},
                self.right: {self.nodiv: True, self.div: True},
            },
            "Upper eyelid": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Upper leg": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
            "Upper lip": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Upper torso": {
                self.both: {self.nodiv: True, self.div: True},
                self.left: {self.nodiv: False, self.div: False},
                self.right: {self.nodiv: False, self.div: False},
            },
            "Wrist": {
                self.both: {self.nodiv: True, self.div: False},
                self.left: {self.nodiv: True, self.div: False},
                self.right: {self.nodiv: True, self.div: False},
            },
        }

    def predef_locns_descr_byfilename(self, filename):
        locationtext = filename.replace("-slash-", "/")
        locationtext = locationtext.replace("_", " ")

        if locationtext.startswith("Right "):
            locationtext = locationtext.replace("Right ", "")
            locationtext = locationtext + " - " + self.contraoripsi
        elif locationtext.startswith("Left "):
            locationtext = locationtext.replace("Left ", "")
            locationtext = locationtext + " - " + self.contraoripsi

        return locationtext

    def fnamestr_by_predef_locns_descr(self, locationtext, RorL):
        filename_string = locationtext.replace("/", "-slash-")
        filename_string = filename_string.replace(" ", "_")

        if RorL == self.right:
            filename_string = "Right_" + filename_string
        elif RorL == self.left:
            filename_string = "Left_" + filename_string
        elif RorL == self.both:
            pass  # we don't have to do anything to the string

        return filename_string

    # @cached_property
    # def predefined_locations_description_byfilename(self):
    #     return {
    #         "Abdominal-Waist_Area": "Abdominal/waist area",
    #         "Above_Forehead-Hairline": "Above Forehead (hairline)",
    #         "Ankles": "Ankles",
    #         "Right_Ankle":  "Ankle - " + self.contraoripsi,
    #         "Left_Ankle": "Ankle - " + self.contraoripsi,
    #         "Armpits": "Armpits",
    #         "Right_Armpit": "Armpit - " + self.contraoripsi,
    #         "Left_Armpit": "Armpit - " + self.contraoripsi,
    #         "Arms": "Arms",
    #         "Right_Arm": "Arm - " + self.contraoripsi,
    #         "Left_Arm": "Arm - " + self.contraoripsi,
    #         "Below_Nose-Philtrum": "Below nose / philtrum",
    #         "Between_Eyebrows": "Between eyebrows",
    #         "Between_Fingers_1_and_2": "Between Fingers 1 and 2",
    #         "Right_Between_Fingers_1_and_2": "Between Fingers 1 and 2 - " + self.contraoripsi,
    #         "Left_Between_Fingers_1_and_2": "Between Fingers 1 and 2 - " + self.contraoripsi,
    #         "Between_Fingers_2_and_3": "Between Fingers 2 and 3",
    #         "Right_Between_Fingers_2_and_3": "Between Fingers 2 and 3 - " + self.contraoripsi,
    #         "Left_Between_Fingers_2_and_3": "Between Fingers 2 and 3 - " + self.contraoripsi,
    #         "Between_Fingers_3_and_4": "Between Fingers 3 and 4",
    #         "Right_Between_Fingers_3_and_4": "Between Fingers 3 and 4 - " + self.contraoripsi,
    #         "Left_Between_Fingers_3_and_4": "Between Fingers 3 and 4 - " + self.contraoripsi,
    #         "Between_Fingers": "Between fingers",
    #         "Right_Between_Fingers": "Between fingers - " + self.contraoripsi,
    #         "Left_Between_Fingers": "Between fingers - " + self.contraoripsi,
    #         "Between_Thumb_and_Finger_1": "Between Thumb and Finger 1",
    #         "Right_Between_Thumb_and_Finger_1": "Between Thumb and Finger 1 - " + self.contraoripsi,
    #         "Left_Between_Thumb_and_Finger_1": "Between Thumb and Finger 1 - " + self.contraoripsi,
    #         "Biceps": "Biceps",
    #         "Left_Bicep": "Biceps - " + self.contraoripsi,
    #         "Right_Bicep": "Biceps - " + self.contraoripsi,
    #         "Cheek_and_Nose": "Cheek/nose",
    #         "Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear",
    #         "Left_Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear - " + self.contraoripsi,
    #         "Right_Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear - " + self.contraoripsi,
    #         "Cheekbone_under_Eye": "Cheekbone under eye",
    #         "Right_Cheekbone_under_Eye": "Cheekbone under eye - " + self.contraoripsi,
    #         "Left_Cheekbone_under_Eye": "Cheekbone under eye - " + self.contraoripsi,
    #         "Cheeks": "Cheeks",
    #         "Left_Cheek": "Cheek - " + self.contraoripsi,
    #         "Right_Cheek": "Cheek - " + self.contraoripsi,
    #         "Chest-Breast_Area": "Chest/breast area",
    #         "Chin": "Chin",
    #         "Corners_of_Mouth": "Corner of mouth",
    #         "Left_Corner_of_Mouth": "Corner of mouth - " + self.contraoripsi,
    #         "Right_Corner_of_Mouth": "Corner of mouth - " + self.contraoripsi,
    #         "Earlobes": "Earlobes",
    #         "Right_Earlobe": "Earlobe - " + self.contraoripsi,
    #         "Left_Earlobe": "Earlobe - " + self.contraoripsi,
    #         "Ears": "Ears",
    #         "Right_Ear": "Ear - " + self.contraoripsi,
    #         "Left_Ear": "Ear - " + self.contraoripsi,
    #         "Elbows": "Elbows",
    #         "Right_Elbow": "Elbow - " + self.contraoripsi,
    #         "Left_Elbow": "Elbow - " + self.contraoripsi,
    #         "Eye_Region": "Eye region",
    #         "Eyebrows": "Eyebrows",
    #         "Right_Eyebrow": "Eyebrow - " + self.contraoripsi,
    #         "Left_Eyebrow": "Eyebrow - " + self.contraoripsi,
    #         "Eyelids": "Eyelids",
    #         "Right_Eyelids": "Eyelids - " + self.contraoripsi,
    #         "Left_Eyelids": "Eyelids - " + self.contraoripsi,
    #         "Eyes": "Eyes",
    #         "Right_Eye": "Eye - " + self.contraoripsi,
    #         "Left_Eye": "Eye - " + self.contraoripsi,
    #         "Face": "Face",
    #         "Feet": "Feet",
    #         "Right_Foot": "Foot - " + self.contraoripsi,
    #         "Left_Foot": "Foot - " + self.contraoripsi,
    #         "Forearms": "Forearms",
    #         "Right_Forearm": "Forearm - " + self.contraoripsi,
    #         "Left_Forearm": "Forearm - " + self.contraoripsi,
    #         "Finger_1": "Finger 1",
    #         "Right_Finger_1": "Finger 1 - " + self.contraoripsi,
    #         "Left_Finger_1": "Finger 1 - " + self.contraoripsi,
    #         "Finger_2": "Finger 2",
    #         "Right_Finger_2": "Finger 2 - " + self.contraoripsi,
    #         "Left_Finger_2": "Finger 2 - " + self.contraoripsi,
    #         "Finger_3": "Finger 3",
    #         "Right_Finger_3": "Finger 3 - " + self.contraoripsi,
    #         "Left_Finger_3": "Finger 3 - " + self.contraoripsi,
    #         "Finger_4": "Finger 4",
    #         "Right_Finger_4": "Finger 4 - " + self.contraoripsi,
    #         "Left_Finger_4": "Finger 4 - " + self.contraoripsi,
    #         "Fingers_and_Thumbs": "Fingers and thumbs",
    #         "Right_Fingers_and_Thumb": "Fingers and thumb - " + self.contraoripsi,
    #         "Left_Fingers_and_Thumb": "Fingers and thumb - " + self.contraoripsi,
    #         "Fingers": "Fingers",
    #         "Right_Fingers": "Fingers - " + self.contraoripsi,
    #         "Left_Fingers": "Fingers - " + self.contraoripsi,
    #         "Forearms": "Forearms",
    #         "Right_Forearm": "Forearm - " + self.contraoripsi,
    #         "Left_Forearm": "Forearm - " + self.contraoripsi,
    #         "Forehead_Region": "Forehead region",
    #         "Forehead": "Forehead",
    #         "Groin": "Groin",
    #         "Hands_minus_Fingers": "Hands minus fingers",
    #         "Right_Hand_minus_Fingers": "Hand minus Fingers - " + self.contraoripsi,
    #         "Left_Hand_minus_Fingers": "Hand minus Fingers - " + self.contraoripsi,
    #         "Hands": "Hands",
    #         "Right_Hand": "Hand - " + self.contraoripsi,
    #         "Left_Hand": "Hand - " + self.contraoripsi,
    #         "Heels_of_Hands": "Heels of hands",
    #         "Right_Heel_of_Hands": "Heel of hand - " + self.contraoripsi,
    #         "Left_Heel_of_Hands": "Heel of hand - " + self.contraoripsi,
    #         "Hips": "Hip",
    #         "Right_Hip": "Hip - " + self.contraoripsi,
    #         "Left_Hip": "Hip - " + self.contraoripsi,
    #         "Jaws": "Jaws",
    #         "Right_Jaw": "Jaw - " + self.contraoripsi,
    #         "Left_Jaw": "Jaw - " + self.contraoripsi,
    #         "Knees": "Knees",
    #         "Right_Knee": "Knee - " + self.contraoripsi,
    #         "Left_Knee": "Knee - " + self.contraoripsi,
    #         "Legs_and_Feet": "Legs and feet",
    #         "Right_Leg_and_Foot": "Leg and foot - " + self.contraoripsi,
    #         "Left_Leg_and_Foot": "Leg and foot - " + self.contraoripsi,
    #         "Lips": "Lips",
    #         "Lower_Eyelids": "Lower eyelids",
    #         "Right_Lower_Eyelid": "Lower eyelid - " + self.contraoripsi,
    #         "Left_Lower_Eyelid": "Lower eyelid - " + self.contraoripsi,
    #         "Mouth": "Mouth",
    #         "Outer_Corners_of_Eyes": "Outer corners of eyes",
    #         "Outer_Corner_of_Left_Eye": "Outer corner of eye - " + self.contraoripsi,
    #         "Outer_Corner_of_Right_Eye": "Outer corner of eye - " + self.contraoripsi,
    #         "Nostrils": "Nostrils",
    #         "Nose": "Nose",
    #         "Nose_Root": "Nose root",
    #         "Nose_Ridge": "Nose ridge",
    #         "Nose_Tip": "Nose tip",
    #         "Right_Nostril": "Nostril - " + self.contraoripsi,
    #         "Left_Nostril": "Nostril - " + self.contraoripsi,
    #         "Pelvis_Area": "Pelvis area",
    #         "Shoulders": "Shoulders",
    #         "Right_Shoulder": "Shoulder - " + self.contraoripsi,
    #         "Left_Shoulder": "Shoulder - " + self.contraoripsi,
    #         "Sides_of_Face": "Sides of face",
    #         "Right_Side_of_Face": "Side of face - " + self.contraoripsi,
    #         "Left_Side_of_Face": "Side of face - " + self.contraoripsi,
    #         "Temple": "Temple",
    #         "Right_Temple": "Temple - " + self.contraoripsi,
    #         "Left_Temple": "Temple - " + self.contraoripsi,
    #         "Thumbs": "Thumbs",
    #         "Right_Thumb": "Thumb - " + self.contraoripsi,
    #         "Left_Thumb": "Thumb - " + self.contraoripsi,
    #         "Upper_Arms_above_Bicep": "Upper arms above bicep",
    #         "Right_Upper_Arm_above_Bicep": "Upper arm above bicep - " + self.contraoripsi,
    #         "Left_Upper_Arm_above_Bicep": "Upper arm above bicep - " + self.contraoripsi,
    #         "Upper_Eyelids": "Upper eyelids",
    #         "Right_Upper_Eyelid": "Upper eyelids - " + self.contraoripsi,
    #         "Left_Upper_Eyelid": "Upper eyelids - " + self.contraoripsi,
    #         "Upper_Legs": "Upper legs",
    #         "Right_Upper_Leg": "Upper leg - " + self.contraoripsi,
    #         "Left_Upper_Leg": "Upper leg - " + self.contraoripsi,
    #         "Upper_Lip": "Upper lip",
    #         "Upper_Torso": "Upper torso",
    #         "Wrists": "Wrists",
    #         "Right_Wrist": "Wrist - " + self.contraoripsi,
    #         "Left_Wrist": "Wrist - " + self.contraoripsi,
    #         "Septum-Nostril_Area": "Septum/nostril area",
    #         "Septum": "Septum",
    #         "Sternum-Clavicle_Area": "Sternum/clavicle area",
    #         "Teeth": "Teeth",
    #         "Top_of_Head": "Top of head",
    #         "Torso": "Torso",
    #         "Underchin": "Under chin",
    #         "Upper_Arms": "Upper arms",
    #         "Right_Upper_Arm": "Upper arm - " + self.contraoripsi,
    #         "Left_Upper_Arm": "Upper arm - " + self.contraoripsi,
    #         "Upper_Torso": "Upper torso",
    #         # TODO KV check
    #     }


    @cached_property
    def hand_illustrations(self):
        return {
            'neutral': self.get_resource('illustrations/neutral.jpg'),
            'slot2': self.get_resource('illustrations/slot2.jpg'),
            'slot3': self.get_resource('illustrations/slot3.jpg'),
            'slot4': self.get_resource('illustrations/slot4.jpg'),
            'slot5': self.get_resource('illustrations/slot5.jpg'),
            'slot6': self.get_resource('illustrations/slot6.jpg'),
            'slot7': self.get_resource('illustrations/slot7.jpg'),
            'slot10': self.get_resource('illustrations/slot10.jpg'),
            'slot11': self.get_resource('illustrations/slot11.jpg'),
            'slot12': self.get_resource('illustrations/slot12.jpg'),
            'slot13': self.get_resource('illustrations/slot13.jpg'),
            'slot14': self.get_resource('illustrations/slot14.jpg'),
            'slot15': self.get_resource('illustrations/slot15.jpg'),
            'slot17': self.get_resource('illustrations/slot17.jpg'),
            'slot18': self.get_resource('illustrations/slot18.jpg'),
            'slot19': self.get_resource('illustrations/slot19.jpg'),
            'slot20': self.get_resource('illustrations/slot20.jpg'),
            'slot22': self.get_resource('illustrations/slot22.jpg'),
            'slot23': self.get_resource('illustrations/slot23.jpg'),
            'slot24': self.get_resource('illustrations/slot24.jpg'),
            'slot25': self.get_resource('illustrations/slot25.jpg'),
            'slot27': self.get_resource('illustrations/slot27.jpg'),
            'slot28': self.get_resource('illustrations/slot28.jpg'),
            'slot29': self.get_resource('illustrations/slot29.jpg'),
            'slot30': self.get_resource('illustrations/slot30.jpg'),
            'slot32': self.get_resource('illustrations/slot32.jpg'),
            'slot33': self.get_resource('illustrations/slot33.jpg'),
            'slot34': self.get_resource('illustrations/slot34.jpg')
        }

    @cached_property
    def predefined(self):
        return {
            'base': self.get_resource('predefined_handshapes/base.png'),
            'no-match': self.get_resource('predefined_handshapes/no-match.png'),
            'empty': self.get_resource('predefined_handshapes/empty.png'),

            '1': self.get_resource('predefined_handshapes/1.png'),
            'bent-1': self.get_resource('predefined_handshapes/bent-1.png'),
            'crooked-1': self.get_resource('predefined_handshapes/crooked-1.png'),

            '3': self.get_resource('predefined_handshapes/3.png'),
            'clawed-3': self.get_resource('predefined_handshapes/clawed-3.png'),
            'contracted-3': self.get_resource('predefined_handshapes/contracted-3.png'),

            '4': self.get_resource('predefined_handshapes/4.png'),
            'bent-4': self.get_resource('predefined_handshapes/bent-4.png'),
            'clawed-4': self.get_resource('predefined_handshapes/clawed-4.png'),
            'crooked-4': self.get_resource('predefined_handshapes/crooked-4.png'),
            'slanted-4': self.get_resource('predefined_handshapes/slanted-4.png'),

            '5': self.get_resource('predefined_handshapes/5.png'),
            'bent-5': self.get_resource('predefined_handshapes/bent-5.png'),
            'bent-midfinger-5': self.get_resource('predefined_handshapes/bent-midfinger-5.png'),
            'clawed-5': self.get_resource('predefined_handshapes/clawed-5.png'),
            'clawed-extended-5': self.get_resource('predefined_handshapes/clawed-extended-5.png'),
            'contracted-5': self.get_resource('predefined_handshapes/contracted-5.png'),
            'relaxed-contracted-5': self.get_resource('predefined_handshapes/relaxed-contracted-5.png'),
            'crooked-5': self.get_resource('predefined_handshapes/crooked-5.png'),
            'crooked-slanted-5': self.get_resource('predefined_handshapes/crooked-slanted-5.png'),
            'modified-5': self.get_resource('predefined_handshapes/modified-5.png'),
            'slanted-5': self.get_resource('predefined_handshapes/slanted-5.png'),
            
            '8': self.get_resource('predefined_handshapes/8.png'),
            'covered-8': self.get_resource('predefined_handshapes/covered-8.png'),
            'extended-8': self.get_resource('predefined_handshapes/extended-8.png'),
            'open-8': self.get_resource('predefined_handshapes/open-8.png'),

            'A': self.get_resource('predefined_handshapes/A.png'),
            'closed-A-index': self.get_resource('predefined_handshapes/closed-A-index.png'),
            'extended-A': self.get_resource('predefined_handshapes/extended-A.png'),
            'A-index': self.get_resource('predefined_handshapes/A-index.png'),
            'modified-A': self.get_resource('predefined_handshapes/modified-A.png'),
            'open-A': self.get_resource('predefined_handshapes/open-A.png'),

            'B1': self.get_resource('predefined_handshapes/B1.png'),
            'bent-B': self.get_resource('predefined_handshapes/bent-B.png'),
            'bent-extended-B': self.get_resource('predefined_handshapes/bent-extended-B.png'),
            'clawed-extended-B': self.get_resource('predefined_handshapes/clawed-extended-B.png'),
            'contracted-B': self.get_resource('predefined_handshapes/contracted-B.png'),
            'extended-B': self.get_resource('predefined_handshapes/extended-B.png'),
            'slanted-extended-B': self.get_resource('predefined_handshapes/slanted-extended-B.png'),

            'B2': self.get_resource('predefined_handshapes/B2.png'),

            'C': self.get_resource('predefined_handshapes/C.png'),
            'clawed-C': self.get_resource('predefined_handshapes/clawed-C.png'),
            'clawed-spread-C': self.get_resource('predefined_handshapes/clawed-spread-C.png'),
            'contracted-C': self.get_resource('predefined_handshapes/contracted-C.png'),
            'extended-C': self.get_resource('predefined_handshapes/extended-C.png'),
            'flat-C': self.get_resource('predefined_handshapes/flat-C.png'),
            'C-index': self.get_resource('predefined_handshapes/C-index.png'),
            'double-C-index': self.get_resource('predefined_handshapes/double-C-index.png'),
            'spread-C': self.get_resource('predefined_handshapes/spread-C.png'),

            'D': self.get_resource('predefined_handshapes/D.png'),
            'partially-bent-D': self.get_resource('predefined_handshapes/partially-bent-D.png'),
            'closed-bent-D': self.get_resource('predefined_handshapes/closed-bent-D.png'),
            'modified-D': self.get_resource('predefined_handshapes/modified-D.png'),

            'E': self.get_resource('predefined_handshapes/E.png'),
            'open-E': self.get_resource('predefined_handshapes/open-E.png'),

            'F': self.get_resource('predefined_handshapes/F.png'),
            'adducted-F': self.get_resource('predefined_handshapes/adducted-F.png'),
            'clawed-F': self.get_resource('predefined_handshapes/clawed-F.png'),
            'covered-F': self.get_resource('predefined_handshapes/covered-F.png'),
            'flat-F': self.get_resource('predefined_handshapes/flat-F.png'),
            'flat-clawed-F': self.get_resource('predefined_handshapes/flat-clawed-F.png'),
            'flat-open-F': self.get_resource('predefined_handshapes/flat-open-F.png'),
            'offset-F': self.get_resource('predefined_handshapes/offset-F.png'),
            'open-F': self.get_resource('predefined_handshapes/open-F.png'),
            'slanted-F': self.get_resource('predefined_handshapes/slanted-F.png'),

            'G': self.get_resource('predefined_handshapes/G.png'),
            'closed-modified-G': self.get_resource('predefined_handshapes/closed-modified-G.png'),
            'closed-double-modified-G': self.get_resource('predefined_handshapes/closed-double-modified-G.png'),
            'double-modified-G': self.get_resource('predefined_handshapes/double-modified-G.png'),
            'modified-G': self.get_resource('predefined_handshapes/modified-G.png'),

            'I': self.get_resource('predefined_handshapes/I.png'),
            'bent-I': self.get_resource('predefined_handshapes/bent-I.png'),
            'bent-combined-I+1': self.get_resource('predefined_handshapes/bent-combined-I+1.png'),
            'clawed-I': self.get_resource('predefined_handshapes/clawed-I.png'),
            'combined-I+1': self.get_resource('predefined_handshapes/combined-I+1.png'),
            'combined-ILY': self.get_resource('predefined_handshapes/combined-ILY.png'),
            'combined-I+A': self.get_resource('predefined_handshapes/combined-I+A.png'),
            'flat-combined-I+1': self.get_resource('predefined_handshapes/flat-combined-I+1.png'),

            'K': self.get_resource('predefined_handshapes/K.png'),
            'extended-K': self.get_resource('predefined_handshapes/extended-K.png'),

            'L': self.get_resource('predefined_handshapes/L.png'),
            'bent-L': self.get_resource('predefined_handshapes/bent-L.png'),
            'bent-thumb-L': self.get_resource('predefined_handshapes/bent-thumb-L.png'),
            'clawed-L': self.get_resource('predefined_handshapes/clawed-L.png'),
            'clawed-extended-L': self.get_resource('predefined_handshapes/clawed-extended-L.png'),
            'contracted-L': self.get_resource('predefined_handshapes/contracted-L.png'),
            'double-contracted-L': self.get_resource('predefined_handshapes/double-contracted-L.png'),
            'crooked-L': self.get_resource('predefined_handshapes/crooked-L.png'),

            'M': self.get_resource('predefined_handshapes/M.png'),
            'flat-M': self.get_resource('predefined_handshapes/flat-M.png'),

            'middle-finger': self.get_resource('predefined_handshapes/middle-finger.png'),

            'N': self.get_resource('predefined_handshapes/N.png'),

            'O': self.get_resource('predefined_handshapes/O.png'),
            'covered-O': self.get_resource('predefined_handshapes/covered-O.png'),
            'flat-O': self.get_resource('predefined_handshapes/flat-O.png'),
            'O-index': self.get_resource('predefined_handshapes/O-index.png'),
            'modified-O': self.get_resource('predefined_handshapes/modified-O.png'),
            'offset-O': self.get_resource('predefined_handshapes/offset-O.png'),
            'open-O-index': self.get_resource('predefined_handshapes/open-O-index.png'),
            'spread-open-O': self.get_resource('predefined_handshapes/spread-open-O.png'),

            'R': self.get_resource('predefined_handshapes/R.png'),
            'bent-R': self.get_resource('predefined_handshapes/bent-R.png'),
            'extended-R': self.get_resource('predefined_handshapes/extended-R.png'),

            'S': self.get_resource('predefined_handshapes/S.png'),

            'T': self.get_resource('predefined_handshapes/T.png'),
            'covered-T': self.get_resource('predefined_handshapes/covered-T.png'),

            'U': self.get_resource('predefined_handshapes/U.png'),
            'bent-U': self.get_resource('predefined_handshapes/bent-U.png'),
            'bent-extended-U': self.get_resource('predefined_handshapes/bent-extended-U.png'),
            'clawed-U': self.get_resource('predefined_handshapes/clawed-U.png'),
            'contracted-U': self.get_resource('predefined_handshapes/contracted-U.png'),
            'contracted-U-index': self.get_resource('predefined_handshapes/contracted-U-index.png'),
            'crooked-U': self.get_resource('predefined_handshapes/crooked-U.png'),
            'extended-U': self.get_resource('predefined_handshapes/extended-U.png'),

            'V': self.get_resource('predefined_handshapes/V.png'),
            'bent-V': self.get_resource('predefined_handshapes/bent-V.png'),
            'bent-extended-V': self.get_resource('predefined_handshapes/bent-extended-V.png'),
            'clawed-V': self.get_resource('predefined_handshapes/clawed-V.png'),
            'clawed-extended-V': self.get_resource('predefined_handshapes/clawed-extended-V.png'),
            'closed-V': self.get_resource('predefined_handshapes/closed-V.png'),
            'crooked-V': self.get_resource('predefined_handshapes/crooked-V.png'),
            'crooked-extended-V': self.get_resource('predefined_handshapes/crooked-extended-V.png'),
            'slanted-V': self.get_resource('predefined_handshapes/slanted-V.png'),

            'W': self.get_resource('predefined_handshapes/W.png'),
            'clawed-W': self.get_resource('predefined_handshapes/clawed-W.png'),
            'closed-W': self.get_resource('predefined_handshapes/closed-W.png'),
            'covered-W': self.get_resource('predefined_handshapes/covered-W.png'),
            'crooked-W': self.get_resource('predefined_handshapes/crooked-W.png'),

            'X': self.get_resource('predefined_handshapes/X.png'),
            'closed-X': self.get_resource('predefined_handshapes/closed-X.png'),

            'Y': self.get_resource('predefined_handshapes/Y.png'),
            'combined-Y+middle': self.get_resource('predefined_handshapes/combined-Y+middle.png'),
            'combined-Y+U': self.get_resource('predefined_handshapes/combined-Y+U.png'),
            # 'modified-Y': self.get_resource('predefined_handshapes/modified-Y.png'),  # this file was deleted 20211115

            'open-palm': self.get_resource('predefined_handshapes/open-palm.png')
        }
