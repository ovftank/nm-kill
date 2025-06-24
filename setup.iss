[Setup]
AppName=NM KILL
AppVersion=1.0.0
AppPublisher=ovftank
AppPublisherURL=https://github.com/ovftank/nm-kill
AppSupportURL=https://github.com/ovftank/nm-kill/issues
AppUpdatesURL=https://github.com/ovftank/nm-kill/releases
DefaultDirName={autopf}\NM KILL
DefaultGroupName=NM KILL
AllowNoIcons=yes
LicenseFile=
OutputDir=installer
OutputBaseFilename=nm-kill-setup
SetupIconFile=static\favicon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkablealone
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 10.0

[Files]
Source: "nm-kill.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "static\*"; DestDir: "{app}\static"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\NM KILL"; Filename: "{app}\nm-kill.exe"
Name: "{group}\{cm:UninstallProgram,NM KILL}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\NM KILL"; Filename: "{app}\nm-kill.exe"; Tasks: desktopicon
Name: "{commonprograms}\Quick Launch\NM KILL"; Filename: "{app}\nm-kill.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\nm-kill.exe"; Description: "{cm:LaunchProgram,NM KILL}"; Flags: nowait postinstall skipifsilent
