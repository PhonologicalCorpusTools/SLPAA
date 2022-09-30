import importlib
import json
import sys
from os import path
meipass_path = sys._MEIPASS

# debugging

# end debugging

with open(path.join(meipass_path, 'runtime', 'base.json')) as f:
    settings = json.load(f)

module = importlib.import_module('fbs_runtime._frozen')
module.BUILD_SETTINGS = settings
module.BUILD_SETTINGS['environment'] = 'local'
module.BUILD_SETTINGS['meipass_path'] = meipass_path
