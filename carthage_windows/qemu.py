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

__all__ = []

def driver_version_str(windows_version):
    if windows_version == 'w11':
        return 'w11'
    raise NotImplementedError

@inject_autokwargs(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    )
class QemuDrivers(ModelTasks, WinConfigPlugin):

    name = 'qemu_windows_config'
    
    def find_base_cd(self):
        images = self.carthage_windows.resource_dir.glob('assets/virtio-*.iso')
        images_list = list(images)
        assert len(images_list) == 1
        return images_list[0]

    #: Things to grab from cd
    drivers = (
        'vioscsi',
        'qxl',
        'qxldod',
        'NetKVM',
    )
    oem_msis = (
        'virtio-win-gt-x64.msi',
    )
    
    @setup_task("Pull out virtio drivers")
    async def grab_virtio_drivers(self):
        image = self.find_base_cd()
        iso_out = self.stamp_path/'extract'
        async with extract_cd(image, iso_out):
            drivers = self.stamp_path/'drivers'
            try:
                shutil.rmtree(drivers)
            except FileNotFoundError: pass
            drivers.mkdir()
            for d in self.drivers:
                await carthage.sh.rsync('-a',
                                  iso_out/d, drivers)
            oem = self.stamp_path/'oem'
            try:
                shutil.rmtree(oem)
            except FileNotFoundError: pass
            oem.mkdir()
            for f in self.oem_msis:
                await carthage.sh.rsync('-a', iso_out/f, str(oem))

    async def apply(self, wconfig):
        oem = self.stamp_path/'oem'
        drivers = self.stamp_path/'drivers'
        for o in self.oem_msis:
            wconfig.oem_files.append(oem/o)
            wconfig.specialize_powershell.add(f'msiexec /i c:\\windows\\setup\{o} /nq /norestart')
        v = driver_version_str(wconfig.windows_version)
        for d in self.drivers:
            if list(drivers.glob(f'{d}/{v}/amd64')):
                wconfig.driver_files.append(f'{drivers}/{d}/{v}/amd64/')

__all__ += ['QemuDrivers']
