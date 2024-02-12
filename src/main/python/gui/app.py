import errno
import sys
from os import getcwd
from os.path import join, exists, realpath, dirname
from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from .main_window import MainWindow

right = "R"
left = "L"
both = "both/all"
div = "with divisions"
nodiv = "no divisions"
contraoripsi = "contra/ipsi"


class AppContext(ApplicationContext):
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
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Abdominal-Waist_Area-' + colour + '.svg')}
            },
            "Above forehead (hairline)": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Above_Forehead-Hairline-' + colour + '.svg')}
            },
            "Ankle": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Ankles-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Ankle-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Ankle-' + colour + '.svg')},
            },
            "Armpit": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Armpits-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Armpit-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Armpit-' + colour + '.svg')},
            },
            # TODO KV fix
            "Ankles": self.get_resource('predefined_locations/' + colour + '_HL/Ankles-' + colour + '.svg'),
            "Armpits": self.get_resource('predefined_locations/' + colour + '_HL/Armpits-' + colour + '.svg'),
            "Arms": self.get_resource('predefined_locations/' + colour + '_HL/Arms-' + colour + '.svg'),
            "Chin": self.get_resource('predefined_locations/' + colour + '_HL/Chin-' + colour + '.svg'),
            "Arm": {
                left: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Arm_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Arm-' + colour + '.svg'),
                },
                right: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Arm_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Arm-' + colour + '.svg'),
                },
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Arms_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Arms-' + colour + '.svg'),
                }
            },
            "Back of head": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Back_of_Head-' + colour + '.svg')}
            },
            "Behind ear": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Behind_Ears-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Behind_Ear-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Behind_Ear-' + colour + '.svg')},
            },
            "Below nose / philtrum": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Below_Nose-Philtrum-' + colour + '.svg')}
            },
            "Between eyebrows": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Eyebrows-' + colour + '.svg')}
            },
            "Between Fingers 1 and 2": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers_1_and_2-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_1_and_2-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_1_and_2-' + colour + '.svg')},
            },
            "Between Fingers 2 and 3": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers_2_and_3-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_2_and_3-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers_2_and_3-' + colour + '.svg')},
            },
            "Between Fingers 3 and 4": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers_3_and_4-' + colour + '.svg')},
                left: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers_3_and_4-' + colour + '.svg')},
                right: {nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Right_Between_Fingers_3_and_4-' + colour + '.svg')},
            },
            "Between fingers": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Fingers-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Between_Fingers-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Fingers-' + colour + '.svg')},
            },
            "Between Thumb and Finger 1": {
                both: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Between_Thumb_and_Finger_1-' + colour + '.svg')},
                left: {nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Left_Between_Thumb_and_Finger_1-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Between_Thumb_and_Finger_1-' + colour + '.svg')},
            },
            "Biceps": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Biceps-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Bicep-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Bicep-' + colour + '.svg')},
            },
            "Buttocks": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Buttocks-' + colour + '.svg')}
            },
            "Cheek": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheeks-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Cheek-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Cheek-' + colour + '.svg')}
            },
            "Cheek/nose": {
                both: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheek_and_Nose-' + colour + '.svg'),
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Cheek_and_Nose_with_Divisions-' + colour + '.svg')
                }
            },
            "Cheekbone in front of ear": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheekbone_in_Front_of_Ear-' + colour + '.svg')},
                left: {nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Left_Cheekbone_in_Front_of_Ear-' + colour + '.svg')},
                right: {nodiv: self.get_resource(
                    'predefined_locations/' + colour + '_HL/Right_Cheekbone_in_Front_of_Ear-' + colour + '.svg')}
            },
            "Cheekbone under eye": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Cheekbone_under_Eye-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Cheekbone_under_Eye-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Cheekbone_under_Eye-' + colour + '.svg')}
            },
            "Chest/breast area": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Chest-Breast_Area-' + colour + '.svg')}
            },
            # "Chin": {
            #     both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Chin-' + colour + '.svg')}
            # },
            # Corner of mouth doesn't exist in Location tree as a general option-- only in contra- & ipsi-specific forms
            "Corner of mouth": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Corners_of_Mouth-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Corner_of_Mouth-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Corner_of_Mouth-' + colour + '.svg')}
            },
            "Earlobe": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Earlobes-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Earlobe-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Earlobe-' + colour + '.svg')},
            },
            "Ear": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Ears_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Ears-' + colour + '.svg'),
                },
                left: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Ear_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Ear-' + colour + '.svg'),
                },
                right: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Ear_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Ear-' + colour + '.svg'),
                }
            },
            "Elbow": {
                both: {self.get_resource('predefined_locations/' + colour + '_HL/Elbows-' + colour + '.svg')},
                left: {self.get_resource('predefined_locations/' + colour + '_HL/Left_Elbow-' + colour + '.svg')},
                right: {self.get_resource('predefined_locations/' + colour + '_HL/Right_Elbow-' + colour + '.svg')}
            },
            "Eye region": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Eye_Region_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eye_Region-' + colour + '.svg'),
                },
            },
            "Eyebrow": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Eyebrows_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eyebrows-' + colour + '.svg'),
                },
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Eyebrow-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Eyebrow-' + colour + '.svg')}
            },
            "Eyelid": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eyelids-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Eyelids-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Eyelids-' + colour + '.svg')}
            },
            "Eye": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Eyes_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Eyes-' + colour + '.svg'),
                },
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Eye-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Eye-' + colour + '.svg')}
            },
            "Face": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Face_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Face-' + colour + '.svg'),
                },
            },
            "Finger 1": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_1-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_1-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_1-' + colour + '.svg')},
            },
            "Finger 2": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_2-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_2-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_2-' + colour + '.svg')},
            },
            "Finger 3": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_3-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_3-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_3-' + colour + '.svg')},
            },
            "Finger 4": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Finger_4-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Finger_4-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Finger_4-' + colour + '.svg')},
            },
            "Fingers and thumb": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Fingers_and_Thumbs-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Fingers_and_Thumb-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Fingers_and_Thumb-' + colour + '.svg')}
            },
            "Fingers": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Fingers-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Fingers-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Fingers-' + colour + '.svg')}
            },
            "Foot": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Feet-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Foot-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Foot-' + colour + '.svg')}
            },
            "Forearm": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Forearms-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Forearm-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Forearm-' + colour + '.svg')},
            },
            "Forehead region": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Forehead_Region_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Forehead_Region-' + colour + '.svg'),
                },
            },
            "Forehead": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Forehead-' + colour + '.svg')}
            },
            "Groin": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Groin-' + colour + '.svg')}
            },
            "Hand minus fingers": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Hands_minus_Fingers-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hand_minus_Fingers-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hand_minus_Fingers-' + colour + '.svg')}
            },
            "Whole hand": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Hands_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Hands-' + colour + '.svg'),
                },
                left: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hand-' + colour + '.svg'),
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hand_with_Divisions-' + colour + '.svg')
                },
                right: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hand-' + colour + '.svg'),
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hand_with_Divisions-' + colour + '.svg')
                }
            },
            "Head": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Head_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Head-' + colour + '.svg'),
                },
            },
            "Heel of hand": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Heels_of_Hands-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Heel_of_Hand-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Heel_of_Hand-' + colour + '.svg')},
            },
            "Hip": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Hips-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Hip-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Hip-' + colour + '.svg')}
            },
            "Jaw": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Jaws-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Jaw-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Jaw-' + colour + '.svg')}
            },
            "Knee": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Knees-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Knee-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Knee-' + colour + '.svg')}
            },
            "Legs and feet": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Legs_and_Feet_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Legs_and_Feet-' + colour + '.svg'),
                },
                left: {
                    div: self.get_resource(
                        'predefined_locations/' + colour + '_HL/Left_Leg_and_Foot_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Leg_and_Foot-' + colour + '.svg')
                },
                right: {
                    div: self.get_resource(
                        'predefined_locations/' + colour + '_HL/Right_Leg_and_Foot_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Leg_and_Foot-' + colour + '.svg')
                }
            },
            "Lips": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lips-' + colour + '.svg')},
            },
            "Lower eyelid": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Eyelids-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Lower_Eyelid-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Lower_Eyelid-' + colour + '.svg')}
            },
            "Lower leg": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Legs-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Lower_Leg-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Lower_Leg-' + colour + '.svg')}
            },
            "Lower lip": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Lip-' + colour + '.svg')},
            },
            "Lower torso": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Torso_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Lower_Torso-' + colour + '.svg'),
                },
            },
            "Mouth": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Mouth_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Mouth-' + colour + '.svg'),
                },
            },
            "Neck": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Neck-' + colour + '.svg'), },
            },
            "Nose": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Nose_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose-' + colour + '.svg'),
                },
            },
            "Nose root": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose_Root-' + colour + '.svg'), },
            },
            "Nose ridge": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose_Ridge-' + colour + '.svg'), },
            },
            "Nose tip": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nose_Tip-' + colour + '.svg'), },
            },
            "Nostril": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Nostrils-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Nostril-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Nostril-' + colour + '.svg')}
            },
            "Outer corner of eye": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Outer_Corners_of_Eyes-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Outer_Corner_of_Left_Eye-' + colour + '.svg')},
                right: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Outer_Corner_of_Right_Eye-' + colour + '.svg')},
            },
            "Overall": {
                both: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Overall_Highlight-' + colour + '.svg'),
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Overall_with_Divisions-' + colour + '.svg')
                },
            },
            "Pelvis area": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Pelvis_Area-' + colour + '.svg')}
            },
            "Septum": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Septum-' + colour + '.svg')},
            },
            "Septum/nostril area": {
                both: {
                    div: self.get_resource(
                        'predefined_locations/' + colour + '_HL/Septum-Nostril_Area_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Septum-Nostril_Area-' + colour + '.svg')
                },
            },
            "Shoulder": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Shoulders-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Shoulder-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Shoulder-' + colour + '.svg')}
            },
            "Side of face": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Sides_of_Face-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Side_of_Face-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Side_of_Face-' + colour + '.svg')}
            },
            "Sternum/clavicle area": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Sternum-Clavicle_Area-' + colour + '.svg')},
            },
            "Teeth": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Teeth-' + colour + '.svg')},
            },
            "Temple": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Temple-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Temple-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Temple-' + colour + '.svg')}
            },
            "Thumb": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Thumbs-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Thumb-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Thumb-' + colour + '.svg')}
            },
            "Top of head": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Top_of_Head-' + colour + '.svg')},
            },
            "Torso": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Torso_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Torso-' + colour + '.svg')
                },
            },
            "Under chin": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Underchin-' + colour + '.svg')},
            },
            "Upper arm above biceps": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Arms_above_Bicep-' + colour + '.svg')},
                left: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Arm_above_Bicep-' + colour + '.svg')},
                right: {
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Arm_above_Bicep-' + colour + '.svg')}
            },
            "Upper arm": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Arms_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Arms-' + colour + '.svg'),
                },
                left: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Arm_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Arm-' + colour + '.svg')
                },
                right: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Arm_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Arm-' + colour + '.svg')
                }
            },
            "Upper eyelid": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Eyelids-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Eyelid-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Eyelid-' + colour + '.svg')}
            },
            "Upper leg": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Legs-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Upper_Leg-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Upper_Leg-' + colour + '.svg')}
            },
            "Upper lip": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Lip-' + colour + '.svg')},
            },
            "Upper torso": {
                both: {
                    div: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Torso_with_Divisions-' + colour + '.svg'),
                    nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Upper_Torso-' + colour + '.svg')
                },
            },
            "Wrist": {
                both: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Wrists-' + colour + '.svg')},
                left: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Left_Wrist-' + colour + '.svg')},
                right: {nodiv: self.get_resource('predefined_locations/' + colour + '_HL/Right_Wrist-' + colour + '.svg')}
            },
        }

    @cached_property
    def predefined_locations_description_byfilename(self):
        return {
            "Abdominal-Waist_Area": "Abdominal/waist area",
            "Above_Forehead-Hairline": "Above Forehead (hairline)",
            "Ankles": "Ankles",
            "Right_Ankle":  "Ankle - " + contraoripsi,
            "Left_Ankle": "Ankle - " + contraoripsi,
            "Armpits": "Armpits",
            "Right_Armpit": "Armpit - " + contraoripsi,
            "Left_Armpit": "Armpit - " + contraoripsi,
            "Arms": "Arms",
            "Right_Arm": "Arm - " + contraoripsi,
            "Left_Arm": "Arm - " + contraoripsi,
            "Below_Nose-Philtrum": "Below nose / philtrum",
            "Between_Eyebrows": "Between eyebrows",
            "Between_Fingers_1_and_2": "Between Fingers 1 and 2",
            "Right_Between_Fingers_1_and_2": "Between Fingers 1 and 2 - " + contraoripsi,
            "Left_Between_Fingers_1_and_2": "Between Fingers 1 and 2 - " + contraoripsi,
            "Between_Fingers_2_and_3": "Between Fingers 2 and 3",
            "Right_Between_Fingers_2_and_3": "Between Fingers 2 and 3 - " + contraoripsi,
            "Left_Between_Fingers_2_and_3": "Between Fingers 2 and 3 - " + contraoripsi,
            "Between_Fingers_3_and_4": "Between Fingers 3 and 4",
            "Right_Between_Fingers_3_and_4": "Between Fingers 3 and 4 - " + contraoripsi,
            "Left_Between_Fingers_3_and_4": "Between Fingers 3 and 4 - " + contraoripsi,
            "Between_Fingers": "Between fingers",
            "Right_Between_Fingers": "Between fingers - " + contraoripsi,
            "Left_Between_Fingers": "Between fingers - " + contraoripsi,
            "Between_Thumb_and_Finger_1": "Between Thumb and Finger 1",
            "Right_Between_Thumb_and_Finger_1": "Between Thumb and Finger 1 - " + contraoripsi,
            "Left_Between_Thumb_and_Finger_1": "Between Thumb and Finger 1 - " + contraoripsi,
            "Biceps": "Biceps",
            "Left_Bicep": "Biceps - " + contraoripsi,
            "Right_Bicep": "Biceps - " + contraoripsi,
            "Cheek_and_Nose": "Cheek/nose",
            "Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear",
            "Left_Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear - " + contraoripsi,
            "Right_Cheekbone_in_Front_of_Ear": "Cheekbone in front of ear - " + contraoripsi,
            "Cheekbone_under_Eye": "Cheekbone under eye",
            "Right_Cheekbone_under_Eye": "Cheekbone under eye - " + contraoripsi,
            "Left_Cheekbone_under_Eye": "Cheekbone under eye - " + contraoripsi,
            "Cheeks": "Cheeks",
            "Left_Cheek": "Cheek - " + contraoripsi,
            "Right_Cheek": "Cheek - " + contraoripsi,
            "Chest-Breast_Area": "Chest/breast area",
            "Chin": "Chin",
            # TODO KV continue
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
