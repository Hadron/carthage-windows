# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

import carthage.pytest_plugin
import pytest
from pathlib import Path
from carthage import *
from carthage.modeling import *
from carthage_windows import *
import carthage_windows.layout
from carthage.pytest import *

pytest_plugins = ('carthage.pytest_plugin', )

@pytest.fixture()
def ainjector(ainjector):
    base_injector(
        carthage.plugins.load_plugin, 'carthage_windows')
    return ainjector

class layout(carthage_windows.layout.layout):

    @provides("windows_net")
    class net(NetworkModel):
        bridge_name = 'blaptop'
        v4_config = V4Config(dhcp=True)

    class net_config(NetworkConfigModel):
        add('eth0', mac=persistent_random_mac, net=injector_access('windows_net'))

    @provides(carthage.vm.vm_image_key)
    class image(LibvirtWindowsBaseImage):
        pass

    class vm_1(MachineModel):
        add_provider(machine_implementation_key, dependency_quote(carthage.vm.Vm))
        ssh_login_user = 'admin'
        


@async_test
async def test_image_build(ainjector):
    l = await ainjector(layout)
    ainjector = l.ainjector
    await l.image.delete()
    #wait_for_shutdown gives 30 minutes, but we want extra time so we can actually clean up.
    with TestTiming(32*60):
        await l.image.async_become_ready()
    
@async_test
async def test_use_image(ainjector):
    l = await ainjector(layout)
    ainjector = l.ainjector
    with TestTiming(32*60):
        await l.image.async_become_ready()
    with TestTiming(10*60):
        vm =l.vm_1.machine
        try:
            async with vm.machine_running():
                await vm.ssh('powershell ls')
        finally:
            await vm.delete()
            
