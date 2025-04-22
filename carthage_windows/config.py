# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

import dataclasses
from pathlib import Path
from carthage import *
import carthage.ssh

__all__ = []

@dataclasses.dataclass
class WindowsConfig:

    #: w10, w11, 2k22
    windows_version: str
    
    #: the product key to select the windows image to install. This product key is not used for activation. This key is a generic key for Win 11 pro
    product_key:str = "VK7JG-NPHTM-C97JM-9MPGT-3V66T"

    #: enable sshd
    enable_sshd: bool = True
    #: Files to copy into c:\windows\setup
    oem_files:list = dataclasses.field(default_factory=lambda: [])

    #: Files to make available as drivers; nothing auto installs these but they are made available in the driver store and for example if their rank is high enough may be used to select a virtio disk.
    driver_files: list = dataclasses.field(default_factory=lambda:[])

#: The password for the admin local account.
    admin_password:str = 'admin'

    #: Disable device encryption
    disable_device_encryption: bool = True
    
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
@inject_autokwargs(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    )
class WinRemotingPlugin(WinConfigPlugin):

    name = 'windows_remoting'

    async def apply(self, wconfig):
        assets = self.carthage_windows.resource_dir/'assets'
        wconfig.oem_files.append(assets/'ConfigureRemotingForAnsible.ps1')
        wconfig.firstlogon_powershell.append('c:\\windows\\setup\\ConfigureRemotingForAnsible.ps1')

__all__ += ['WinRemotingPlugin']

@inject_autokwargs(
    authorized_keys=carthage.ssh.AuthorizedKeysFile)
class AuthorizedKeysPlugin(WinConfigPlugin):

    name = 'authorized_keys'

    async def apply(self, wconfig:WindowsConfig):
        wconfig.oem_files.append(self.authorized_keys.path)
        wconfig.specialize_powershell.extend([
            'New-Item -ItemType Directory -Force -Path c:\\ProgramData\\ssh',
            'copy c:\\windows\\setup\\authorized_keys c:\\ProgramData\\ssh\\administrators_authorized_keys',
            ])

__all__ += ['AuthorizedKeysPlugin']

@inject(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    injector=Injector)
def find_asset(glob, *, carthage_windows, injector):
    config = injector(ConfigLayout)
    if assets_dir := config.windows.assets_dir:
        assets = Path(assets_dir)/'windows'
    else:
        assets = carthage_windows.resource_dir/'assets'
    results = list(assets.glob(glob))
    if len(results) == 0:
        return None
    if len(results) == 1:
        return results[0]
    raise ValueError('too many results')

__all__ += ['find_asset']

def install_msi(wconfig, msi_path):
    wconfig.oem_files.append(msi_path)
    wconfig.firstlogon_powershell.append(f'Write-Output "Installing {msi_path.name}"')
    wconfig.firstlogon_powershell.append(f'msiexec /i c:\\windows\\setup\\{msi_path.name} /qn /norestart /L*+ c:\\windows\\setup\\{msi_path.name}.log |Out-Default')

__all__ += ['install_msi']
    
