# -*- mode: python -*-

block_cipher = None


a = Analysis(['/Users/YuHsiangLo/Documents/SLP-AA_new/SLP-AA/src/main/python/main.py'],
             pathex=['/Users/YuHsiangLo/Documents/SLP-AA_new/SLP-AA/target/PyInstaller'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=['/Users/YuHsiangLo/Documents/pyqt5_tutorial/fbsenv/lib/python3.7/site-packages/fbs/freeze/hooks'],
             runtime_hooks=['/Users/YuHsiangLo/Documents/SLP-AA_new/SLP-AA/target/PyInstaller/fbs_pyinstaller_hook.py'],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Sign Language Phonetic Annotator and Analyzer',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False , icon='/Users/YuHsiangLo/Documents/SLP-AA_new/SLP-AA/target/Icon.icns')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               name='Sign Language Phonetic Annotator and Analyzer')
app = BUNDLE(coll,
             name='Sign Language Phonetic Annotator and Analyzer.app',
             icon='/Users/YuHsiangLo/Documents/SLP-AA_new/SLP-AA/target/Icon.icns',
             bundle_identifier='com.rogerlo.templateapplication')
