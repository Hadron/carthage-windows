# Copyright (C) 2024, 2025, Hadron Industries.
# Carthage is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License version 3
# as published by the Free Software Foundation. It is distributed
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the file
# LICENSE for details.

import contextlib
import shutil
from pathlib import Path
import carthage
from carthage import *
from carthage.modeling import *
from carthage import files
from carthage import sh
from carthage.plugins import CarthagePlugin
from .config import *

__all__ = []

@contextlib.asynccontextmanager
async def extract_cd(iso_file:str, out_dir:Path) -> Path:
    '''
    Returns a path of the directory containing the contents of the CD.
    Perhaps by extracting; perhaps by mounting.
    Will be deleted/unmounted when the context exits
    :param out_dir: an output directory that will be created if it does not exist and will be claned on context exit.
    '''
    out_dir.mkdir(parents=True, exist_ok=True)
    if sevenzip := getattr(carthage.sh, '7z', None):
        try:
            await sevenzip('x', '-o'+str(out_dir), '--', iso_file)
            yield Path(out_dir)
        finally:
            shutil.rmtree(out_dir)
    else:
        await carthage.sh.mount(
            '-oloop',
            iso_file, out_dir)
        try:
            yield out_dir
        finally:
            await carthage.sh.umount(out_dir)
            
@inject_autokwargs(
    carthage_windows=InjectionKey(CarthagePlugin, name='carthage-windows'),
    )
class NoPromptInstallImage(SetupTaskMixin):

    stamp_subdir = 'carthage_windows/no_prompt_install'

    def find_base_cd(self):
        if assets_dir := self.config_layout.windows.assets_dir:
            assets_path = Path(assets_dir)/'windows'
        else:
            assets_path = self.carthage_windows.resource_dir/'assets'
        images = assets_path.glob('Win11*.iso')
        images_list = list(images)
        assert len(images_list) == 1, f'Expecting only one image in {assets_path}'
        return images_list[0]

    @memoproperty
    def output_path(self):
        res = Path(self.config_layout.windows.image_dir)
        res.mkdir(parents=True, exist_ok=True)
        return res
    
    @memoproperty
    def base_name(self):
        '''The windows install image without .iso extension
        '''
        return self.find_base_cd().stem

    @memoproperty
    def image_name(self):
        '''
        Return a path to the final resulting image.
        '''
        return self.output_path.joinpath(        self.base_name+'_noprompt.iso')

    def qemu_config(self, disk_config):
        return dict(
            path=self.image_name,
            source_type='file',
            driver='raw',
            qemu_source='file'
        )

    @setup_task("Repack without Prompt")
    async def repack_noprompt_image(self):
# See https://palant.info/2023/02/13/automating-windows-installation-in-a-vm/ for the mkisofs options
        extract_dir = self.state_path/'extract'
        image = self.find_base_cd()
        iso_builder = files.CdContext(
            self.output_path,
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
        async with extract_cd(str(image), extract_dir):
            async with iso_builder as extra_dir:
                # Add anything we want to overlay into the image into extra_dir
                pass

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
    windows_version=windows_version_key,
    )
class AutoUnattendCd(SetupTaskMixin):

    stamp_subdir = 'carthage_windows/autounattend_cd'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.injector.add_provider(InjectionKey(WindowsConfig), self.build_config)
        
    async def build_config(self)-> WindowsConfig:
        config = WindowsConfig(self.windows_version)
        for _, plugin in await self.ainjector.filter_instantiate_async(
                WinConfigPlugin,
                ['name']):
            await plugin.apply(config)
        return config
    autounattend_xml = mako_task('autounattend.xml.mako', wconfig=InjectionKey(WindowsConfig), sysprep=False)
    sysprep_xml = mako_task('autounattend.xml.mako', sysprep=True, wconfig=InjectionKey(WindowsConfig), output='sysprep_unattend.xml')
    

    @setup_task("Create autounattend CD")
    async def create_autounattend_cd(self):
        assets = self.carthage_windows.resource_dir/'assets'
        iso_builder = files.CdContext(self.stamp_path,
                                      'autounattend.iso',
                                      )
        async with iso_builder as contents_path:
            wconfig = await self.ainjector.get_instance_async(WindowsConfig)
            if not wconfig.generalize:
                run_service ='-Status Running'
            else:
                run_service = ''
            if wconfig.enable_sshd:
                wconfig.firstlogon_powershell.extend([
                    'Add-WindowsCapability -online -name OpenSSH.Server~~~~0.0.1.0',
                    f'Set-Service sshd -StartupType automatic {run_service}',
                    'get-NetFirewallRule -name *openssh* |set-NetFirewallRule -profile public,private,domain',
                    ])
            if wconfig.disable_device_encryption:
                wconfig.specialize_powershell.extend([
                    'New-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\BitLocker" -Name "PreventDeviceEncryption" -Value 1 -PropertyType DWord',
                    'New-ItemProperty -Path "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\BitLocker" -Name "DisableBDE" -Value 1 -PropertyType DWord'])

            wconfig.oem_files.append(self.stamp_path/'sysprep_unattend.xml')
            if wconfig.generalize:
                wconfig.firstlogon_powershell.append(
                    'c:\\windows\\system32\\sysprep\\sysprep /generalize /oobe /shutdown /unattend:c:\\windows\\setup\\sysprep_unattend.xml')
            oem_setup = contents_path/'$OEM$/$$/Setup'
            oem_setup.mkdir(parents=True)
            for oem_file in wconfig.oem_files:
                await sh.rsync('-a', oem_file, str(oem_setup))
            driver_dir = contents_path/'$WinPEDriver$'
            driver_dir.mkdir()
            for driver_file in wconfig.driver_files:
                await sh.rsync('-a', driver_file, driver_dir)
            with oem_setup.joinpath('specialize.ps1').open('wt') as specialize:
                for scriptlet in wconfig.specialize_powershell:
                    specialize.write(scriptlet+'\n')
                specialize.write('\n')
            with oem_setup.joinpath('firstlogon.ps1').open('wt') as firstlogon:
                for scriptlet in wconfig.firstlogon_powershell:
                    firstlogon.write(scriptlet+'\n')
                firstlogon.write('\n')
                    
            shutil.copy2(self.stamp_path/'autounattend.xml',
                         contents_path)

    def qemu_config(self, disk_config):
        return dict(
            path=self.stamp_path/'autounattend.iso',
            source_type='file',
            driver='raw',
            qemu_source='file'
        )

__all__ += ['AutoUnattendCd']

class LibvirtWindowsBaseImage(LibvirtImageModel):
    self_provider(InjectionKey(carthage.image.ImageVolume))
    name = 'windows_base'
    size = 128*1024
    memory_mb = 16*1024
    cpus = 4
    console_needed = True
    disk_config = [
        dict(
            volume=InjectionKey(carthage.image.ImageVolume, _ready=False),),
        dict(
            volume=InjectionKey(NoPromptInstallImage),
            target_type='cdrom',
            bus='sata',
            ),
        dict(
            volume=InjectionKey(AutoUnattendCd),
            target_type='cdrom',
            bus='sata',
            )]

    class WaitForInstall(carthage.machine.BaseCustomization):

        description = "Wait for install to complete"

        @setup_task("Wait")
        async def wait_for_install(self):
            await self.host.wait_for_shutdown()

__all__ += ['LibvirtWindowsBaseImage']
