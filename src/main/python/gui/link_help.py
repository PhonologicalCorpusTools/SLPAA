# for 'help' button behaviour.
# separate file because it needs to be linked from different modules
from constant import FROZEN, VERSION
import webbrowser

help_map = {
    # help_map is a dictionary of moduletype (key) and its help page (value)
    'movement': 'movement_module',
    'location': 'location_module',
    'handconfig': 'hand_configuration_module',
    'relation': 'relation_module',
    'orientation': 'orientation_module',
    'nonmanual': 'nonmanual_module',
    'signlevel': 'sign_level_info',
    'signtype': 'sign_type',
    'xslot': 'timing'
}


def show_help(module_type:str) -> None:
    # activate when the user clicks 'help' btn. launch the web browser and open a relevant readthedocs page

    # generate the url to land
    base_url = 'https://slp-aa.readthedocs.io/en/'
    version = 'latest/' if not FROZEN else "v{}.{}.{}/".format(*VERSION)

    help_url = f'{base_url}{version}{help_map[module_type]}.html'
    webbrowser.open(help_url)
