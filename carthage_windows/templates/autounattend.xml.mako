<?xml version="1.0" encoding="utf-8"?>
<unattend xmlns="urn:schemas-microsoft-com:unattend" xmlns:wcm="http://schemas.microsoft.com/WMIConfig/2002/State">
  <!--https://schneegans.de/windows/unattend-generator/?LanguageMode=Unattended&UILanguage=en-US&Locale=en-US&Keyboard=00000409&GeoLocation=244&ProcessorArchitecture=amd64&BypassRequirementsCheck=true&ComputerNameMode=Custom&ComputerName=windows-base&TimeZoneMode=Implicit&PartitionMode=Unattended&PartitionLayout=GPT&EspSize=300&RecoveryMode=Partition&RecoverySize=1000&WindowsEditionMode=Unattended&WindowsEdition=pro&UserAccountMode=Unattended&AccountName0=Admin&AccountPassword0=blueteam1&AccountGroup0=Administrators&AccountName1=&AccountName2=&AccountName3=&AccountName4=&AutoLogonMode=Own&PasswordExpirationMode=Unlimited&LockoutMode=Default&HideFiles=Hidden&DisableWidgets=true&ClassicContextMenu=true&DisableAppSuggestions=true&VirtIoGuestTools=true&WifiMode=Interactive&ExpressSettings=DisableAll&KeysMode=Skip&WdacMode=Skip-->
  <!-- This configuration has been manually modified since it was auto-generated. to update from the auto generator it is probably best to use those initial settings and diff. -->
	<settings pass="offlineServicing"></settings>
        %if not sysprep:
	<settings pass="windowsPE">
		<component name="Microsoft-Windows-International-Core-WinPE" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
			<SetupUILanguage>
				<UILanguage>en-US</UILanguage>
			</SetupUILanguage>
			<InputLocale>0409:00000409</InputLocale>
			<SystemLocale>en-US</SystemLocale>
			<UILanguage>en-US</UILanguage>
			<UserLocale>en-US</UserLocale>
		</component>
		<component name="Microsoft-Windows-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                  <DiskConfiguration>
                    <Disk wcm:action="add">
                      <DiskID>0</DiskID> 
                      <WillWipeDisk>true</WillWipeDisk> 
                      <CreatePartitions>
                        <!-- System partition (ESP) -->
                        <CreatePartition wcm:action="add">
                          <Order>1</Order> 
                          <Type>EFI</Type> 
                          <Size>400</Size> 
                        </CreatePartition>
                        <!-- Microsoft reserved partition (MSR) -->
                        <CreatePartition wcm:action="add">
                          <Order>2</Order> 
                          <Type>MSR</Type> 
                          <Size>128</Size> 
                        </CreatePartition>
                        <!-- Windows partition; installer automatically creates recovery partition -->
                        <CreatePartition wcm:action="add">
                          <Order>3</Order> 
                          <Type>Primary</Type> 
                          <Extend>true</Extend> 
                        </CreatePartition>
                      </CreatePartitions>

                      <ModifyPartitions>
                        <!-- System partition (ESP) -->
                        <ModifyPartition wcm:action="add">
                          <Order>1</Order> 
                          <PartitionID>1</PartitionID> 
                          <Label>System</Label> 
                          <Format>FAT32</Format> 
                        </ModifyPartition>
                        <!-- Windows partition -->
                        <ModifyPartition wcm:action="add">
                          <Order>2</Order> 
                          <PartitionID>3</PartitionID> 
                          <Label>Windows</Label> 
                          <Letter>C</Letter> 
                          <Format>NTFS</Format> 
                        </ModifyPartition>
                      </ModifyPartitions>
                    </Disk>
                    <WillShowUI>OnError</WillShowUI> 
                  </DiskConfiguration>

			<ImageInstall>
				<OSImage>
					<InstallTo>
						<DiskID>0</DiskID>
						<PartitionID>3</PartitionID>
					</InstallTo>
				</OSImage>
			</ImageInstall>
			<UserData>
				<ProductKey>
					<Key>${wconfig.product_key}</Key>
				</ProductKey>
				<AcceptEula>true</AcceptEula>
			</UserData>
                        <UseConfigurationSet>true</UseConfigurationSet>
			<RunSynchronous>
				<RunSynchronousCommand wcm:action="add">
					<Order>1</Order>
					<Path>reg.exe add "HKLM\SYSTEM\Setup\LabConfig" /v BypassTPMCheck /t REG_DWORD /d 1 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>2</Order>
					<Path>reg.exe add "HKLM\SYSTEM\Setup\LabConfig" /v BypassSecureBootCheck /t REG_DWORD /d 1 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>3</Order>
					<Path>reg.exe add "HKLM\SYSTEM\Setup\LabConfig" /v BypassRAMCheck /t REG_DWORD /d 1 /f</Path>
				</RunSynchronousCommand>
			</RunSynchronous>
		</component>
	</settings>
