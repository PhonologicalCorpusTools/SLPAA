from fbs_runtime.application_context.PyQt5 import ApplicationContext, cached_property
from .main_window import MainWindow


class AppContext(ApplicationContext):
    def run(self):
        self.main_window.show()
        return self.app.exec_()

    @cached_property
    def main_window(self):
        return MainWindow(self)

    @cached_property
    def icons(self):
        return {
            'blank': self.get_resource('icons/blank.png'),
            'copy': self.get_resource('icons/copy.png'),
            'delete': self.get_resource('icons/delete.png'),
            'load': self.get_resource('icons/load.png'),
            'paste': self.get_resource('icons/paste.png'),
            'plus': self.get_resource('icons/plus.png'),
            'save': self.get_resource('icons/disk.png'),
            'new_sign': self.get_resource('icons/hand.png')
        }

    @cached_property
    def default_location_images(self):
        return {
            'head': self.get_resource('default_location_images/head.jpg'),
            'upper_body': self.get_resource('default_location_images/upper_body.jpg'),
            'weak_hand': self.get_resource('default_location_images/weak_hand.jpg')
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
