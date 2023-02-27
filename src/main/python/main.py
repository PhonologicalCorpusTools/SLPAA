import sys
# import subprocess
from gui.app import AppContext

if __name__ == '__main__':
    # TODO KV - I thought I could sneak in a check & install for dependencies in the script itself,
    #  but *all* imports are checked before the code even starts to run. So this appears to be useless.
    # try:
    #     subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', '../../../requirements.txt'])
    #     print("Successfully checked and installed package dependencies using pip.")
    # except Exception as pip_exc:
    #     try:
    #         subprocess.check_call([sys.executable, '-m', 'pip3', 'install', '-r', '../../../requirements.txt'])
    #         print("Successfully checked and installed package dependencies using pip3.")
    #     except Exception as pip3_exc:
    #         print("Failed to check and install package dependencies with both pip and pip3.")
    #         print(pip_exc.args)
    #         print(pip3_exc.args)

    appctxt = AppContext()
    exit_code = appctxt.run()
    sys.exit(exit_code)
