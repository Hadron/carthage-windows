# Copyright (C) 2024, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

import shutil
from carthage import *
from carthage.modeling import *
from carthage import files
from carthage import sh
from carthage.plugins import CarthagePlugin

__all__ = []

@inject_autokwargs(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    )
class NoPromptInstallImage(ModelTasks):

    def find_base_cd(self):
        images = self.carthage_windows.resource_dir.glob('assets/*.iso')
        images_list = list(images)
        assert len(images_list) == 1
        return images_list[0]

    @memoproperty
    def base_name(self):
        '''The windows install image without .iso extension
        '''
        return self.find_base_cd().stem

    @memoproperty
    def image_name(self):
        '''
        Retur a path to the final resulting image.
        '''
        return self.stamp_path.joinpath(        self.base_name+'_noprompt.iso')

    @setup_task("Repack without Prompt")
    async def repack_noprompt_image(self):
# See https://palant.info/2023/02/13/automating-windows-installation-in-a-vm/ for the mkisofs options
        extract_dir = self.stamp_path/'extract'
        image = self.find_base_cd()
        iso_builder = files.CdContext(
            self.stamp_path,
            (self.image_name).name,
            '-iso-level', '4',
            '-disable-deep-relocation',
            '-untranslated-filenames',
            '-b', 'boot/etfsboot.com',
            '-no-emul-boot',
            '-boot-load-size', '8',
            '-eltorito-alt-boot',
                        '-eltorito-platform', 'efi',
            '-b', 'efi/microsoft/boot/efisys_noprompt.bin',
            # And include the original image contents
            extract_dir,
            )
        extract_dir.mkdir(parents=True, exist_ok=True)
        await sh.mount(
            '-oloop',
            '-oro',
            str(image),
            extract_dir)
        try:
            breakpoint()
            async with iso_builder as extra_dir:
                # Add anything we want to overlay into the image into extra_dir
                pass
        finally:
            await sh.umount(extract_dir)

    @repack_noprompt_image.check_completed()
    def repack_noprompt_image(self):
        image = self.find_base_cd()
        output = self.image_name
        image_stat = image.stat()
        if not output.exists(): return False
        output_stat = output.stat()
        if output_stat.st_mtime > image_stat.st_mtime:
            return output_stat.st_mtime
        return False

__all__ += ['NoPromptInstallImage']
        

@inject_autokwargs(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    )
class AutoUnattendCd(ModelTasks):

    @setup_task("Create autounattend CD")
    async def create_autounattend_cd(self):
        assets = self.carthage_windows.resource_dir/'assets'
        iso_builder = files.CdContext(self.stamp_path,
                                      'autounattend.iso',
                                      )
        async with iso_builder as contents_path:
            shutil.copy2(assets/'autounattend.xml',
                         contents_path)

__all__ += ['AutounattendCd']
