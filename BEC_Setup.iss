[Setup]
AppName=BEC Computational System
AppVersion=1.0
AppPublisher=Bumhang Engineering
AppPublisherURL=https://example.com
AppSupportURL=https://example.com
AppUpdatesURL=https://example.com
DefaultDirName={pf}\BEC Computational System
DefaultGroupName=BEC Computational System
AllowNoIcons=yes
OutputDir=C:\Users\USER\sourcecodes\python-codes\dist\installer
OutputBaseFilename=BEC_Setup
SetupIconFile=C:\Users\USER\sourcecodes\python-codes\dist\BEC Computational System.exe
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\USER\sourcecodes\python-codes\dist\BEC Computational System.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "C:\Users\USER\sourcecodes\python-codes\Data\*"; DestDir: "{app}\Data"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\BEC Computational System"; Filename: "{app}\BEC Computational System.exe"
Name: "{group}\{cm:UninstallProgram,BEC Computational System}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\BEC Computational System"; Filename: "{app}\BEC Computational System.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\BEC Computational System"; Filename: "{app}\BEC Computational System.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\BEC Computational System.exe"; Description: "{cm:LaunchProgram,BEC Computational System}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: dirifempty; Name: "{app}\Data"
Type: dirifempty; Name: "{app}"
