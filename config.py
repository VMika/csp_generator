import os
import platform
from pathlib import Path

# Defining base dir and db file
ROOT_DIR = Path(os.path.dirname(__file__))
DB_FILE = str(ROOT_DIR/'db'/'csp.db')

# Getting platform to point to suited binaries
operating_system = platform.system()

# Setting right driver
if operating_system == 'Linux':
    PROXY = str(ROOT_DIR/'scripts'/'browsermob-proxy-2.1.4-bin'/'browsermob-proxy-2.1.4'/'bin'/'browsermob-proxy')
    GECKO_DRIVER = str(ROOT_DIR/'scripts'/'geckodriver_unix')
    # Setting execution permission
    os.chmod(PROXY, 0o744)
    os.chmod(GECKO_DRIVER, 0o744)

elif operating_system == 'Windows':
    PROXY = str(ROOT_DIR/'scripts'/'browsermob-proxy-2.1.4-bin'/'browsermob-proxy-2.1.4'/'bin'/'browsermob-proxy.bat')
    GECKO_DRIVER = str(ROOT_DIR/'scripts'/'geckodriver_windows')

