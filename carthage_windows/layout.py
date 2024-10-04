# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.


from carthage import *
from carthage.modeling import *
from carthage.ansible import *
from carthage.network import V4Config

from . import cd
from . import qemu
from . import config
from . import examples

class layout(CarthageLayout):

    no_prompt_install_image = cd.NoPromptInstallImage
    autounattend_cd = cd.AutoUnattendCd

    add_provider(config.windows_version_key, 'w11')
    #add_provider(config.WinRemotingPlugin)
    add_provider(config.AuthorizedKeysPlugin)
    add_provider(qemu.QemuDrivers)
    add_provider(examples.NvdaInstall)
    