%endif
	<settings pass="generalize"></settings>
        %if not sysprep:
	<settings pass="specialize">
          <component name="microsoft-windows-securestartup-filterdriver-" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
            <PreventDeviceEncryption>true</PreventDeviceEncryption>
          </component>


<component name="Microsoft-Windows-Deployment" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
			<RunSynchronous>
				<RunSynchronousCommand wcm:action="add">
					<Order>1</Order>
					<Path>net.exe accounts /maxpwage:UNLIMITED</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>2</Order>
					<Path>reg.exe add "HKLM\SOFTWARE\Policies\Microsoft\Dsh" /v AllowNewsAndInterests /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>3</Order>
					<Path>reg.exe load "HKU\DefaultUser" "C:\Users\Default\NTUSER.DAT"</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>4</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "ContentDeliveryAllowed" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>5</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "FeatureManagementEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>6</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "OEMPreInstalledAppsEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>7</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "PreInstalledAppsEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>8</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "PreInstalledAppsEverEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>9</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SilentInstalledAppsEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>10</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SoftLandingEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>11</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContentEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>12</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-310093Enabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>13</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-338387Enabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>14</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-338388Enabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>15</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-338389Enabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>16</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-338393Enabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>17</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SubscribedContent-353698Enabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>18</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v "SystemPaneSuggestionsEnabled" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>19</Order>
					<Path>reg.exe unload "HKU\DefaultUser"</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>20</Order>
					<Path>reg.exe add "HKLM\Software\Policies\Microsoft\Windows\CloudContent" /v "DisableWindowsConsumerFeatures" /t REG_DWORD /d 0 /f</Path>
				</RunSynchronousCommand>
      <RunSynchronousCommand wcm:action="add">
        <Order>21</Order>
        <Path>powershell.exe -noprofile -ExecutionPolicy unrestricted C:\Windows\Setup\specialize.ps1 &gt;c:\windows\setup\specialize.log *&gt;&amp;1</Path>
      </RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>23</Order>
					<Path>reg.exe load "HKU\DefaultUser" "C:\Users\Default\NTUSER.DAT"</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>24</Order>
					<Path>reg.exe add "HKU\DefaultUser\Software\Microsoft\Windows\CurrentVersion\RunOnce" /v "ClassicContextMenu" /t REG_SZ /d "reg.exe add \"HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}\InprocServer32\" /ve /f" /f</Path>
				</RunSynchronousCommand>
				<RunSynchronousCommand wcm:action="add">
					<Order>25</Order>
					<Path>reg.exe unload "HKU\DefaultUser"</Path>
				</RunSynchronousCommand>
			</RunSynchronous>
		</component>
		<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
			<ComputerName>windows-base</ComputerName>
		</component>
	</settings>
        %endif
	<settings pass="auditSystem"></settings>
	<settings pass="auditUser"></settings>
	<settings pass="oobeSystem">
		<component name="Microsoft-Windows-International-Core" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
			<InputLocale>0409:00000409</InputLocale>
			<SystemLocale>en-US</SystemLocale>
			<UILanguage>en-US</UILanguage>
			<UserLocale>en-US</UserLocale>
		</component>
		<component name="Microsoft-Windows-Shell-Setup" processorArchitecture="amd64" publicKeyToken="31bf3856ad364e35" language="neutral" versionScope="nonSxS">
                  %if (not sysprep) or wconfig.admin_password:
		  <UserAccounts>
				<LocalAccounts>
					<LocalAccount wcm:action="add">
						<Name>Admin</Name>
						<Group>Administrators</Group>
						<Password>
							<Value>${wconfig.admin_password or 'admin'}</Value>
							<PlainText>true</PlainText>
						</Password>
					</LocalAccount>
				</LocalAccounts>
			</UserAccounts>
                        %endif
                        %if not sysprep:
			<AutoLogon>
				<Username>Admin</Username>
				<Enabled>true</Enabled>
				<LogonCount>1</LogonCount>
				<Password>
					<Value>${wconfig.admin_password or 'admin'}</Value>
					<PlainText>true</PlainText>
				</Password>
			</AutoLogon>
                        %endif
			<OOBE>
				<ProtectYourPC>3</ProtectYourPC>
				<HideEULAPage>true</HideEULAPage>
				<HideWirelessSetupInOOBE>false</HideWirelessSetupInOOBE>
			</OOBE>
                        %if not sysprep:
			<FirstLogonCommands>
				<SynchronousCommand wcm:action="add">
					<Order>1</Order>
					<CommandLine>reg.exe add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon" /v AutoLogonCount /t REG_DWORD /d 0 /f</CommandLine>
				</SynchronousCommand>
				<SynchronousCommand wcm:action="add">
					<Order>2</Order>
					<CommandLine>powershell.exe -NoProfile -ExecutionPolicy Unrestricted c:\windows\setup\firstlogon.ps1 &gt;c:\windows\setup\firstlogon.log *&gt;&amp;1</CommandLine>
				</SynchronousCommand>
			</FirstLogonCommands>
                        %endif
		</component>
	</settings>
</unattend>
