#define MyAppName        "File Renamer"
#define MyAppVersion     "0.0.1"
#define MyAppPublisher   "Your Name"
#define MyAppURL         "https://portfolio.chunzps.com"
#define MyAppExeName     "FileRenamer.exe"
#define MyIconFile       "assets\\app.ico"

[Setup]
AppId={{F1A2B3C4-D5E6-4789-ABCD-0123456789AB}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableDirPage=no
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=FileRenamerSetup_{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
WizardStyle=modern
SetupIconFile={#MyIconFile}
UninstallDisplayIcon={app}\{#MyAppExeName}
LicenseFile=LICENSE.txt

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional tasks:"; Flags: unchecked

[Files]
; your app
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
; ship the icon so shortcuts can point to it
Source: "{#MyIconFile}"; DestDir: "{app}"; DestName: "app.ico"; Flags: ignoreversion

[Icons]
; explicitly set the shortcut icon
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"
Name: "{autodesktop}\{#MyAppName}";  Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\app.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Launch {#MyAppName}"; Flags: nowait postinstall skipifsilent

[Code]
function IsWin64: Boolean;
begin
  Result := Is64BitInstallMode;
end;
