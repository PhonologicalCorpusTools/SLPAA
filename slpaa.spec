# -*- mode: python -*-
import os
import sys
import fbs
sys.setrecursionlimit(5000)

block_cipher = None
slpaa_path = os.getcwd()

# setting the path to an icon. ignored on Linux
icon_path = os.path.join(slpaa_path, 'src', 'main', 'icons', 'Icon.ico')
if sys.platform == 'darwin':
    icon_path = os.path.join(slpaa_path, 'src', 'main', 'icons', 'mac', 'icon.icns')

fbs_path = os.path.dirname(fbs.__file__)
src_path = os.path.join(slpaa_path, 'src', 'main', 'python')

added_files = [(os.path.join(slpaa_path, 'src', 'build','settings'), 'runtime'), # base.json to be referred to at runtime
               (os.path.join(slpaa_path, 'src', 'main', 'resources', 'base'), 'resources'), # resources
               (os.path.join(slpaa_path, 'src', 'main', 'icons', 'Icon.ico'), 'resources') # Icon.ico fbs_runtime needs this.
               ]

a = Analysis([os.path.join(src_path, 'main.py')],
             pathex=[slpaa_path],
             binaries=None,
             datas=added_files,
             hiddenimports=[],
             runtime_hooks=[os.path.join(slpaa_path, 'src', 'build', 'runtime_hook.py')],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='SLPAA',
          debug=False,    # True if debugging
          strip=False,
          upx=True,
          console=False,  # True if debugging
          icon=icon_path
          )

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='resources')

if sys.platform == 'darwin':
   app = BUNDLE(exe, name='SLPAA.app', icon=icon_path)