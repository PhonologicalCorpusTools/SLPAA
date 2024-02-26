import errno
import sys
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

    @cached_property
    def default_location_images(self):
        return {
            'head': self.get_resource('default_location_images/head.jpg'),
            'upper_body': self.get_resource('default_location_images/upper_body.jpg'),
            'weak_hand': self.get_resource('default_location_images/weak_hand.jpg'),
            'body_hands_front': self.get_resource('default_location_images/body_hands_front.png'),
            'body_hands_back': self.get_resource('default_location_images/body_hands_back.png')
        }

    # TODO KV eventually delete once we've figured out what we're doing with vector/raster images & qualities
    @cached_property
    def temp_test_images(self):
        return {
            'sample_back': self.get_resource('predefined_locations/Back_View.svg'),
            'sample_front': self.get_resource('predefined_locations/Front_View.svg'),
            'sample_side': self.get_resource('predefined_locations/Side_View.svg')
            # 'Between_Eyebrows-green': self.get_resource('predefined_locations/green_HL/Between_Eyebrows-green.svg')
        }

    @cached_property
    def predefined_locations_test(self):
        colour = "yellow"
        return {
            "Abdominal-Waist_Area": self.get_resource('predefined_locations/' + colour + '_HL/Abdominal-Waist_Area-' + colour + '.svg'),
            "Above_Forehead-Hairline": self.get_resource('predefined_locations/' + colour + '_HL/Above_Forehead-Hairline-' + colour + '.svg'),
            "Ankle_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Ankle-' + colour + '.svg'),
            "Ankle_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Ankle-' + colour + '.svg'),
            "Armpit_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Armpit-' + colour + '.svg'),
            "Armpit_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Armpit-' + colour + '.svg'),
            "Arm_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Arm-' + colour + '.svg'),
            "Arm_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Arm-' + colour + '.svg'),
            "Below_Nose-Philtrum": self.get_resource('predefined_locations/' + colour + '_HL/Below_Nose-Philtrum-' + colour + '.svg'),
            "Between_Eyebrows": self.get_resource('predefined_locations/' + colour + '_HL/Between_Eyebrows-' + colour + '.svg'),
            "Between_Fingers_1_and_2_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_1_and_2-' + colour + '.svg'),
            "Between_Fingers_1_and_2_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_1_and_2-' + colour + '.svg'),
            "Between_Fingers_2_and_3_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_2_and_3-' + colour + '.svg'),
            "Between_Fingers_2_and_3_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_2_and_3-' + colour + '.svg'),
            "Between_Fingers_3_and_4_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_3_and_4-' + colour + '.svg'),
            "Between_Fingers_3_and_4_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_3_and_4-' + colour + '.svg'),
            "Between_Fingers_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers-' + colour + '.svg'),
            "Between_Fingers_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers-' + colour + '.svg'),
            "Between_Thumb_and_Finger_1_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Thumb_and_Finger_1-' + colour + '.svg'),
            "Between_Thumb_and_Finger_1_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Thumb_and_Finger_1-' + colour + '.svg'),
            "Biceps_Left": self.get_resource('predefined_locations/' + colour + '_HL/Left_Bicep-' + colour + '.svg'),
            "Biceps_Right": self.get_resource('predefined_locations/' + colour + '_HL/Right_Bicep-' + colour + '.svg'),
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
        return {
            "Abdominal/waist area": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Abdominal-Waist_Area-' + colour + '.svg')}
            },
            "Above forehead (hairline)": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Above_Forehead-Hairline-' + colour + '.svg')}
            },
            "Ankle": {
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Ankle-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Ankle-' + colour + '.svg')},
            },
            "Ankles": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Ankles-' + colour + '.svg')},
            },
            "Armpit": {
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Armpit-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Armpit-' + colour + '.svg')},
            },
            "Armpits": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Armpits-' + colour + '.svg')},
            },
            # # TODO KV fix
            # "Ankles": self.get_resource('predefined_locations/' + colour + '_HL/Ankles-' + colour + '.svg'),
            # "Armpits": self.get_resource('predefined_locations/' + colour + '_HL/Armpits-' + colour + '.svg'),
            # "Arms": self.get_resource('predefined_locations/' + colour + '_HL/Arms-' + colour + '.svg'),
            # "Chin": self.get_resource('predefined_locations/' + colour + '_HL/Chin-' + colour + '.svg'),
            "Arm": {
                self.left: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Arm_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Arm-' + colour + '.svg'),
                },
                self.right: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Arm_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Arm-' + colour + '.svg'),
                },
            },
            "Arms": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Arms_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Arms-' + colour + '.svg'),
                }
            },
            "Back of head": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Back_of_Head-' + colour + '.svg')}
            },
            "Behind ear": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Behind_Ears-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Behind_Ear-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Behind_Ear-' + colour + '.svg')},
            },
            "Below nose / philtrum": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Below_Nose-Philtrum-' + colour + '.svg')}
            },
            "Between eyebrows": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Eyebrows-' + colour + '.svg')}
            },
            "Between Fingers 1 and 2": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers_1_and_2-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_1_and_2-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_1_and_2-' + colour + '.svg')},
            },
            "Between Fingers 2 and 3": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers_2_and_3-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_2_and_3-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_2_and_3-' + colour + '.svg')},
            },
            "Between Fingers 3 and 4": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers_3_and_4-' + colour + '.svg')},
                self.left: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_3_and_4-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Right_Between_Fingers_3_and_4-' + colour + '.svg')},
            },
            "Between fingers": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers-' + colour + '.svg')},
            },
            "Between Thumb and Finger 1": {
                self.both: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Thumb_and_Finger_1-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Left_Between_Thumb_and_Finger_1-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Thumb_and_Finger_1-' + colour + '.svg')},
            },
            "Biceps": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Biceps-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Bicep-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Bicep-' + colour + '.svg')},
            },
            "Buttocks": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Buttocks-' + colour + '.svg')}
            },
            "Cheek": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheeks-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Cheek-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Cheek-' + colour + '.svg')}
            },
            "Cheek/nose": {
                self.both: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheek_and_Nose-' + colour + '.svg'),
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Cheek_and_Nose_with_Divisions-' + colour + '.svg')
                }
            },
            "Cheekbone in front of ear": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheekbone_in_Front_of_Ear-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Left_Cheekbone_in_Front_of_Ear-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Right_Cheekbone_in_Front_of_Ear-' + colour + '.svg')}
            },
            "Cheekbone under eye": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheekbone_under_Eye-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Cheekbone_under_Eye-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Cheekbone_under_Eye-' + colour + '.svg')}
            },
            "Chest/breast area": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Chest-Breast_Area-' + colour + '.svg')}
            },
            "Chin": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Chin-' + colour + '.svg')}
            },
            # Corner of mouth doesn't exist in Location tree as a general option-- only in contra- & ipsi-specific forms
            "Corner of mouth": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Corners_of_Mouth-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Corner_of_Mouth-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Corner_of_Mouth-' + colour + '.svg')}
            },
            "Earlobe": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Earlobes-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Earlobe-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Earlobe-' + colour + '.svg')},
            },
            "Ear": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Ears_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Ears-' + colour + '.svg'),
                },
                self.left: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Ear_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Ear-' + colour + '.svg'),
                },
                self.right: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Ear_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Ear-' + colour + '.svg'),
                }
            },
            "Elbow": {
                self.both: {self.get_resource('predefined_locations/' + colour + '_HL/Elbows-' + colour + '.svg')},
                self.left: {self.get_resource('predefined_locations/' + colour + '_HL/Left_Elbow-' + colour + '.svg')},
                self.right: {self.get_resource('predefined_locations/' + colour + '_HL/Right_Elbow-' + colour + '.svg')}
            },
            "Eye region": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Eye_Region_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eye_Region-' + colour + '.svg'),
                },
            },
            "Eyebrow": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Eyebrows_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eyebrows-' + colour + '.svg'),
                },
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Eyebrow-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Eyebrow-' + colour + '.svg')}
            },
            "Eyelid": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eyelids-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Eyelids-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Eyelids-' + colour + '.svg')}
            },
            "Eye": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Eyes_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eyes-' + colour + '.svg'),
                },
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Eye-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Eye-' + colour + '.svg')}
            },
            "Face": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Face_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Face-' + colour + '.svg'),
                },
            },
            "Finger 1": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_1-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_1-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_1-' + colour + '.svg')},
            },
            "Finger 2": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_2-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_2-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_2-' + colour + '.svg')},
            },
            "Finger 3": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_3-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_3-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_3-' + colour + '.svg')},
            },
            "Finger 4": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_4-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_4-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_4-' + colour + '.svg')},
            },
            "Fingers and thumb": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Fingers_and_Thumbs-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Fingers_and_Thumb-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Fingers_and_Thumb-' + colour + '.svg')}
            },
            "Fingers": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Fingers-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Fingers-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Fingers-' + colour + '.svg')}
            },
            "Foot": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Feet-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Foot-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Foot-' + colour + '.svg')}
            },
            "Forearm": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Forearms-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Forearm-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Forearm-' + colour + '.svg')},
            },
            "Forehead region": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Forehead_Region_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Forehead_Region-' + colour + '.svg'),
                },
            },
            "Forehead": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Forehead-' + colour + '.svg')}
            },
            "Groin": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Groin-' + colour + '.svg')}
            },
            "Hand minus fingers": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Hands_minus_Fingers-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hand_minus_Fingers-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hand_minus_Fingers-' + colour + '.svg')}
            },
            "Whole hand": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Hands_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Hands-' + colour + '.svg'),
                },
                self.left: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hand-' + colour + '.svg'),
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hand_with_Divisions-' + colour + '.svg')
                },
                self.right: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hand-' + colour + '.svg'),
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hand_with_Divisions-' + colour + '.svg')
                }
            },
            "Head": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Head_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Head-' + colour + '.svg'),
                },
            },
            "Heel of hand": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Heels_of_Hands-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Heel_of_Hand-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Heel_of_Hand-' + colour + '.svg')},
            },
            "Hip": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Hips-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hip-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hip-' + colour + '.svg')}
            },
            "Jaw": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Jaws-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Jaw-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Jaw-' + colour + '.svg')}
            },
            "Knee": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Knees-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Knee-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Knee-' + colour + '.svg')}
            },
            "Legs and feet": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Legs_and_Feet_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Legs_and_Feet-' + colour + '.svg'),
                },
            },
            "Leg and foot": {
                self.left: {
                    self.div: self.get_resource(
                        'predefined_locations/' + colour + '_HL/Left_Leg_and_Foot_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Leg_and_Foot-' + colour + '.svg')
                },
                self.right: {
                    self.div: self.get_resource(
                        'predefined_locations/' + colour + '_HL/Right_Leg_and_Foot_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Leg_and_Foot-' + colour + '.svg')
                }
            },
            "Lips": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lips-' + colour + '.svg')},
            },
            "Lower eyelid": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Eyelids-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Lower_Eyelid-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Lower_Eyelid-' + colour + '.svg')}
            },
            "Lower leg": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Legs-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Lower_Leg-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Lower_Leg-' + colour + '.svg')}
            },
            "Lower lip": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Lip-' + colour + '.svg')},
            },
            "Lower torso": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Torso_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Torso-' + colour + '.svg'),
                },
            },
            "Mouth": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Mouth_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Mouth-' + colour + '.svg'),
                },
            },
            "Neck": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Neck-' + colour + '.svg'), },
            },
            "Nose": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Nose_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose-' + colour + '.svg'),
                },
            },
            "Nose root": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose_Root-' + colour + '.svg'), },
            },
            "Nose ridge": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose_Ridge-' + colour + '.svg'), },
            },
            "Nose tip": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose_Tip-' + colour + '.svg'), },
            },
            "Nostril": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nostrils-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Nostril-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Nostril-' + colour + '.svg')}
            },
            "Outer corner of eye": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Outer_Corners_of_Eyes-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Outer_Corner_of_Left_Eye-' + colour + '.svg')},
                self.right: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Outer_Corner_of_Right_Eye-' + colour + '.svg')},
            },
            "Overall": {
                self.both: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Overall_Highlight-' + colour + '.svg'),
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Overall_with_Divisions-' + colour + '.svg')
                },
            },
            "Pelvis area": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Pelvis_Area-' + colour + '.svg')}
            },
            "Septum": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Septum-' + colour + '.svg')},
            },
            "Septum/nostril area": {
                self.both: {
                    self.div: self.get_resource(
                        'predefined_locations/' + colour + '_HL/Septum-Nostril_Area_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Septum-Nostril_Area-' + colour + '.svg')
                },
            },
            "Shoulder": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Shoulders-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Shoulder-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Shoulder-' + colour + '.svg')}
            },
            "Side of face": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Sides_of_Face-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Side_of_Face-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Side_of_Face-' + colour + '.svg')}
            },
            "Sternum/clavicle area": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Sternum-Clavicle_Area-' + colour + '.svg')},
            },
            "Teeth": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Teeth-' + colour + '.svg')},
            },
            "Temple": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Temple-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Temple-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Temple-' + colour + '.svg')}
            },
            "Thumb": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Thumbs-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Thumb-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Thumb-' + colour + '.svg')}
            },
            "Top of head": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Top_of_Head-' + colour + '.svg')},
            },
            "Torso": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Torso_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Torso-' + colour + '.svg')
                },
            },
            "Under chin": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Underchin-' + colour + '.svg')},
            },
            "Upper arm above biceps": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Arms_above_Bicep-' + colour + '.svg')},
                self.left: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Arm_above_Bicep-' + colour + '.svg')},
                self.right: {
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Arm_above_Bicep-' + colour + '.svg')}
            },
            "Upper arm": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Arms_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Arms-' + colour + '.svg'),
                },
                self.left: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Arm_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Arm-' + colour + '.svg')
                },
                self.right: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Arm_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Arm-' + colour + '.svg')
                }
            },
            "Upper eyelid": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Eyelids-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Eyelid-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Eyelid-' + colour + '.svg')}
            },
            "Upper leg": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Legs-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Leg-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Leg-' + colour + '.svg')}
            },
            "Upper lip": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Lip-' + colour + '.svg')},
            },
            "Upper torso": {
                self.both: {
                    self.div: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Torso_with_Divisions-' + colour + '.svg'),
                    self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Torso-' + colour + '.svg')
                },
            },
            "Wrist": {
                self.both: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Wrists-' + colour + '.svg')},
                self.left: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Wrist-' + colour + '.svg')},
                self.right: {self.nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Wrist-' + colour + '.svg')}
            },
        }

    @cached_property
    def predefined_locations_description_byfilename(self):
        return {
            "Abdominal-Waist_Area": "Abdominal/waist area",
            "Above_Forehead-Hairline": "Above Forehead (hairline)",
            "Ankles": "Ankles",
            "Right_Ankle":  "Ankle - " + self.contraoripsi,
            "Left_Ankle": "Ankle - " + self.contraoripsi,
            "Armpits": "Armpits",
            "Right_Armpit": "Armpit - " + self.contraoripsi,
            "Left_Armpit": "Armpit - " + self.contraoripsi,
            "Arms": "Arms",
            "Right_Arm": "Arm - " + self.contraoripsi,
            "Left_Arm": "Arm - " + self.contraoripsi,
            "Below_Nose-Philtrum": "Below nose / philtrum",
            "Between_Eyebrows": "Between eyebrows",
            "Between_Fingers_1_and_2": "Between Fingers 1 and 2",
            "Right_Between_Fingers_1_and_2": "Between Fingers 1 and 2 - " + self.contraoripsi,
            "Left_Between_Fingers_1_and_2": "Between Fingers 1 and 2 - " + self.contraoripsi,
            "Between_Fingers_2_and_3": "Between Fingers 2 and 3",
            "Right_Between_Fingers_2_and_3": "Between Fingers 2 and 3 - " + self.contraoripsi,
            "Left_Between_Fingers_2_and_3": "Between Fingers 2 and 3 - " + self.contraoripsi,
            "Between_Fingers_3_and_4": "Between Fingers 3 and 4",
            "Right_Between_Fingers_3_and_4": "Between Fingers 3 and 4 - " + self.contraoripsi,
            "Left_Between_Fingers_3_and_4": "Between Fingers 3 and 4 - " + self.contraoripsi,
            "Between_Fingers": "Between fingers",
            "Right_Between_Fingers": "Between fingers - " + self.contraoripsi,
            "Left_Between_Fingers": "Between fingers - " + self.contraoripsi,
            "Between_Thumb_and_Finger_1": "Between Thumb and Finger 1",
            "Right_Between_Thumb_and_Finger_1": "Between Thumb and Finger 1 - " + self.contraoripsi,
            "Left_Between_Thumb_and_Finger_1": "Between Thumb and Finger 1 - " + self.contraoripsi,
            "Biceps": "Biceps",
            "Left_Bicep": "Biceps - " + self.contraoripsi,
            "Right_Bicep": "Biceps - " + self.contraoripsi,
            "Cheek_and_Nose": "Cheek/nose",
            "Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear",
            "Left_Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear - " + self.contraoripsi,
            "Right_Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear - " + self.contraoripsi,
            "Cheekbone_under_Eye": "Cheekbone under eye",
            "Right_Cheekbone_under_Eye": "Cheekbone under eye - " + self.contraoripsi,
            "Left_Cheekbone_under_Eye": "Cheekbone under eye - " + self.contraoripsi,
            "Cheeks": "Cheeks",
            "Left_Cheek": "Cheek - " + self.contraoripsi,
            "Right_Cheek": "Cheek - " + self.contraoripsi,
            "Chest-Breast_Area": "Chest/breast area",
            "Chin": "Chin",
            "Corners_of_Mouth": "Corner of mouth",
            "Left_Corner_of_Mouth": "Corner of mouth - " + self.contraoripsi,
            "Right_Corner_of_Mouth": "Corner of mouth - " + self.contraoripsi,
            "Earlobes": "Earlobes",
            "Right_Earlobe": "Earlobe - " + self.contraoripsi,
            "Left_Earlobe": "Earlobe - " + self.contraoripsi,
            "Ears": "Ears",
            "Right_Ear": "Ear - " + self.contraoripsi,
            "Left_Ear": "Ear - " + self.contraoripsi,
            "Elbows": "Elbows",
            "Right_Elbow": "Elbow - " + self.contraoripsi,
            "Left_Elbow": "Elbow - " + self.contraoripsi,
            "Eye_Region": "Eye region",
            "Eyebrows": "Eyebrows",
            "Right_Eyebrow": "Eyebrow - " + self.contraoripsi,
            "Left_Eyebrow": "Eyebrow - " + self.contraoripsi,
            "Eyelids": "Eyelids",
            "Right_Eyelids": "Eyelids - " + self.contraoripsi,
            "Left_Eyelids": "Eyelids - " + self.contraoripsi,
            "Eyes": "Eyes",
            "Right_Eye": "Eye - " + self.contraoripsi,
            "Left_Eye": "Eye - " + self.contraoripsi,
            "Face": "Face",
            "Feet": "Feet",
            "Right_Foot": "Foot - " + self.contraoripsi,
            "Left_Foot": "Foot - " + self.contraoripsi,
            "Forearms": "Forearms",
            "Right_Forearm": "Forearm - " + self.contraoripsi,
            "Left_Forearm": "Forearm - " + self.contraoripsi,
            "Finger_1": "Finger 1",
            "Right_Finger_1": "Finger 1 - " + self.contraoripsi,
            "Left_Finger_1": "Finger 1 - " + self.contraoripsi,
            "Finger_2": "Finger 2",
            "Right_Finger_2": "Finger 2 - " + self.contraoripsi,
            "Left_Finger_2": "Finger 2 - " + self.contraoripsi,
            "Finger_3": "Finger 3",
            "Right_Finger_3": "Finger 3 - " + self.contraoripsi,
            "Left_Finger_3": "Finger 3 - " + self.contraoripsi,
            "Finger_4": "Finger 4",
            "Right_Finger_4": "Finger 4 - " + self.contraoripsi,
            "Left_Finger_4": "Finger 4 - " + self.contraoripsi,
            "Fingers_and_Thumbs": "Fingers and thumbs",
            "Right_Fingers_and_Thumb": "Fingers and thumb - " + self.contraoripsi,
            "Left_Fingers_and_Thumb": "Fingers and thumb - " + self.contraoripsi,
            "Fingers": "Fingers",
            "Right_Fingers": "Fingers - " + self.contraoripsi,
            "Left_Fingers": "Fingers - " + self.contraoripsi,
            "Forearms": "Forearms",
            "Right_Forearm": "Forearm - " + self.contraoripsi,
            "Left_Forearm": "Forearm - " + self.contraoripsi,
            "Forehead_Region": "Forehead region",
            "Forehead": "Forehead",
            "Groin": "Groin",
            "Hands_minus_Fingers": "Hands minus fingers",
            "Right_Hand_minus_Fingers": "Hand minus Fingers - " + self.contraoripsi,
            "Left_Hand_minus_Fingers": "Hand minus Fingers - " + self.contraoripsi,
            "Hands": "Hands",
            "Right_Hand": "Hand - " + self.contraoripsi,
            "Left_Hand": "Hand - " + self.contraoripsi,
            "Heels_of_Hands": "Heels of hands",
            "Right_Heel_of_Hands": "Heel of hand - " + self.contraoripsi,
            "Left_Heel_of_Hands": "Heel of hand - " + self.contraoripsi,
            "Hips": "Hip",
            "Right_Hip": "Hip - " + self.contraoripsi,
            "Left_Hip": "Hip - " + self.contraoripsi,
            "Jaws": "Jaws",
            "Right_Jaw": "Jaw - " + self.contraoripsi,
            "Left_Jaw": "Jaw - " + self.contraoripsi,
            "Knees": "Knees",
            "Right_Knee": "Knee - " + self.contraoripsi,
            "Left_Knee": "Knee - " + self.contraoripsi,
            "Legs_and_Feet": "Legs and feet",
            "Right_Leg_and_Foot": "Leg and foot - " + self.contraoripsi,
            "Left_Leg_and_Foot": "Leg and foot - " + self.contraoripsi,
            "Lips": "Lips",
            "Lower_Eyelids": "Lower eyelids",
            "Right_Lower_Eyelid": "Lower eyelid - " + self.contraoripsi,
            "Left_Lower_Eyelid": "Lower eyelid - " + self.contraoripsi,
            "Mouth": "Mouth",
            "Outer_Corners_of_Eyes": "Outer corners of eyes",
            "Outer_Corner_of_Left_Eye": "Outer corner of eye - " + self.contraoripsi,
            "Outer_Corner_of_Right_Eye": "Outer corner of eye - " + self.contraoripsi,
            "Nostrils": "Nostrils",
            "Nose": "Nose",
            "Nose_Root": "Nose root",
            "Nose_Ridge": "Nose ridge",
            "Nose_Tip": "Nose tip",
            "Right_Nostril": "Nostril - " + self.contraoripsi,
            "Left_Nostril": "Nostril - " + self.contraoripsi,
            "Pelvis_Area": "Pelvis area",
            "Shoulders": "Shoulders",
            "Right_Shoulder": "Shoulder - " + self.contraoripsi,
            "Left_Shoulder": "Shoulder - " + self.contraoripsi,
            "Sides_of_Face": "Sides of face",
            "Right_Side_of_Face": "Side of face - " + self.contraoripsi,
            "Left_Side_of_Face": "Side of face - " + self.contraoripsi,
            "Temple": "Temple",
            "Right_Temple": "Temple - " + self.contraoripsi,
            "Left_Temple": "Temple - " + self.contraoripsi,
            "Thumbs": "Thumbs",
            "Right_Thumb": "Thumb - " + self.contraoripsi,
            "Left_Thumb": "Thumb - " + self.contraoripsi,
            "Upper_Arms_above_Bicep": "Upper arms above bicep",
            "Right_Upper_Arm_above_Bicep": "Upper arm above bicep - " + self.contraoripsi,
            "Left_Upper_Arm_above_Bicep": "Upper arm above bicep - " + self.contraoripsi,
            "Upper_Eyelids": "Upper eyelids",
            "Right_Upper_Eyelid": "Upper eyelids - " + self.contraoripsi,
            "Left_Upper_Eyelid": "Upper eyelids - " + self.contraoripsi,
            "Upper_Legs": "Upper legs",
            "Right_Upper_Leg": "Upper leg - " + self.contraoripsi,
            "Left_Upper_Leg": "Upper leg - " + self.contraoripsi,
            "Upper_Lip": "Upper lip",
            "Upper_Torso": "Upper torso",
            "Wrists": "Wrists",
            "Right_Wrist": "Wrist - " + self.contraoripsi,
            "Left_Wrist": "Wrist - " + self.contraoripsi,
            "Septum-Nostril_Area": "Septum/nostril area",
            "Septum": "Septum",
            "Sternum-Clavicle_Area": "Sternum/clavicle area",
            "Teeth": "Teeth",
            "Top_of_Head": "Top of head",
            "Torso": "Torso",
            "Underchin": "Under chin",
            "Upper_Arms": "Upper arms",
            "Right_Upper_Arm": "Upper arm - " + self.contraoripsi,
            "Left_Upper_Arm": "Upper arm - " + self.contraoripsi,
            "Upper_Torso": "Upper torso",
            # TODO KV check
        }

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
