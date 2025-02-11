# for 'help' button behaviour.
# separate file because it needs to be linked from different modules
import subprocess  # for inquiring github commit hash
import webbrowser  # for launching web browser that opens readthedocs documentations
import sys
from os import getcwd, path
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon  # for version number message box icon

from constant import FROZEN, VERSION, ModuleTypes

help_map = {
    # help_map is a dictionary of functionality (key) and the corresponding help page (value)
    ModuleTypes.MOVEMENT: 'movement_module',
    ModuleTypes.LOCATION: 'location_module',
    ModuleTypes.HANDCONFIG: 'hand_configuration_module',   # coming from the 'Help' btn in the hand configuration dialog
    'predefined_handshapes': 'predefined_handshapes',  # coming from the btn below 'load predefined handshape' inside hc
    ModuleTypes.RELATION: 'relation_module',
    ModuleTypes.ORIENTATION: 'orientation_module',
    ModuleTypes.NONMANUAL: 'nonmanual_module',
    'signlevel': 'sign_level_info',
    ModuleTypes.SIGNTYPE: 'sign_type',
    'xslot': 'timing',  # for sign timing and xslots
    'preferences': 'global_settings',  # coming from preferences dialog
}


# Open the relevant readthedocs page on a web browser. Called when clicking a 'help' btn.
def show_help(functionality: str) -> None:
    # special case: help > about is the exception. instead of readthedocs, show github repo
    if functionality == 'about':
        webbrowser.open('https://github.com/PhonologicalCorpusTools/SLPAA?tab=readme-ov-file#readme')
        return

    # in other cases, open readthedocs
    base_url = 'https://slp-aa.readthedocs.io/en/'
    # version = 'latest/' if not FROZEN else "v{}.{}.{}/".format(*VERSION)
    # make sure to uncomment the above (and delete the below) if (i) releasing and (ii) readthedocs is done
    version = 'latest/'  # temporarily disable directing to a frozen version help page

    if functionality not in help_map:
        # do not have an individual readthedocs page. land on the main page
        webbrowser.open(f'{base_url}{version}')
        return

    # compose the url to land
    help_url = f'{base_url}{version}{help_map[functionality]}.html'
    webbrowser.open(help_url)


def show_version() -> None:
    # it prompts a message box showing the version number. a git commit hash may show instead of version number

    # first, compose the message that will go into the msgbox.
    msg = "You are running SLPAA "
    if FROZEN:
        # if frozen, show the version number specified in constants.py
        msg += "version {}.{}.{}".format(*VERSION)
    else:
        # if running from the source code, try to use git commit number
        msg += "from the source code."
        try:
            # Get the latest git commit number
            git_version = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).strip().decode('utf-8')
            msg += f'\nGit hash: {git_version}'
        except Exception as e:
            pass

    # now summon the slpaa icon
    if FROZEN:
        resource_dir = path.join(sys._MEIPASS, 'resources')  # cf. 'datas' parameter in .spec
    else:  # running from source
        parent_dir = path.dirname(getcwd())
        resource_dir = path.join(parent_dir, 'resources', 'base')
    slpaa_icon = QIcon(path.join(resource_dir, 'icons', 'slpaa.png'))

    # finally, create a message box with the msg and icon
    msg_box = QMessageBox()
    msg_box.setWindowIcon(slpaa_icon)
    msg_box.setIconPixmap(slpaa_icon.pixmap(32, 32))
    msg_box.setWindowTitle('SLPAA version')
    msg_box.setText(msg)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()
