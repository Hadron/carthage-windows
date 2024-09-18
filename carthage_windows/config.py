# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

import dataclasses
from carthage import *

__all__ = []

@dataclasses.dataclass
class WindowsConfig:

    #: w10, w11, 2k22
    windows_version: str
    
    #: the product key to select the windows image to install. This product key is not used for activation. This key is a generic key for Win 11 pro
    product_key:str = "VK7JG-NPHTM-C97JM-9MPGT-3V66T"

    #: Files to copy into c:\windows\setup
    oem_files:list = dataclasses.field(default_factory=lambda: [])

    #: Files to make available as drivers; nothing auto installs these but they are made available in the driver store and for example if their rank is high enough may be used to select a virtio disk.
    driver_files: list = dataclasses.field(default_factory=lambda:[])

#: The password for the admin local account.
    admin_password:str = 'admin'

    #: Each list entry is a set of powershell code that will be run in the specialize pass. These items are concatenated into a single powershell script that is run in that pass.
    specialize_powershell: list = dataclasses.field(default_factory=lambda: [])

    #: These Powershell scripts are run in the firstlogoncommands pass in ObbeSystem. Again, concatenated as for specialize.
    firstlogon_powershell: list = dataclasses.field(default_factory=lambda: [])

    #: Generalize the image (sysprep) after specialization pass
    generalize:bool = True

__all__ += ['WindowsConfig']

class WinConfigPlugin(AsyncInjectable):

    '''
    All the WinConfig plugins in a given injector context are run by the image generation machinery; they can modify the :class:`WindowsConfig` adding  files or powershell snipits.
    '''

    name:str

    @classmethod
    def default_class_injection_key(cls):
        return InjectionKey(WinConfigPlugin, name=cls.name)

    async def apply(self, config:WindowsConfig):
        '''
        Abstract method to modify the config.
        '''
        pass

__all__ += ['WinConfigPlugin']

#: A string representing the Windows version
windows_version_key = InjectionKey('carthage-windows/windows_version')

__all__ += ['windows_version_key']