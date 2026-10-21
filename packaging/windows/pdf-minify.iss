; PDF Minify installer for Windows x64 (Inno Setup 6).
; Built by .github/workflows/build-windows.yml:
;   ISCC /DAppVersion=x.y.z /DSourceDir=<built app folder> /O<output folder> pdf-minify.iss
; Installs for the current user by default, like Task Coach; settings and
; temporary files are never in the install folder, so uninstalling keeps them.

#ifndef AppVersion
  #error Pass /DAppVersion=x.y.z
#endif
#ifndef SourceDir
  #error Pass /DSourceDir=<built app folder>
#endif

#define AppName "PDF Minify"
#define AppPublisher "Real Carbonneau"
#define AppURL "https://github.com/realcarbonneau/pdf-minify"

[Setup]
AppId={{FC94418A-588A-43FB-9958-D58756B79BF5}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}/issues
AppUpdatesURL={#AppURL}/releases
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
DisableProgramGroupPage=yes
OutputBaseFilename=pdf-minify_{#AppVersion}_windows-x64-setup
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
SetupIconFile=pdf-minify.ico
UninstallDisplayIcon={app}\pdf-minify.ico
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0
LicenseFile=..\..\LICENSE
ChangesAssociations=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceDir}\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\pdf-minify.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\pdf-minify.ico"
Name: "{group}\{cm:UninstallProgram,{#AppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\pdf-minify.pyw"""; WorkingDir: "{app}"; IconFilename: "{app}\pdf-minify.ico"; Tasks: desktopicon

[Run]
Filename: "{app}\python\pythonw.exe"; Parameters: """{app}\pdf-minify.pyw"""; WorkingDir: "{app}"; Description: "{cm:LaunchProgram,{#AppName}}"; Flags: nowait postinstall skipifsilent

[Registry]
; "Open with > PDF Minify" for PDFs, without taking over the default PDF viewer.
Root: HKA; Subkey: "Software\Classes\PDFMinify.pdf"; ValueType: string; ValueName: ""; ValueData: "PDF Document"; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\PDFMinify.pdf\DefaultIcon"; ValueType: string; ValueName: ""; ValueData: "{app}\pdf-minify.ico,0"
Root: HKA; Subkey: "Software\Classes\PDFMinify.pdf\shell\open\command"; ValueType: string; ValueName: ""; ValueData: """{app}\python\pythonw.exe"" ""{app}\pdf-minify.pyw"" ""%1"""
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; ValueType: string; ValueName: "PDFMinify.pdf"; ValueData: ""; Flags: uninsdeletevalue
