; RP Text Studio user-scope installer. Build with Inno Setup 6 ISCC.exe.
#ifndef AppVersion
  #define AppVersion "0.2.0"
#endif
#define AppName "RP Text Studio"
#define AppExe "RPTextStudio.exe"

[Setup]
AppId={{6BF877BA-7792-41B3-BB0B-B19CAB845B7D}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher=RP Text Studio
DefaultDirName={localappdata}\Programs\RPTextStudio
DefaultGroupName=RP Text Studio
OutputDir=installer-dist
OutputBaseFilename=RPTextStudio-Setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName=RP Text Studio
WizardStyle=modern
DisableProgramGroupPage=yes
ChangesAssociations=no
CloseApplications=yes
RestartApplications=no

[Files]
Source: "dist\{#AppExe}"; DestDir: "{app}"; Flags: ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Desktopverknüpfung erstellen"; GroupDescription: "Zusätzliche Verknüpfungen:"; Flags: unchecked

[Icons]
Name: "{group}\RP Text Studio"; Filename: "{app}\{#AppExe}"; WorkingDir: "{app}"
Name: "{autodesktop}\RP Text Studio"; Filename: "{app}\{#AppExe}"; Tasks: desktopicon; WorkingDir: "{app}"

[Run]
Filename: "{app}\{#AppExe}"; Description: "RP Text Studio starten"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
; Intentionally empty: no user data, registry, saved WoW paths or projects removed.
