# Copyright (C) 2024, 2025, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

from carthage import inject, Injector
import carthage.config
from . import layout
from .cd import *
from .config import *
from .qemu import *

class WindowsSchema(carthage.config.ConfigSchema, prefix='windows'):
    # Where the base windows CD is
    assets_dir: carthage.config.ConfigPath
    #: Where we place large output artificats like the modified windows CD
    image_dir:carthage.config.ConfigPath = '{cache_dir}/windows'

@inject(injector=Injector)
def carthage_plugin(injector):
    injector.add_provider(layout.layout)
