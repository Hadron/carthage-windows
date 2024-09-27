# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

import shutil
from carthage import *
import carthage.sh
from carthage.modeling import *
from .cd import extract_cd
from .config import *

'''
Some example plugins that are useful to Carthage developers to demonstrate usage.
'''

__all__ = []

@inject_autokwargs(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    )
class NvdaInstall( WinConfigPlugin):

    
    '''
    No, this does not install your Nvidia video drivers.  It installs the nvda screen reader from nvaccess.org.
    '''

    name = 'nvda_screenreader_install'
    @property
    def nvda_path(self):
        assets = self.carthage_windows.resource_dir/'assets'
        nvda_exe = list(assets.glob('nvda_*.exe'))
        if not nvda_exe: return None
        if len(nvda_exe) > 1:
            raise ValueError('Multiple nvda executables')
        return nvda_exe[0]
    
    async def apply(self, wconfig):
        if not self.nvda_path:
            return
        wconfig.oem_files.append(self.nvda_path)
        nvda_name = self.nvda_path.name
        wconfig.firstlogon_powershell.append(f'c:\\windows\\setup\\{nvda_name} --install-silent --enable-start-on-logon=true')

__all__ += ['NvdaInstall']
